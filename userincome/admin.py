from django.contrib import admin
from .models import UserIncome, Source, CustomSource

# Register your models here.

admin.site.register(UserIncome)
admin.site.register(Source)
admin.site.register(CustomSource)
