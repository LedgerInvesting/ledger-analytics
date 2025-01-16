from rest_framework import serializers

from .models import TriangleData


class TriangleDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TriangleData
        fields = "__all__"
