from django.contrib import admin

from userpreferences.models import UserPreference
from .models import Expense, Category, CustomCategory


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('amount', 'description', 'owner', 'category', 'date',)
    search_fields = ('description', 'category', 'date',)

    list_per_page = 5


admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Category)
admin.site.register(UserPreference)
admin.site.register(CustomCategory
                    )
