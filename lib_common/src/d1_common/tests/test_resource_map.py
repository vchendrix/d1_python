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

from __future__ import absolute_import

import cStringIO as StringIO

import rdflib
import rdflib.compare

import d1_common.resource_map
import d1_common.util

import d1_test.d1_test_case


class TestResourceMap(d1_test.d1_test_case.D1TestCase):
  # def _norm_nt(self, nt_str):
  #   return sorted([sorted(v.split(' ')) for v in nt_str.split('\n')])

  # def _normalize_n_triples(self, nt_str):
  #   return '\n'.join(sorted(nt_str.splitlines()))

  # def _norm_triples(self, triple_list):
  #   return sorted([sorted(v) for v in triple_list])

  # def _norm_to_str(self, nt_str):
  #   return pprint.pformat(self._norm_nt(nt_str))

  # def _assert_is_equal_nt(self, a_nt, b_nt):
  #   assert self._norm_nt(a_nt) == self._norm_nt(b_nt)

  def _create(self):
    return d1_common.resource_map.ResourceMap(
      'ore_pid', 'meta_pid', ['data_pid', 'data2_pid', 'data3_pid'], debug=False
    )

  def _sort_obj(self, obj):
    if isinstance(obj, dict):
      return self._sort_obj(obj.items())
    elif isinstance(obj, list):
      return sorted(obj)
    return obj

  def test_0010(self, mn_client_v2):
    """__init__(): Empty"""
    ore = d1_common.resource_map.ResourceMap()
    assert isinstance(ore, d1_common.resource_map.ResourceMap)

  def test_0020(self, mn_client_v2):
    """__init__(): Instantiate resource map by ORE PID"""
    ore = d1_common.resource_map.ResourceMap('test_pid', ore_software_id='TEST')
    self.assert_equals_sample(ore, 'resource_map_pid', mn_client_v2)

  def test_0030(self, mn_client_v2):
    """serialize(): Instantiate resource map by pid, scimeta and scidata"""
    ore = self._create()
    self.assert_equals_sample(ore, 'resource_map_full', mn_client_v2)

  def test_0040(self, mn_client_v2):
    """getAggregation()"""
    ore = self._create()
    aggr = ore.getAggregation()
    assert isinstance(aggr, rdflib.URIRef)
    assert str(
      aggr
    ) == 'https://cn.dataone.org/cn/v2/resolve/ore_pid/aggregation'

  def test_0050(self, mn_client_v2):
    """getObjectByPid()"""
    ore = self._create()
    u = ore.getObjectByPid('ore_pid')
    assert isinstance(u, rdflib.URIRef)
    assert str(u) == 'https://cn.dataone.org/cn/v2/resolve/ore_pid'

  def test_0060(self, mn_client_v2):
    """addResource()"""
    ore = self._create()
    ore.addResource('resource1_pid')
    self.assert_equals_sample(ore, 'resource_map_add_resource', mn_client_v2)

  def test_0070(self, mn_client_v2):
    """setDocuments()"""
    ore = self._create()
    ore.addResource('resource1_pid')
    ore.addResource('resource2_pid')
    ore.setDocuments('resource1_pid', 'resource2_pid')
    self.assert_equals_sample(ore, 'resource_map_set_documents', mn_client_v2)

  def test_0080(self, mn_client_v2):
    """setDocumentedBy()"""
    ore = self._create()
    ore.addResource('resource1_pid')
    ore.addResource('resource2_pid')
    ore.setDocuments('resource1_pid', 'resource2_pid')
    self.assert_equals_sample(
      ore, 'resource_map_set_documented_by', mn_client_v2
    )

  def test_0090(self, mn_client_v2):
    """addMetadataDocument()"""
    ore = self._create()
    ore.addMetadataDocument('meta_pid')
    self.assert_equals_sample(
      ore, 'resource_map_add_metadata_document_by', mn_client_v2
    )

  def test_0100(self, mn_client_v2):
    """addDataDocuments()"""
    ore = self._create()
    ore.addDataDocuments(['more_data1_pid', 'more_data2_pid'], 'meta_pid')
    self.assert_equals_sample(
      ore, 'resource_map_add_data_documents_by', mn_client_v2
    )

  def test_0110(self, mn_client_v2):
    """getResourceMapPid()"""
    ore = self._create()
    resource_map_pid = ore.getResourceMapPid()
    assert isinstance(resource_map_pid, str)
    assert resource_map_pid == 'ore_pid'

  def test_0120(self, mn_client_v2):
    """getAllTriples()"""
    ore = self._create()
    triple_list = ore.getAllTriples()
    sorted_triple_list = self._sort_obj(triple_list)
    self.assert_equals_sample(
      sorted_triple_list, 'resource_map_get_all_triples', mn_client_v2
    )

  def test_0130(self, mn_client_v2):
    """getAllPredicates()"""
    ore = self._create()
    predicate_list = ore.getAllPredicates()
    sorted_predicate_list = self._sort_obj(predicate_list)
    self.assert_equals_sample(
      sorted_predicate_list, 'resource_map_get_all_predicates', mn_client_v2
    )

  def test_0140(self, mn_client_v2):
    """getSubjectObjectsByPredicate()"""
    ore = self._create()
    subobj_list = ore.getSubjectObjectsByPredicate(
      'http://www.openarchives.org/ore/terms/isAggregatedBy'
    )
    sorted_subobj_list = self._sort_obj(subobj_list)
    self.assert_equals_sample(
      sorted_subobj_list, 'resource_map_get_subject_objects_by_predicate',
      mn_client_v2
    )

  def test_0150(self, mn_client_v2):
    """getAggregatedPids()"""
    ore = self._create()
    pid_list = ore.getAggregatedPids()
    sorted_pid_list = self._sort_obj(pid_list)
    self.assert_equals_sample(
      sorted_pid_list, 'resource_map_get_aggregated_pids', mn_client_v2
    )

  def test_0160(self, mn_client_v2):
    """getAggregatedScienceMetadataPids()"""
    ore = self._create()
    pid_list = ore.getAggregatedScienceMetadataPids()
    sorted_pid_list = self._sort_obj(pid_list)
    self.assert_equals_sample(
      sorted_pid_list, 'resource_map_get_aggregated_science_metadata_pids',
      mn_client_v2
    )

  def test_0170(self, mn_client_v2):
    """getAggregatedScienceDataPids()"""
    ore = self._create()
    pid_list = ore.getAggregatedScienceDataPids()
    sorted_pid_list = self._sort_obj(pid_list)
    self.assert_equals_sample(
      sorted_pid_list, 'resource_map_get_aggregated_science_data_pids',
      mn_client_v2
    )

  def test_0180(self, mn_client_v2):
    """asGraphvizDot()"""
    ore = self._create()
    stream = StringIO.StringIO()
    ore.asGraphvizDot(stream)
    self.assert_equals_sample(
      stream.getvalue(), 'resource_map_as_graphviz_dot', mn_client_v2
    )
    # print stream.getvalue()
    # return
    # assert 'node1 -> node2' in stream.getvalue()