# tracker/encoders.py
from decimal import Decimal
from django.core.serializers.json import DjangoJSONEncoder

class DecimalJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)