from django import forms
from .models import Expense
from django.utils.timezone import now

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'description', 'date', 'category']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ExpenseForm, self).__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if not amount:
            raise forms.ValidationError('Amount is required')
        return amount

    def clean_description(self):
        description = self.cleaned_data['description']
        if not description:
            raise forms.ValidationError('Description is required')
        return description

    def clean_category(self):
        category = self.cleaned_data['category']
        if not category:
            raise forms.ValidationError('Category is required')
        return category

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.owner = self.request.user
        if commit:
            instance.save()
        return instance
