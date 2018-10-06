#!/usr/bin/env python
# coding: utf-8

import os
import sys

sys.setdefaultencoding('utf8')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HDFS_Web.settings")

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()