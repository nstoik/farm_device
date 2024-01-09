# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""
# pylint: disable=redefined-outer-name
import pytest

from fd_device.database.database import create_all_tables, drop_all_tables, get_session


@pytest.fixture(scope="session")
def dbsession():
    """Returns an sqlalchemy session."""
    yield get_session()


@pytest.fixture()
def tables(dbsession):
    """Create all tables for testing. Delete when done."""
    create_all_tables()
    yield
    dbsession.close()
    drop_all_tables()
