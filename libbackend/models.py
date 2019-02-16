from django.db import models

# Create your models here.
class Book(models.Model):
    isbn10 = models.CharField(max_length=20, unique=True)
    isbn13 = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    authors = models.ManyToManyField("Author")
    genres = models.ManyToManyField("Genre")

    publisher = models.CharField(max_length=255, blank=True)
    published_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)

    page_count = models.IntegerField(blank=True)
    language = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return_string = "Book title: " + self.title + ", ISBN13: " + self.isbn13
        return return_string
    

class Author(models.Model):
    name = models.CharField(max_length=255)

class Genre(models.Model):
    genre = models.CharField(max_length=255)

class BookImage(models.Model):
    book = models.ForeignKey(Book, null=True, blank=True, on_delete=models.CASCADE, related_name='book')
    small_thumbnail = models.URLField(blank=True)
    thumbnail = models.URLField(blank=True)
    small = models.URLField(blank=True)
    medium = models.URLField(blank=True)
    large = models.URLField(blank=True)
    extra_large = models.URLField(blank=True)