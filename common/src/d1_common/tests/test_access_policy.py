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

import unittest

import d1_common.access_policy
import d1_common.xml
import d1_test.util


class TestAccessPolicy(unittest.TestCase):
  def setUp(self):
    self.ap_pyxb = d1_test.util.read_test_xml('accessPolicy_v1_0.redundant.xml')

  def test_0010(self):
    """_get_grouped_permission_dict()"""
    perm_dict = d1_common.access_policy._get_grouped_permission_dict([
      ('subj1', 'write'),
      ('subj2', 'read'),
      ('subj3', 'write'),
    ])
    self.assertDictEqual(
      perm_dict, {
        'read': ['subj2'],
        'write': ['subj1', 'subj3'],
      }
    )

  def test_0020(self):
    """get_normalized_permission_from_iter()"""
    self.assertEqual(
      d1_common.access_policy.get_normalized_permission_from_iter(
        ['write', 'changePermission']
      ),
      'changePermission',
    )

  def test_0030(self):
    """get_normalized_permission_from_iter()"""
    self.assertEqual(
      d1_common.access_policy.get_normalized_permission_from_iter(['write']),
      'write',
    )

  def test_0040(self):
    """get_normalized_permission_from_iter()"""
    self.assertIsNone(
      d1_common.access_policy.get_normalized_permission_from_iter([])
    )

  def test_0050(self):
    """get_effective_permission_list_from_iter()"""
    self.assertListEqual(
      d1_common.access_policy.get_effective_permission_list_from_iter(
        ['write', 'changePermission']
      ),
      ['read', 'write', 'changePermission'],
    )

  def test_0060(self):
    """get_effective_permission_list_from_iter()"""
    self.assertListEqual(
      d1_common.access_policy.get_effective_permission_list_from_iter(['write']
                                                                      ),
      ['read', 'write'],
    )

  def test_0070(self):
    """get_effective_permission_list_from_iter()"""
    self.assertIsNone(
      d1_common.access_policy.get_effective_permission_list_from_iter([])
    )

  def test_0080(self):
    """is_subject_allowed()"""
    self.assertTrue(
      d1_common.access_policy.is_subject_allowed(self.ap_pyxb, 'subj1', 'read')
    )

  def test_0090(self):
    """is_subject_allowed()"""
    self.assertFalse(
      d1_common.access_policy.
      is_subject_allowed(self.ap_pyxb, 'subj1', 'write')
    )

  def test_0100(self):
    """is_subject_allowed()"""
    self.assertFalse(
      d1_common.access_policy.
      is_subject_allowed(self.ap_pyxb, 'subj1', 'changePermission')
    )

  def test_0110(self):
    """is_subject_allowed()"""
    self.assertTrue(
      d1_common.access_policy.is_subject_allowed(self.ap_pyxb, 'subj2', 'read')
    )

  def test_0120(self):
    """is_subject_allowed()"""
    self.assertTrue(
      d1_common.access_policy.
      is_subject_allowed(self.ap_pyxb, 'subj2', 'write')
    )

  def test_0130(self):
    """is_subject_allowed()"""
    self.assertFalse(
      d1_common.access_policy.
      is_subject_allowed(self.ap_pyxb, 'subj2', 'changePermission')
    )

  def test_0140(self):
    """get_access_policy_pyxb()"""
    ap_dict = {
      'read': ['subj2'],
      'write': ['subj1', 'subj3'],
    }
    ap_pyxb = d1_common.access_policy.get_access_policy_pyxb(ap_dict)
    ap_xml = d1_test.util.read_utf8_to_unicode('accessPolicy_v1_0.basic.xml')
    self.assertEqual(ap_pyxb.toxml(), ap_xml)

  def test_0150(self):
    """get_effective_permission_dict()"""
    ap_dict = d1_common.access_policy.get_effective_permission_dict(
      self.ap_pyxb
    )
    expected_ap_dict = {
      u'subj1': ['read'],
      u'subj2': ['read', 'write'],
      u'subj3': ['read', 'write'],
      u'subj4': ['read', 'write', 'changePermission'],
      u'subj5': ['read', 'write'],
    }
    self.assertDictEqual(ap_dict, expected_ap_dict)

  def test_0160(self):
    """get_normalized_permission_list()"""
    ap_list = d1_common.access_policy.get_normalized_permission_list(
      self.ap_pyxb
    )
    expected_ap_list = [
      (u'subj1', 'read'),
      (u'subj2', 'write'),
      (u'subj3', 'write'),
      (u'subj4', 'changePermission'),
      (u'subj5', 'write'),
    ]
    self.assertListEqual(ap_list, expected_ap_list)

  def test_0170(self):
    """get_effective_permission_list()"""
    ap_list = d1_common.access_policy.get_effective_permission_list(
      self.ap_pyxb, 'subj5'
    )
    self.assertListEqual(ap_list, ['read', 'write'])