from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
import datetime

from libbackend.models import Book, Author, Genre, BookImage


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('name',)

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('genre',)

class BookImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookImage
        fields = ('book', 'small_thumbnail', 'thumbnail', 'small', 'medium', 'large', 'extra_large',)

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('title', 'subtitle', 'publisher', 'publisheddate', 'description', 'pagecount', 
                'language', 'isbn', 'genres', 'authors', 'book_image',)

class GoogleVolumeSerializer(serializers.Serializer):
    volumeInfo = serializers.DictField()
    
    def create(self, validated_data):
        #print(validated_data)
        volume = validated_data["volumeInfo"]

        isbn13 = "-1"
        for isbn in volume["industryIdentifiers"]:
            if isbn["type"] == "ISBN_13":
                isbn13 = isbn["identifier"]

        try: 
            queried_book = Book.objects.get(isbn13=isbn13)
            print("Book already in database. ")
            return queried_book
        except ObjectDoesNotExist:
            pass

        authors = volume.pop('authors',{})
        print(authors)
        for author in authors:
            data = dict()
            data['name'] = author
            author_serializer = AuthorSerializer(data=data)
            if author_serializer.is_valid(raise_exception=True):
                authors = author_serializer.save()

        genres = volume.pop('categories',{})
        if volume.get("mainCategory", False) and volume.get("mainCategory", False) not in genres:
            genres[genres.length] = volume["mainCategory"]
        for genre in genres:
            data = dict()
            data["genre"] = genre
            genre_serializer = GenreSerializer(data=data)
            if genre_serializer.is_valid(raise_exception=True):
                genres = genre_serializer.save()

        book_data = dict()
        for isbn in volume["industryIdentifiers"]:
            if isbn["type"] == "ISBN_10":
                book_data["isbn10"] = isbn["identifier"]
            elif isbn["type"] == "ISBN_13":
                book_data["isbn13"] = isbn["identifier"]
            else:
                continue #Do nothing for the moment
        
        if volume.get("title", False):
            book_data["title"] = volume["title"]
        if volume.get("subtitle", False):
            book_data["subtitle"] = volume["subtitle"]
        if volume.get("publisher", False):
            book_data["publisher"] = volume["publisher"]
        if volume.get("publishedDate", False):
            book_data["published_date"] = datetime.datetime(int(volume["publishedDate"]), 1,1)
        if volume.get("description", False):
            book_data["description"] = volume["description"]
        if volume.get("pageCount", False):
            book_data["page_count"] = volume["pageCount"]
        if volume.get("language", False):
            book_data["language"] = volume["language"]
        
        book = Book.objects.create(**book_data)
        book.save()
        book.genres.add(genres)
        book.authors.add(authors)
        
        book_image = volume.pop('imageLinks', False)
        if book_image:
            book_image["small_thumbnail"] = book_image.pop('smallThumbnail',"")
            book_image["extra_large"] = book_image.pop('extraLarge',"")
            
            book_image = BookImageSerializer(data=book_image, book=book)
            if book_image.is_valid(raise_exception=True):
                book_image = book_image.save()

        book.save()
        return book

    #TODO Create a good  validation method: https://www.django-rest-framework.org/api-guide/serializers/#validation
    #def validate 