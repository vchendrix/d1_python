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
"""Test MNStorage.archive() for standalone objects"""

from __future__ import absolute_import

import responses

import gmn.tests.gmn_mock
import gmn.tests.gmn_test_case


@gmn.tests.gmn_mock.disable_auth_decorator
class TestArchiveStandalone(gmn.tests.gmn_test_case.D1TestCase):
  def _assert_archived_flag_set(self, client, binding):
    pid, sid, sciobj_str, sysmeta_pyxb = self.create_obj(client, binding)
    self.assertFalse(sysmeta_pyxb.archived)
    pid_archived = client.archive(pid)
    self.assertEqual(pid, pid_archived.value())
    archived_sysmeta_pyxb = client.getSystemMetadata(pid)
    self.assertTrue(archived_sysmeta_pyxb.archived)

  @responses.activate
  def test_0010_v1(self):
    """MNStorage.archive(): Archived flag is set in sysmeta"""
    self._assert_archived_flag_set(self.client_v1, self.v1)

  @responses.activate
  def test_0020_v2(self):
    """MNStorage.archive(): Archived flag is set in sysmeta"""
    self._assert_archived_flag_set(self.client_v2, self.v2)
