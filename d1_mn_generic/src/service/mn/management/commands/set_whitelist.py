#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This work was created by participants in the DataONE project, and is
# jointly copyrighted by participating institutions in DataONE. For
# more information on DataONE, see our web site at http://dataone.org.
#
#   Copyright 2009-2012 DataONE
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
"""
:mod:`set_whitelist`
=============================================

:Synopsis:
  When running in production, GMN requires that subjects that wish to create,
  update or delete science objects are registered in a whitelist. This
  management command manages the whitelist.
:Created: 2012-3-5
:Author: DataONE (Dahl)
"""

# Stdlib.
import logging

# Django.
from django.core.management.base import NoArgsCommand

# App.
import mn.models


class Command(NoArgsCommand):
  help = 'Set the whitelist for create, update and delete operations'

  def handle(self, *args, **options):
    if len(args) != 1:
      print(
        'Must specify the path to a file that contains a list of subjects '
        'to whitelist'
      )
      exit()

    verbosity = int(options.get('verbosity', 1))

    if verbosity <= 1:
      logging.getLogger('').setLevel(logging.ERROR)

    n_subjects = self.set_whitelist(args[0])

    print 'Successfully whitelisted {0} subjects'.format(n_subjects)

  def set_whitelist(self, whitelist_path):
    with open(whitelist_path) as f:
      mn.models.WhitelistForCreateUpdateDelete.objects.all().delete()
      cnt = 0
      for subject in f:
        subject = subject.strip()
        if subject == '' or subject.startswith('#'):
          continue
        w = mn.models.WhitelistForCreateUpdateDelete()
        w.set(subject)
        w.save()
        cnt += 1

    return cnt