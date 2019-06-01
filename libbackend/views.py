import json
import coreapi

from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from rest_framework.filters import BaseFilterBackend

from .analyse import get_isbn_from_barcode, get_google_volume_from_isbn
from .models import Book, Genre, Book2User
from .serializers import BookSerializer, GoogleVolumeSerializer, GenreAPISerializer

class GenreFilter(BaseFilterBackend):
    def get_schema_fields(self, view):
        return [coreapi.Field(
            name='genre',
            location='query',
            required=False,
            type='string'
        )]

    def filter_queryset(self, request, queryset, view):
        genre = request.query_params.get('genre', None)
        if genre:
            queryset = queryset.filter(genres__genre=genre)
        return queryset

class BooksViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = BookSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = (GenreFilter, )

    def get_queryset(self):
        if self.request.query_params.get('display', None) != 'all':
            return Book.objects.filter(users=self.request.user)
        return Book.objects.all()
    
class RegisterView(APIView):
    permission_classes = (IsAuthenticated, )
    queryset = Book.objects.all()
    
    def post(self, request, *args, **kwargs):
        photo = request.FILES.get('image', None)
        if photo is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Please provide an image.")
        isbn = get_isbn_from_barcode(photo)
        if isbn == -1:
            return Response(status=status.HTTP_412_PRECONDITION_FAILED, data="Could not decode the barcode.")
        google_volume = get_google_volume_from_isbn(isbn)
        google_volume = json.loads(google_volume)
        if google_volume.get("totalItems", 0) == 0:
                return Response(status=status.HTTP_412_PRECONDITION_FAILED, data="Book not found in Google Books API")
        #print("Google volume data is " + str(google_volume.get("items", [])))
        volume_serialiser = GoogleVolumeSerializer(data=google_volume['items'], many=True)
        if volume_serialiser.is_valid(raise_exception=True):
            volume_serialiser.save()
        
        for ser_instance in volume_serialiser.instance:
            Book2User.objects.get_or_create(book=ser_instance["book"], user=self.request.user)
        
        return Response(status=status.HTTP_201_CREATED, data=volume_serialiser.data)

class GenreViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreAPISerializer
    permission_classes = (IsAuthenticated, )


        