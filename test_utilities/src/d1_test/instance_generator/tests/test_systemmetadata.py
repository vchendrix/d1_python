#!/usr/bin/env python
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

import hashlib
import logging
import unittest

import d1_common.types.dataoneTypes_v1 as dataoneTypes_v1
import d1_test.instance_generator.system_metadata as sysmeta

#===============================================================================


class TestSystemMetadata(unittest.TestCase):
  def setUp(self):
    pass

  def test_0010(self):
    """generate()"""
    s = sysmeta.generate()
    self.assertIsInstance(s, dataoneTypes_v1.SystemMetadata)
    self.assertTrue(s.toxml())

  def ztest_020(self):
    """generate_from_file()"""
    s = sysmeta.generate_from_file(__file__)
    self.assertIsInstance(s, dataoneTypes_v1.SystemMetadata)
    self.assertTrue(s.toxml())
    checksum_calculator = hashlib.sha1()
    with open(__file__, 'rb') as f:
      checksum_calculator.update(f.read())
    self.assertEqual(s.checksum.value(), checksum_calculator.hexdigest())


if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  unittest.main()