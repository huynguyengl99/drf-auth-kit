from urllib.parse import unquote_plus

from rest_framework import serializers


class UnquoteStringField(serializers.CharField):
    def to_internal_value(self, data: str) -> str:
        return unquote_plus(data)
