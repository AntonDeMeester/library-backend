from dateutil import parser

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import transaction
from django.db.models.query import Q
import datetime

from utils.serializers import GetOrCreateSerializer

from .models import Book, Author, Genre, BookImage


#region database models
class AuthorSerializer(GetOrCreateSerializer):
    class Meta:
        model = Author
        fields = '__all__'
       

class GenreSerializer(GetOrCreateSerializer):
    class Meta:
        model = Genre
        fields = '__all__'
        
class BookImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = BookImage
        fields = '__all__'

class NestedBookImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = BookImage
        exclude = ('book', )

class BookSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, required=False)
    authors = AuthorSerializer(many=True, required=False)
    book_image = NestedBookImageSerializer()

    class Meta:
        model = Book
        exclude = ('users', )

#endregion database models

#region Google Volume parsing

class GoogleVolumeIndustryIdentifiers(serializers.Serializer):
    type = serializers.CharField()
    identifier = serializers.CharField()

class GoogleVolumeDimensionsSerializer(serializers.Serializer):
    height = serializers.CharField(required=False)
    width = serializers.CharField(required=False)
    thickness = serializers.CharField(required=False)

class GoogleVolumeImageLinksSerializer(serializers.Serializer):
    smallThumbnail = serializers.URLField(required=False)
    thumbnail = serializers.URLField(required=False)
    small = serializers.URLField(required=False)
    medium = serializers.URLField(required=False)
    large = serializers.URLField(required=False)
    extraLarge = serializers.URLField(required=False)

class GoogleVolumeInfoSerializer(serializers.Serializer):
    title = serializers.CharField()
    subtitle = serializers.CharField(required=False)
    authors = serializers.ListField(child=serializers.CharField())
    publisher = serializers.CharField(required=False)
    publishedDate = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    industryIdentifiers = GoogleVolumeIndustryIdentifiers(many=True)
    pageCount = serializers.IntegerField(required=False)
    #dimensions = GoogleVolumeDimensionsSerializer()
    #printType = serializers.ChoiceField(('BOOK', 'MAGAZINE'))
    categories = serializers.ListField(child=serializers.CharField(), required=False)
    #averageRating = serializers.FloatField()
    #ratingsCount = serializers.IntegerField()
    #contentVersion = serializers.CharField()
    imageLinks = GoogleVolumeImageLinksSerializer(required=False)
    language = serializers.CharField(required=False)
    mainCategory = serializers.CharField(required=False)
    #previewLink = serializers.URLField()

    def create(self, validated_data):

        #Check if we have the book already in the database
        isbn13 = None
        isbn10 = None
        industry_identifiers = validated_data.pop('industryIdentifiers', [])
        for isbn in industry_identifiers:
            if isbn["type"] == "ISBN_13":
                isbn13 = isbn["identifier"]
            elif isbn["type"] == "ISBN_10":
                isbn10 = isbn["identifier"]

        authors_data = validated_data.pop('authors',[])
        authors = [ {'name': x } for x in authors_data ]
        authors_serializer = AuthorSerializer(data=authors, many=True)
        authors_serializer.is_valid(raise_exception=True)

        genres_data = validated_data.pop('categories',[])
        if validated_data.get("mainCategory", False) and validated_data.get("mainCategory", None) not in genres:
            genres.append(validated_data.pop("mainCategory"))
        genres = [ {'genre': x } for x in genres_data ]
        genres_serializer = GenreSerializer(data=genres, many=True)
        genres_serializer.is_valid(raise_exception=True)

        #Transform from camelCase to snake_case + renaming and refactor if necessary
        snake_case_data = {}
        snake_case_data['title'] = validated_data.get('title')
        snake_case_data['subtitle'] = validated_data.get('subtitle', '')
        snake_case_data['publisher'] = validated_data.get('publisher', '')
        snake_case_data['published_date'] = parser.parse(validated_data.get('publishedDate', None)).date()
        snake_case_data['description'] = validated_data.get('description', '')
        snake_case_data['page_count'] = int(validated_data.get('pageCount'))
        snake_case_data['language'] = validated_data.get('language', '')

        book_image_camel = validated_data.pop('imageLinks', None)
        if book_image_camel:
            book_image_snake = {}
            book_image_snake['small_thumbnail'] = book_image_camel.get('smallThumbnail', '')
            book_image_snake['thumbnail'] = book_image_camel.get('thumbnail', '')
            book_image_snake['small'] = book_image_camel.get('small', '')
            book_image_snake['medium'] = book_image_camel.get('medium', '')
            book_image_snake['large'] = book_image_camel.get('large', '')
            book_image_snake['extra_large'] = book_image_camel.get('extraLarge', '')
                           
        #Only create everything at the end
        with transaction.atomic():
            authors_obj = authors_serializer.save()
            validated_data['authors'] = authors_obj
            genres_obj = genres_serializer.save()
            validated_data['genres'] = genres_obj
            try: 
                #Query object don't seem to exist.
                #query = Q(id=-1)
                if isbn13 is not None:
                    snake_case_data['isbn10'] = isbn10
                    book, _ = Book.objects.update_or_create(isbn13=isbn13, defaults=snake_case_data)
                elif isbn10 is not None:
                    snake_case_data['isbn13'] = isbn13
                    book, _ = Book.objects.update_or_create(isbn13=isbn13, defaults=snake_case_data)
            except MultipleObjectsReturned:
                #This is not ok. If there is one book with the same isbn13 and another with isbn10, something went wrong.
                raise ValidationError("More than one book with the same ISBN10 or ISBN13 exists. Please configure this properly.")

            if genres_obj:
                book.genres.set(genres_obj)
            if authors_obj:
                book.authors.set(authors_obj)

            if book_image_camel:
                book_image_snake['book'] = book.id
                book_image = BookImageSerializer(data=book_image_snake)
                book_image.is_valid(raise_exception=True)
                book_image.save()
        
        return book

class GoogleVolumeUserInfoSerializer(serializers.Serializer):
    review = serializers.CharField(required=False)
    isPurchased = serializers.BooleanField()

class GoogleVolumeObject():

    def __init__(self, book):
        self.book = book

class GoogleVolumeSerializer(serializers.Serializer):
    kind = serializers.CharField(write_only=True, required=False)
    id = serializers.CharField(write_only=True, required=False)
    etag = serializers.CharField(write_only=True, required=False)
    selfLink = serializers.URLField(write_only=True, required=False)
    volumeInfo = GoogleVolumeInfoSerializer(write_only=True)
    userInfo = GoogleVolumeUserInfoSerializer(write_only=True, required=False)
    book = BookSerializer(read_only=True)
    
    def create(self, validated_data):

        volume_info_serialiazer = GoogleVolumeInfoSerializer(data=validated_data['volumeInfo'])
        volume_info_serialiazer.is_valid(raise_exception=True)
        book = volume_info_serialiazer.save()

        instance = {} 
        instance['book'] = book

        return instance
#endregion Google Volume parsing

#region apimodels

class GenreAPISerializer(GenreSerializer):
    book_count = serializers.SerializerMethodField()

    def get_book_count(self, genre):
        return genre.books.count()

#endregion apimodels