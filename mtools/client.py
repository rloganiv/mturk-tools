"""
The MTurk client.

Defines `client` to be used as a singleton in other scripts.
"""
import logging

import boto3

from mtools.config import config


logger = logging.getLogger(__name__)


client = boto3.client(
    'mturk',
    region_name=config['mturk'].pop('region_name', None),
    endpoint_url=config['mturk'].pop('endpoint_url', None),
    aws_access_key_id=config['mturk'].pop('aws_access_key_id', None),
    aws_secret_access_key=config['mturk'].pop('secret_access_key', None)
)

logger.info('Client at endpoint: %s', client._endpoint)
