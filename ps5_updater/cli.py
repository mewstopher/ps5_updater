# _*_ coding: utf-8 _*_

"""Console script for ps5_updater."""
import sys
import click
from ps5_updater.ps5_updater import func1


@click.command()
def main(args=None):
    """console script for ps5_updater."""
    click.echo("Hello, what would you like to search for?")
    return 0


if __name__ == "__main__":
    sys.exit(main()) # pragma: no cover
