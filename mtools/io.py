"""
Utilities and commands for ingesting data into mtools.
"""
import hashlib
import json
import logging

import click
from sqlalchemy.sql import exists

from mtools.db import session_scope
from mtools.db import Dataset, HitType, Instance, Qualification
from mtools.cli import cli
from mtools.client import client


logger = logging.getLogger(__name__)


def compute_checksum(filename):
    hash_ = hashlib.md5()
    with open(filename, 'rb') as f:
        hash_.update(f.read())
    digest = hash_.hexdigest()
    return digest


def create_instance(obj, eval_type):
    sentence_good = obj['sentence_good']
    sentence_bad = obj['sentence_bad']
    if eval_type == 'left':
        sentence_good = obj['left_context'] + ' ' + sentence_good
        sentence_bad = obj['left_context'] + ' ' + sentence_bad
    if eval_type == 'right':
        sentence_good = sentence_good + ' ' + obj['right_context']
        sentence_bad = sentence_bad + ' ' + obj['right_context']
    instance = Instance(
        sentence_good=sentence_good,
        sentence_bad=sentence_bad,
    )
    return instance


@cli.command()
@click.option('-e', '--eval_type', type=str, required=True)
@click.argument('filename')
def load_dataset(filename, eval_type):
    assert eval_type in ('left', 'right', 'no_context')
    # Add the dataset
    md5sum = compute_checksum(filename)
    dataset = Dataset(filename=filename, md5sum=md5sum, eval_type=eval_type)

    # Add the instances
    with open(filename, 'r') as f:
        instances = []
        for line in f:
            obj = json.loads(line)
            instance = create_instance(obj, eval_type)
            instance.dataset = dataset
            instances.append(instance)

    with session_scope() as session:
        session.add(dataset)
        session.add_all(instances)

    logger.info('Successfully added data from {filename}')


@cli.command()
@click.argument('filename')
def create_hittype(filename):
    # Load definition from a json file
    with open(filename, 'r') as f:
        obj = json.load(f)

    with session_scope() as session:
        # Popping since we don't want in dict when querying API.
        short_name = obj.pop('ShortName')

        # Try to fail early. If the HITType gets created on MTurk but misses
        # the database we're in for a bad time...
        already_exists = (
            session.query(
                exists().where(HitType.short_name == short_name)
            ).scalar()
        )
        print(already_exists)
        if already_exists:
            raise ValueError(f'HITType "{short_name}" already exists.')

        # Create HITType on MTurk.
        response = client.create_hit_type(**obj)

        hit_type = HitType(
            short_name=short_name,
            hit_type_id=response['HITTypeId'],
            title=obj['Title'],
            keywords=obj['Keywords'],
            description=obj['Description'],
            reward=obj['Reward']
        )

        session.add(hit_type)


@cli.command()
@click.argument('filename')
def create_qualification(filename):
    # Load definition from a json file
    with open(filename, 'r') as f:
        obj = json.load(f)

    with session_scope() as session:
        # Popping since we don't want in dict when querying API.
        short_name = obj.pop('ShortName')

        # Try to fail early. If the HITType gets created on MTurk but misses
        # the database we're in for a bad time...
        already_exists = (
            session.query(Qualification)
                   .filter(Qualification.short_name == short_name)
                   .exists()
        )
        if already_exists:
            raise ValueError(f'Qualification "{short_name}" already exists.')

        # Create HITType on MTurk.
        response = client.create_qualification(**obj)

        qualification = Qualification(
            short_name=short_name,
            qualification_type_id=response['QualificationType']['QualificationTypeId'],
            name=obj['Name'],
        )

        session.add(qualification)
