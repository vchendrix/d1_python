# -*- coding: utf-8 -*-

# This work was created by participants in the DataONE project, and is
# jointly copyrighted by participating institutions in DataONE. For
# more information on DataONE, see our web site at http://dataone.org.
#
#   Copyright 2009-2016 DataONE
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import print_function

import logging
import os
import subprocess

import psycopg2
import psycopg2.extensions
import pytest

import d1_gmn.tests.gmn_test_case

from d1_client.cnclient_1_1 import CoordinatingNodeClient_1_1 as cn_v1
from d1_client.cnclient_2_0 import CoordinatingNodeClient_2_0 as cn_v2
from d1_client.mnclient_1_1 import MemberNodeClient_1_1 as mn_v1
from d1_client.mnclient_2_0 import MemberNodeClient_2_0 as mn_v2

import django.conf
import django.core.management
import django.db
import django.db.utils

# from django.db import django.db.connections

DEFAULT_DEBUG_PYCHARM_BIN_PATH = os.path.expanduser('~/bin/JetBrains/pycharm')

# import d1_common.util
# d1_common.util.log_setup(True)


def pytest_addoption(parser):
  """Add a command line option to pytest that enables a mode that invokes
  `kdiff3` to display diffs and, after user confirmation, can automatically
  update or write new test sample documents on mismatches.

  The diff should be studied carefully before updating the sample since there is
  a risk of introducing errors.

  The implementation is in D1TestCase.assert_equals_sample()
  """
  parser.addoption(
    '--update-samples', action='store_true', default=False,
    help='Prompt to update or write new test sample files on failures'
  )
  parser.addoption(
    '--pycharm', action='store_true', default=False,
    help='Attempt to move the cursor in PyCharm to location of most recent test '
    'failure'
  )
  parser.addoption(
    '--refresh-fixture', action='store_true', default=False,
    help='Force reloading the template fixture'
  )


def pytest_generate_tests(metafunc):
  """Parameterize test functions via parameterize_dict class member"""
  try:
    func_arg_list = metafunc.cls.parameterize_dict[metafunc.function.__name__]
  except (AttributeError, KeyError):
    return
  arg_names = sorted(func_arg_list[0])
  metafunc.parametrize(
    arg_names,
    [[func_args[name] for name in arg_names] for func_args in func_arg_list]
  )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
  """Attempt to open error locations in PyCharm. Use with -x / --exitfirst"""
  outcome = yield
  if not pytest.config.getoption("--pycharm"):
    return
  rep = outcome.get_result()
  if rep.when == "call" and rep.failed:
    # src_path, src_line, func_name = rep.location
    src_path = call.excinfo.traceback[-1].path
    src_line = call.excinfo.traceback[-1].lineno + 1
    logging.info('src_path="{}", src_line={}'.format(src_path, src_line))
    # return
    if src_path == '<string>':
      logging.debug('Unable to find location of error')
      return
    try:
      subprocess.call([
        DEFAULT_DEBUG_PYCHARM_BIN_PATH, '--line', str(src_line), str(src_path)
      ])
    except subprocess.CalledProcessError as e:
      logging.warn(
        'Unable to open in PyCharm. error="{}" src_path="{}", src_line={}'.
        format(str(e), src_path, src_line)
      )
    else:
      logging.debug(
        'Opened in PyCharm. src_path="{}", src_line={}'.
        format(src_path, src_line)
      )


# Fixtures for parameterizing tests over CN/MN and v1/v2 clients.

MOCK_BASE_URL = 'http://mock/node'

# CN and MN (for baseclient)


@pytest.fixture(scope='function', params=[cn_v1, mn_v1])
def cn_mn_client_v1(request):
  yield request.param(MOCK_BASE_URL)


@pytest.fixture(scope='function', params=[cn_v2, mn_v2])
def cn_mn_client_v2(request):
  yield request.param(MOCK_BASE_URL)


@pytest.fixture(scope='function', params=[cn_v1, mn_v1, cn_v2, mn_v2])
def cn_mn_client_v1_v2(request):
  yield request.param(MOCK_BASE_URL)


# CN clients


@pytest.fixture(scope='function', params=[cn_v1])
def cn_client_v1(request):
  yield request.param(MOCK_BASE_URL)


@pytest.fixture(scope='function', params=[cn_v2])
def cn_client_v2(request):
  yield request.param(MOCK_BASE_URL)


@pytest.fixture(scope='function', params=[cn_v1, cn_v2])
def cn_client_v1_v2(request):
  yield request.param(MOCK_BASE_URL)


# MN clients


@pytest.fixture(scope='function', params=[mn_v1])
def mn_client_v1(request):
  yield request.param(MOCK_BASE_URL)


@pytest.fixture(scope='function', params=[mn_v2])
def mn_client_v2(request):
  yield request.param(MOCK_BASE_URL)


@pytest.fixture(scope='function', params=[mn_v1, mn_v2])
def mn_client_v1_v2(request):
  yield request.param(MOCK_BASE_URL)


# DB fixtures


@pytest.yield_fixture(scope='session')
def django_db_setup(django_db_blocker):
  """Set up DB fixture
  """
  logging.info('Setting up DB fixture')
  test_db_key = 'default'
  test_db_name = django.conf.settings.DATABASES[test_db_key]['NAME']
  template_db_key = 'template'
  template_db_name = django.conf.settings.DATABASES[template_db_key]['NAME']

  with django_db_blocker.unblock():
    try:
      load_template_fixture(template_db_key, template_db_name)
    except psycopg2.DatabaseError as e:
      logging.debug(str(e))
    logging.debug('Dropping test DB')
    run_sql('postgres', "drop database if exists {};".format(test_db_name))
    logging.debug('Creating test DB from template')
    run_sql(
      'postgres',
      "create database {} template {};".format(test_db_name, template_db_name)
    )
    # Haven't found out how to prevent transactions from being started, so
    # closing the implicit transaction here so that template fixture remains
    # available.
    django.db.connections[test_db_key].commit()
    logging.debug('Test DB ready')
    yield


def load_template_fixture(template_db_key, template_db_name):
  """Load DB fixture from compressed JSON file to template database"""
  logging.info('Loading template DB fixture')
  fixture_file_path = d1_gmn.tests.gmn_test_case.GMNTestCase.get_sample_path(
    'db_fixture.json.bz2'
  )
  if pytest.config.getoption("--refresh-fixture"):
    # django.core.management.call_command('flush', database=template_db_key)
    run_sql('postgres', "drop database if exists {};".format(template_db_name))
  logging.debug('Creating blank DB')
  run_sql(
    'postgres', "create database {} encoding 'utf-8';".format(template_db_name)
  )
  logging.debug('Creating GMN tables')
  django.core.management.call_command(
    'migrate', '--run-syncdb', database=template_db_key
  )
  logging.debug('Populating tables with fixture data')
  django.core.management.call_command(
    'loaddata', fixture_file_path, database=template_db_key, commit=True
  )
  django.db.connections[template_db_key].commit()
  for connection in django.db.connections.all():
    connection.close()


def run_sql(db, sql):
  try:
    conn = psycopg2.connect(database=db)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(sql)
  except psycopg2.DatabaseError as e:
    logging.debug('SQL query result="{}"'.format(str(e)))
    raise
  try:
    return cur.fetchall()
  except psycopg2.DatabaseError:
    return None
  finally:
    # django.db.connections[test_db_key].close()
    conn.close()
    for connection in django.db.connections.all():
      connection.close()


@pytest.fixture(autouse=True)
# @pytest.mark.django_db(transaction=True)
def enable_db_access(db):
  pass
