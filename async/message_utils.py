# coding: utf-8
import redis

from rest_framework.renderers import JSONRenderer


class UTFJSONRenderer(JSONRenderer):
    ensure_ascii = True
