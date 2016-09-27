from setuptools import setup

setup(name='ec2-spot-prices-to-graphite',
    version='0.1',
    description='Fetch EC2 spot price history via the AWS API and to push it into Graphite.',
    url='http://github.com/smaato/ec2-spot-prices-to-graphite',
    author='Daniel Roschka',
    author_email='daniel@smaato.com',
    license='MIT',
    scripts=['ec2_spot_prices_to_graphite.py'],
    zip_safe=False,
    install_requires=['boto3', 'pytz'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
)
