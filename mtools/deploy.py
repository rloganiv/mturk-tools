"""
Utilities and Commands for deploying MTurk HITs.
"""
import click

from mtools.cli import cli
from mtools.db import Dataset, Hit, HitType, Instance


@cli.command()
@click.option('-n', '--num_hits', required=True, type=int)
@click.option('-q', '--questions_per_hit', required=True, type=int)
@click.argument('hit_type')
@click.argument('dataset')
def deploy():
    pass
