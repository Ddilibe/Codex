from django.contrib import admin
from books.models import Book, Transactions, BookStatus, Reviews
# Register your models here.


admin.site.register(Book)
admin.site.register(Transactions)
admin.site.register(BookStatus)
admin.site.register(Reviews)