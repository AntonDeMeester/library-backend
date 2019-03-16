from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def empty_get(request, format=None):
    return Response({"message": "Empty get"})