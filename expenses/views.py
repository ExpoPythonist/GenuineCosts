from itertools import chain

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View

from .forms import ExpenseForm
from .models import Category, Expense, CustomCategory
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from userpreferences.models import UserPreference
import datetime


def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


@method_decorator(login_required(login_url='/authentication/login'), name='dispatch')
class ExpenseIndexView(View):
    template_name = 'expenses/index.html'
    items_per_page = 5

    def get(self, request, *args, **kwargs):
        expenses = Expense.objects.filter(owner=request.user)
        paginator = Paginator(expenses, self.items_per_page)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        try:
            user_preference = UserPreference.objects.get(user=request.user)
            currency = user_preference.currency
        except Exception:
            currency = None

        context = {
            'expenses': expenses,
            'page_obj': page_obj,
            'currency': currency
        }
        return render(request, self.template_name, context)


@method_decorator(login_required(login_url='/authentication/login'), name='dispatch')
class AddExpenseView(View):
    template_name = 'expenses/add_expense.html'

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        owner = request.user.id
        c_categories = CustomCategory.objects.filter(owner=owner).all()
        combined_categories = list(chain(categories, c_categories))

        context = {
            'categories': combined_categories,
            'values': request.GET
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = ExpenseForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense saved successfully')
            return redirect('expenses')

        messages.error(request, 'Please fix the errors below.')
        context = {'categories': Category.objects.all(), 'form': form}
        return render(request, self.template_name, context)


@method_decorator(login_required(login_url='/authentication/login'), name='dispatch')
class EditExpenseView(View):
    template_name = 'expenses/edit-expense.html'

    def get(self, request, id, *args, **kwargs):
        expense = get_object_or_404(Expense, pk=id)
        categories = Category.objects.all()
        # form = ExpenseForm(instance=expense)

        context = {
            'expense': expense,
            'values': expense,
            'categories': categories
        }
        return render(request, self.template_name, context)

    def post(self, request, id, *args, **kwargs):
        expense = get_object_or_404(Expense, pk=id)
        form = ExpenseForm(request.POST, instance=expense, request=request)

        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully')
            return redirect('expenses')

        messages.error(request, 'Please fix the errors below.')
        context = {'expense': expense, 'form': form, 'categories': Category.objects.all()}
        return render(request, self.template_name, context)


def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed')
    return redirect('expenses')


def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30 * 6)
    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=six_months_ago, date__lte=todays_date)
    finalrep = {}

    def get_category(expense):
        return expense.category

    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)

        for item in filtered_by_category:
            amount += item.amount
        return amount

    for x in expenses:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)

    return JsonResponse({'expense_category_data': finalrep}, safe=False)


def stats_view(request):
    return render(request, 'expenses/stats.html')
