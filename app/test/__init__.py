#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

from ... import *


def report(**k):
	"""Run all tests in the test package."""
	trix.ncreate('app.test.loadmodules.report', **k)
	

