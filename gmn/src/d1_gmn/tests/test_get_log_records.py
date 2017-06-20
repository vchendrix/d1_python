# -*- coding: utf-8 -*-

# This work was created by participants in the DataONE project, and is
# jointly copyrighted by participating institutions in DataONE. For
# more information on DataONE, see our web site at http://dataone.org.
#
#   Copyright 2009-2016 DataONE
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Test MNRead.getLogRecords()
"""

from __future__ import absolute_import

import datetime

import freezegun
import pytest
import responses

import d1_gmn.app.models
import d1_gmn.app.util
import d1_gmn.tests.gmn_mock
import d1_gmn.tests.gmn_test_case

import d1_common
import d1_common.types
import d1_common.types.exceptions
import d1_common.xml

import d1_test.d1_test_case
import d1_test.instance_generator.system_metadata


@d1_test.d1_test_case.reproducible_random_decorator('TestGetLogRecords')
@freezegun.freeze_time('1977-05-27')
class TestGetLogRecords(d1_gmn.tests.gmn_test_case.GMNTestCase):
  @responses.activate
  def test_1001(self, mn_client_v1_v2):
    """getLogRecords(): Slicing: start=0, count=0 returns empty slice with
    correct total event count
    """
    with d1_gmn.tests.gmn_mock.disable_auth():
      log = mn_client_v1_v2.getLogRecords(start=0, count=0)
      d1_test.d1_test_case.D1TestCase.assert_equals_sample(
        log, 'get_log_records__number_of_events', mn_client_v1_v2
      )

  @responses.activate
  def test_1002(self, mn_client_v1_v2):
    """getLogRecords(): Slicing: Retrieve front section
    """
    with d1_gmn.tests.gmn_mock.disable_auth():
      log = mn_client_v1_v2.getLogRecords(start=0, count=21)
      d1_test.d1_test_case.D1TestCase.assert_equals_sample(
        log, 'get_log_records__front_section', mn_client_v1_v2
      )

  @responses.activate
  def test_1003(self, mn_client_v1_v2):
    """getLogRecords(): Slicing: Retrieve middle section
    """
    with d1_gmn.tests.gmn_mock.disable_auth():
      log = mn_client_v1_v2.getLogRecords(start=2000, count=15)
      d1_test.d1_test_case.D1TestCase.assert_equals_sample(
        log, 'get_log_records__middle_section', mn_client_v1_v2
      )

  @responses.activate
  def test_1004(self, mn_client_v1_v2):
    """getLogRecords(): Slicing: Retrieve exact end section
    """
    with d1_gmn.tests.gmn_mock.disable_auth():
      n_events = self.get_total_log_records(mn_client_v1_v2)
      # Slice indexes are zero based.
      log = mn_client_v1_v2.getLogRecords(start=n_events - 1, count=1)
      d1_test.d1_test_case.D1TestCase.assert_equals_sample(
        log, 'get_log_records__exact_end_section', mn_client_v1_v2
      )

  @responses.activate
  def test_1005(self, mn_client_v1_v2):
    """getLogRecords(): Slicing: Specifying more events than are
    available returns the available events
    """
    with d1_gmn.tests.gmn_mock.disable_auth():
      n_events = self.get_total_log_records(mn_client_v1_v2)
      # Slice indexes are zero based.
      log = mn_client_v1_v2.getLogRecords(start=n_events - 10, count=100)
      d1_test.d1_test_case.D1TestCase.assert_equals_sample(
        log, 'get_log_records__count_beyond_end_section', mn_client_v1_v2
      )

  @responses.activate
  def test_1006(self, mn_client_v1_v2):
    """getLogRecords(): Slicing: Specifying start above available events
    returns an empty list
    """
    with d1_gmn.tests.gmn_mock.disable_auth():
      n_events = self.get_total_log_records(mn_client_v1_v2)
      # Slice indexes are zero based.
      log = mn_client_v1_v2.getLogRecords(start=n_events + 1234, count=10000)
      d1_test.d1_test_case.D1TestCase.assert_equals_sample(
        log, 'get_log_records__start_beyond_end_section', mn_client_v1_v2
      )

  @responses.activate
  def test_1010(self, mn_client_v1_v2):
    """MNRead.getLogRecords(): event type filter: Unknown event returns an empty
    list.

    In v2, event type is not an enum.
    """
    with d1_gmn.tests.gmn_mock.disable_auth():
      log = mn_client_v1_v2.getLogRecords(event='bogus_event')
      d1_test.d1_test_case.D1TestCase.assert_equals_sample(
        log, 'get_log_records__event_filter_unknown', mn_client_v1_v2
      )

  @responses.activate
  def test_1011(self, mn_client_v1_v2):
    """MNRead.getLogRecords(): event type filter: known event returns list of
    requested size with total equal to the number of events of the type
    """
    with d1_gmn.tests.gmn_mock.disable_auth():
      log = mn_client_v1_v2.getLogRecords(event='update', count=10)
      d1_test.d1_test_case.D1TestCase.assert_equals_sample(
        log, 'get_log_records__event_filter_update', mn_client_v1_v2
      )

  @responses.activate
  def test_1012(self, mn_client_v1_v2):
    """MNRead.getLogRecords(): Date range query: Get all events from 1979
    """
    with d1_gmn.tests.gmn_mock.disable_auth():
      newest_log = mn_client_v1_v2.getLogRecords(
        fromDate=datetime.datetime(1979, 1, 1),
        toDate=datetime.datetime(1979, 12, 31), start=0, count=1
      )
      n_match = newest_log.total
      oldest_log = mn_client_v1_v2.getLogRecords(
        fromDate=datetime.datetime(1979, 1, 1),
        toDate=datetime.datetime(1979, 12, 31), start=n_match - 1, count=1
      )
      # Verify that first and last records are both in 1979 and that first doc
      # is the newest, as GMN sorts on timestamp descending.
      d1_test.d1_test_case.D1TestCase.assert_equals_sample(
        '\n\n'.join([self.format_pyxb(v) for v in (newest_log, oldest_log)]),
        'get_log_records__date_range_first_last',
        mn_client_v1_v2,
      )

  @responses.activate
  def test_1013(self, mn_client_v1_v2):
    """MNRead.getLogRecords(): Date range query: Using a date range in the
    future returns empty list
    """
    with d1_gmn.tests.gmn_mock.disable_auth():
      log = mn_client_v1_v2.getLogRecords(
        fromDate=datetime.datetime(2500, 1, 1),
        toDate=datetime.datetime(3000, 12, 31), start=0, count=1
      )
      d1_test.d1_test_case.D1TestCase.assert_equals_sample(
        log,
        'get_log_records__date_range_in_the_future',
        mn_client_v1_v2,
      )

  @responses.activate
  def test_1014(self, mn_client_v1_v2):
    """MNRead.getLogRecords(): Date range query: End date before start date
    raises InvalidRequest
    """
    with pytest.raises(d1_common.types.exceptions.InvalidRequest):
      with d1_gmn.tests.gmn_mock.disable_auth():
        mn_client_v1_v2.getLogRecords(
          fromDate=datetime.datetime(1692, 5, 1),
          toDate=datetime.datetime(1445, 9, 2), start=0, count=1
        )

  @responses.activate
  @freezegun.freeze_time('2388-08-28')
  def test_1015(self, mn_client_v1_v2):
    """MNRead.getLogRecords(): create() of object causes a new create event to
    be added for the given PID
    """
    with d1_gmn.tests.gmn_mock.disable_auth():
      n_create_events_before = self.get_total_log_records(
        mn_client_v1_v2, event='create'
      )
      with freezegun.freeze_time('2388-08-28'):
        pid, sid, sciobj_str, sysmeta_pyxb = self.create_obj(
          mn_client_v1_v2, now_dt=datetime.datetime(2388, 8, 28)
        )
      # The event timestamp is set directly in the db, so it's not covered by
      # freezegun. We just set it manually.
      sciobj_model = d1_gmn.app.util.get_sci_model(pid)
      event_log_model = d1_gmn.app.models.EventLog.objects.get(
        sciobj=sciobj_model
      )
      event_log_model.timestamp = sysmeta_pyxb.dateUploaded
      event_log_model.save()
      #
      n_create_events_after = self.get_total_log_records(
        mn_client_v1_v2, event='create'
      )
      assert n_create_events_after == n_create_events_before + 1
      # Verify that the most recent record now matches the object that was created
      event_pyxb = mn_client_v1_v2.getLogRecords(start=0, count=1)
      d1_test.d1_test_case.D1TestCase.assert_equals_sample(
        '\n'.join(
          '{}: {}'.format(k, v) for k, v in {
            'pid': pid,
            'sid': sid,
            'sysmeta': d1_common.xml.pretty_pyxb(sysmeta_pyxb),
            'create_event': d1_common.xml.pretty_pyxb(event_pyxb),
          }.items()
        ),
        'get_log_records__new_create_event',
        mn_client_v1_v2,
      )