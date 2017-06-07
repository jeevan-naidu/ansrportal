from django.contrib import admin
from models import Book, Publisher, Author
# Register your models here.


class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'ISBN', 'genre', 'publisher', 'author', 'lend_period', 'page_amount']
    search_fields = ['title', 'genre']


class PublisherAdmin(admin.ModelAdmin,):
    list_display = ['name']


class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'surname']


admin.site.register(Publisher, PublisherAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Author, AuthorAdmin)
