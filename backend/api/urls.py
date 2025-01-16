from django.urls import path

from .views import TriangleDataList

urlpatterns = [
    path("triangle-data/", TriangleDataList.as_view(), name="triangle-data-list"),
]
