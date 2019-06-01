from django.contrib import admin

from libbackend.models import Book, Author, Genre, BookImage

class BookImageTabularInLine(admin.TabularInline):
    model = BookImage

class BookAdmin(admin.ModelAdmin):
    inlines = (BookImageTabularInLine, )

# Register your models here.
admin.site.register(Book, BookAdmin)
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(BookImage)
