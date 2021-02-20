#!/usr/bin/env python
# _*_ coding: utf-8 _*_

"""Tests for 'ps5_updater' package"""

import pytest

from click.testing import CliRunner

from ps5_updater import cli
from ps5_updater.ps5_updater import func1


@pytest.fixture
def response():
    pass


def test_content(response):
    assert True


def test_func1():
    func_return = func1()
    assert func_return == 'foobar'


def test_command_line_interface():
    """test the cli"""
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help Show this message and exit.' in help_result.output