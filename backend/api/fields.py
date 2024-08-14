import base64

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format_info, img_str = data.split(';base64,')
            file_ext = format_info.split('/')[-1]
            data = ContentFile(
                base64.b64decode(img_str),
                name=f'temp.{file_ext}'
            )
        return super().to_internal_value(data)
