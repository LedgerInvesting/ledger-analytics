from rest_framework import generics

from .models import TriangleData
from .serializers import TriangleDataSerializer


class TriangleDataList(generics.ListAPIView):
    queryset = TriangleData.objects.all()
    serializer_class = TriangleDataSerializer
