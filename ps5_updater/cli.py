# _*_ coding: utf-8 _*_

from ps5_updater.notifiers.store_notifiers import TargetNotifier, BestBuyNotifier
from ps5_updater.logging import logging_config
from logging.config import dictConfig
import click
import sys

dictConfig(logging_config)


@click.group()
def main(args=None):
    """console script for ps5_updater."""
    return 0


@main.command()
def search_target():
    try:
        target = TargetNotifier()
        status = target.send_notification()
        print(status)
    except Exception as exc:
        click.secho(str(exc), err=True, fg='red')
    return 0


@main.command()
def search_best_buy():
    try:
        best_buy = BestBuyNotifier()
        best_buy.send_notification()
    except Exception as exc:
        click.secho(str(exc), err=True, fg='red')
    return 0

if __name__ == "__main__":
    sys.exit(main()) # pragma: no cover
