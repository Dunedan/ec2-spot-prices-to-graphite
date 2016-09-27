# Overview

This script fetches the EC2 spot prices via the AWS EC2 DescribeSpotPriceHistory
API and forwards them to a Graphite pickle-compatible endpoint.

The motivation was that the insight into EC2 spot prices AWS offers is quite
limited and really slow if you look at longer periods of time. As we have
Graphite already in use it felt just natural to have the spot prices in there as
well.

# Usage

* Clone this repository and enter the directory you cloned it into.

* Install the script using pip: ```pip install .```

* Call the script with `--help` to get all options:
```
foo@bar:~$ ec2_spot_prices_to_graphite.py --help
usage: ec2_spot_prices_to_graphite.py [-h]
                                      [--aws-access-key-id AWS_ACCESS_KEY_ID]
                                      [--aws-secret-access-key AWS_SECRET_ACCESS_KEY]
                                      [--profile PROFILE_NAME]
                                      [--region REGION_NAME]
                                      [--interval INTERVAL]
                                      [--products PRODUCT_DESCRIPTIONS]
                                      [--log-level LOG_LEVEL]
                                      [--graphite-host GRAPHITE_HOST]
                                      [--graphite-port GRAPHITE_PORT]
                                      [--graphite-prefix GRAPHITE_PREFIX]

Script to pull the EC2 spot price history out of AWS and push it into
Graphite.

optional arguments:
  -h, --help            show this help message and exit
  --aws-access-key-id AWS_ACCESS_KEY_ID
                        Specify a value here if you want to use a different
                        AWS_ACCESS_KEY_ID than configured in the AWS CLI.
  --aws-secret-access-key AWS_SECRET_ACCESS_KEY
                        Specify a value here if you want to use a different
                        AWS_SECRET_ACCESS_KEY than configured in the AWS CLI.
  --profile PROFILE_NAME
                        The AWS CLI profile to use. Defaults to the default
                        profile.
  --region REGION_NAME  The AWS region to connect to. Defaults to the one
                        configured for the AWS CLI.
  --interval INTERVAL   The interval in minutes back from now to gather prices
                        for. Defaults to 1 minute.
  --products PRODUCT_DESCRIPTIONS
                        A comma separated list of products to fetch. Defauls
                        to "Linux/UNIX (Amazon VPC), Windows (Amazon VPC)"
  --log-level LOG_LEVEL
                        The log level to log messages with. Defaults to ERROR.
  --graphite-host GRAPHITE_HOST
                        The graphite host to send the metrics to. Defaults to
                        localhost.
  --graphite-port GRAPHITE_PORT
                        The graphite port to send the metrics to. Defaults to
                        2004.
  --graphite-prefix GRAPHITE_PREFIX
                        A prefix to prepend to the metric name. Defaultsto
                        "aws.ec2.spot-price".
```

# Contribution

Pull Requests are welcome!