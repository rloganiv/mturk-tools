"""
The command-line interface.

Defines `cli` to be used as a singleton in other scripts.
"""
import logging
import sys

import click

# TODO: Refactor so that we don't need to manually import all new commands...
from mtools.config import config
import mtools.db
import mtools.deploy
import mtools.io
import mtools.evaluate
import mtools.mturk


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):

    level = logging.DEBUG if debug else logging.INFO

    logger = logging.getLogger()
    logger.setLevel(level)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(level)

    file_handler = logging.FileHandler(config['logging']['logfile'])
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)


# TODO: Something less tedious
cli.add_command(mtools.db.init_db)
cli.add_command(mtools.db.clear_db)
cli.add_command(mtools.deploy.deploy)
cli.add_command(mtools.io.load_dataset)
cli.add_command(mtools.io.create_hittype)
cli.add_command(mtools.io.create_qualification)
cli.add_command(mtools.mturk.accept_all)


if __name__ == '__main__':
    cli()

