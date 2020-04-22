"""
Utilities and commands for ingesting data into mtools.
"""
import hashlib
import json
import logging

import click

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


def create_instance(obj):
    # Use dict.get for contexts since they are not required.
    instance = Instance(
        sentence_good=obj['sentence_good'],
        sentence_bad=obj['sentence_bad'],
        left_context=obj.get('left_context', None),
        right_context=obj.get('right_context', None)
    )
    return instance


@cli.command()
@click.argument('filename')
def load_dataset(filename):
    # Add the dataset
    md5sum = compute_checksum(filename)
    dataset = Dataset(filename=filename, md5sum=md5sum)
    with session_scope() as session:
        session.add(dataset)

    # Add the instances
    with open(filename, 'r') as f:
        instances = []
        for line in f:
            obj = json.loads(line)
            instance = create_instance(obj)
            instance.dataset = dataset
            instances.append(instance)

    with session_scope() as session:
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
            session.query(HitType)
                   .filter(HitType.short_name == short_name)
                   .exists()
        )
        if already_exists:
            raise ValueError(f'HITType "{short_name}" already exists.')

        # Create HITType on MTurk.
        response = client.create_hit_type(**obj)

        hit_type = HitType(
            short_name=short_name,
            hit_type_id=response['HITTypeId'],
            title=obj['Title'],
            assignment_duration=obj['AssignmentDurationInSeconds'],
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
