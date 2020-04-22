"""
The command-line interface.

Defines `cli` to be used as a singleton in other scripts.
"""
import logging

import click

from mtools.config import config


@click.group()
@click.option('--debug', default=False)
def cli(debug):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        filename=config['logging']['logfile'],
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        level=level
    )


if __name__ == '__main__':
    cli()
