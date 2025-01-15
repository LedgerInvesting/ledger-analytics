from django.http import JsonResponse
from django.shortcuts import render


def get_data(request):
    data = {"labels": ["A", "B", "C", "D"], "values": [10, 20, 15, 25]}
    return JsonResponse(data)
