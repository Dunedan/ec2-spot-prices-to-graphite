#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Daniel Roschka <daniel@smaato.com>
Copyright: Smaato Inc. 2016

Script to fetch EC2 spot price history via the AWS API and to push it into
Graphite.

Attention: The DescribeSpotPriceHistory API call seems to behave funny and
always returns a multiple of 1000 of results. As there are even for 1 minute
more than 1000 values, some instance type combinations will be skipped.
Therefore it's best to limit the query somehow, e.g. by only fetching certain
product descriptions.

# TODO:
- Exponential Backoff (AWS API call + Graphite)
- Kompatibilität für Lambda
"""

import argparse
import logging
import pickle
import re
import socket
import struct
import time
from datetime import datetime, timedelta

from boto3.session import Session


def sanatize_string(string, keep_dots=False):
    """Replace characters in the given string.

    Characters which shouldn't appear in the Graphite metric name get replaced.
    """
    if keep_dots:
        pattern1 = re.compile(r'\s')
    else:
        pattern1 = re.compile(r'[\s\.]')
    pattern2 = re.compile(r'[\/]')
    pattern3 = re.compile(r'[^a-zA-Z_\-0-9\.]')
    string = string.lower()
    string = re.sub(pattern1, r'_', string)
    string = re.sub(pattern2, r'-', string)
    string = re.sub(pattern3, r'', string)
    return string


def get_spot_prices(ec2, interval, graphite_prefix, product_descriptions):
    """Get spot prices for the last x minutes.

    Gets the spot prices for the last x minutes, defined by the interval and
    returns a list of pickle-compatible tuples.
    """
    now = datetime.utcnow()
    response = ec2.describe_spot_price_history(
        StartTime=now - timedelta(minutes=interval),
        EndTime=now,
        ProductDescriptions=product_descriptions
    )

    items = response['SpotPriceHistory']
    while 'NextToken' in response and response['NextToken']:
        response = ec2.describe_spot_price_history(
            StartTime=now - timedelta(minutes=interval),
            EndTime=now,
            ProductDescriptions=product_descriptions,
            NextToken=response['NextToken']
        )
        items += response['SpotPriceHistory']

    metrics = []
    for item in items:
        path = ''
        if graphite_prefix:
            path = '%s.' % sanatize_string(graphite_prefix, keep_dots=True)
        path += '%s.%s.%s' % (
            sanatize_string(item['AvailabilityZone']),
            sanatize_string(item['InstanceType']),
            sanatize_string(item['ProductDescription'])
        )
        timestamp = int(time.mktime(item['Timestamp'].timetuple()))
        value = float(item['SpotPrice'])
        logging.debug('%s %s %s', path, timestamp, value)
        metrics.append((path, (timestamp, value)))
    return metrics


def send_to_graphite(metrics, host, port):
    payload = pickle.dumps(metrics, protocol=2)
    header = struct.pack("!L", len(payload))
    message = header + payload

    sock = socket.socket()
    try:
        sock.connect((host, port))
    except socket.error:
        raise SystemExit("Couldn't connect to %s on port %d. "
                         "Is carbon-cache.py running?" % (host, port))

    sock.sendall(message)
    sock.close()
    logging.debug("Metrics sent successfully to Graphite.")


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                        level='ERROR')
    parser = argparse.ArgumentParser(description='Script to pull the EC2 spot price history '
                                                 'out of AWS and push it into Graphite.')
    parser.add_argument('--aws-access-key-id', dest='aws_access_key_id',
                        help='Specify a value here if you want to use a different ' +
                        'AWS_ACCESS_KEY_ID than configured in the AWS CLI.')
    parser.add_argument('--aws-secret-access-key', dest='aws_secret_access_key',
                        help='Specify a value here if you want to use a different ' +
                        'AWS_SECRET_ACCESS_KEY than configured in the AWS CLI.')
    parser.add_argument('--profile', dest='profile_name',
                        help='The AWS CLI profile to use. Defaults to the default profile.')
    parser.add_argument('--region', dest='region_name', default='us-east-1',
                        help='The AWS region to connect to. Defaults to the one configured for ' +
                        'the AWS CLI.')
    parser.add_argument('--interval', dest='interval', default=1, required=False, type=int,
                        help='The interval in minutes back from now to gather prices for. Defaults to 1 minute.')
    parser.add_argument('--products', dest='product_descriptions',
                        default='Linux/UNIX (Amazon VPC), Windows (Amazon VPC)', required=False,
                        help='A comma separated list of products to fetch. Defauls to ' +
                             '"Linux/UNIX (Amazon VPC), Windows (Amazon VPC)"')
    parser.add_argument('--log-level', dest='log_level', default='ERROR', required=False,
                        help='The log level to log messages with. Defaults to ERROR.')
    parser.add_argument('--graphite-host', dest='graphite_host', default='localhost', required=False,
                        help='The graphite host to send the metrics to. Defaults to localhost.')
    parser.add_argument('--graphite-port', dest='graphite_port', default=2004, required=False, type=int,
                        help='The graphite port to send the metrics to. Defaults to 2004.')
    parser.add_argument('--graphite-prefix', dest='graphite_prefix', default='aws.ec2.spot-price', required=False,
                        help='A prefix to prepend to the metric name. Defaults to "aws.ec2.spot-price".')
    args = parser.parse_args()

    logging.getLogger().setLevel(args.log_level)

    session_args = {key: value for key, value in vars(args).items()
                    if key in ['aws_access_key_id',
                               'aws_secret_access_key',
                               'profile_name',
                               'region_name']}
    session = Session(**session_args)

    ec2 = session.client('ec2')

    product_descriptions = [product.strip() for product in args.product_descriptions.split(',')]
    metrics = get_spot_prices(ec2, args.interval, args.graphite_prefix, product_descriptions)
    send_to_graphite(metrics, args.graphite_host, args.graphite_port)


if __name__ == '__main__':
    main()
