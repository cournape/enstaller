"""
This is the indexed_repo API
============================

FIXME: more text here

"""
import re
import string
from os.path import join, isfile

from chain import Chain
from requirement import Req, dist_as_req
from metadata import spec_from_dist
from dist_naming import filename_dist
