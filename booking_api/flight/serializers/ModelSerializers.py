from flight.models import *
from rest_framework import serializers


class AirportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airport
        fields = "__all__"
        extra_kwargs = {
            "city": {"required": True},
            "name": {"required": True},
            "code": {"required": True},
            "country": {"required": True}

        }
    
    
