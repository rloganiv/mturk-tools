"""
The MTurk client.

Defines `client` to be used as a singleton in other scripts.
"""
import boto3

from mtools.config import config


client = boto3.client(
    'mturk',
    region_name=config['mturk']['region_name'],
    endpoint_url=config['mturk']['endpoint_url']
)
