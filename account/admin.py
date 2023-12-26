from django.contrib import admin
from account.models import CustomUser, PatronUser, AuthorUser
# Register your models here.


admin.site.register(CustomUser)
admin.site.register(PatronUser)
admin.site.register(AuthorUser)