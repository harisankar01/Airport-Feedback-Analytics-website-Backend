from rest_framework import serializers
from .models import Airport_feedbacks


class AirPort_serializer(serializers.ModelSerializer):
    class Meta:
        model = Airport_feedbacks
        fields = "__all__"
        allow_blank = True
