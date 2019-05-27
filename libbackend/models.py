from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Author(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return "{}".format(self.name)

class Genre(models.Model):
    genre = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return "{}".format(self.genre)

class Book(models.Model):
    isbn10 = models.CharField(max_length=20, unique=True)
    isbn13 = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    authors = models.ManyToManyField(to=Author, related_name="books", blank=True) #, through="Books2Authors", blank=True)
    genres = models.ManyToManyField(to=Genre, related_name="books", blank=True) #, through="Books2Genres", blank=True)

    publisher = models.CharField(max_length=255, blank=True)
    published_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)

    page_count = models.IntegerField(null=True, blank=True)
    language = models.CharField(max_length=16, blank=True)

    users = models.ManyToManyField(User, related_name="books", through='Book2User', blank=True)

    def __str__(self):
        return "Book {}, {}".format(self.title, self.isbn13)

class BookImage(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='book_image')
    small_thumbnail = models.URLField(blank=True)
    thumbnail = models.URLField(blank=True)
    small = models.URLField(blank=True)
    medium = models.URLField(blank=True)
    large = models.URLField(blank=True)
    extra_large = models.URLField(blank=True)

    class Meta:
        verbose_name = 'Book image'
        verbose_name_plural = 'Book images'

class Book2User(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    OWNER = 'own'
    OBSERVER = 'obs'
    BORROWER = 'bor'
    USER_LINK_TYPE_CHOICES = (
        (OWNER, 'Owner'),
        (OBSERVER, 'Observer'),
        (BORROWER, 'Borrower')
    )
    user_link_type = models.CharField(max_length=3, choices=USER_LINK_TYPE_CHOICES, default=OWNER)

    class Meta:
        verbose_name = 'Book to user'
        verbose_name_plural = 'Books to users'

"""
class Books2Authors(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

class Books2Genres(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
"""