from django.contrib import admin

from libbackend.models import Book, Author, Genre, BookImage

# Register your models here.
admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(BookImage)
