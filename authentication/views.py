from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.models import User
import json
from django.http import JsonResponse
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.db.models import Sum
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from expenses.models import CustomCategory, Expense
from userincome.models import UserIncome
from .forms import UserForm
from .utils import account_activation_token
from django.urls import reverse
from django.contrib import auth


# Create your views here.


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'sorry email in use,choose another one '}, status=409)
        return JsonResponse({'email_valid': True})


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'username should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'sorry username in use,choose another one '}, status=409)
        return JsonResponse({'username_valid': True})


class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fieldValues': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, 'Password too short')
                    return render(request, 'authentication/register.html', context)

                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = True
                user.save()
                current_site = get_current_site(request)
                email_body = {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                }

                link = reverse('activate', kwargs={
                    'uidb64': email_body['uid'], 'token': email_body['token']})

                email_subject = 'Activate your account'

                activate_url = 'http://' + current_site.domain + link
                try:
                    email = EmailMessage(
                        email_subject,
                        'Hi ' + user.username + ', Please the link below to activate your account \n' + activate_url,
                        'noreply@semycolon.com',
                        [email],
                    )
                    email.send(fail_silently=False)
                    messages.success(request, 'Account successfully created')
                except:
                    pass

                return render(request, 'authentication/register.html')

        return render(request, 'authentication/register.html')


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('login' + '?message=' + 'User already activated')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully')
            return redirect('login')

        except Exception as ex:
            pass

        return redirect('login')


class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome, ' +
                                     user.username + ' you are now logged in')
                    return redirect('expenses')
                messages.error(
                    request, 'Account is not active,please check your email')
                return render(request, 'authentication/login.html')
            messages.error(request, 'Invalid credentials,try again')
            return render(request, 'authentication/login.html')

        messages.error(request, 'Please fill all fields')
        return render(request, 'authentication/login.html')


class AccountView(View):
    def get(self, request):
        expenses = Expense.objects.filter(owner=request.user.id).aggregate(total_expenses=Sum('amount'))[
                       'total_expenses'] or 0
        incomes = UserIncome.objects.filter(owner=request.user.id).aggregate(total_incomes=Sum('amount'))[
                      'total_incomes'] or 0

        available_balance = incomes - expenses

        context = {
            'user_id': request.user.id if request.user.id else None,
            'username': request.user.username if request.user.username else None,
            'email': request.user.email if request.user.email else None,
            'first_name': request.user.first_name if request.user.first_name else None,
            'last_name': request.user.last_name if request.user.last_name else None,
            'available_balance': available_balance if available_balance else None
        }

        return render(request, 'account_view.html', context)

# class AccountEditView(View):
#     def get(self, request):
#         context = {
#             'user_id': request.user.id if request.user.id else None,
#             'username': request.user.username if request.user.username else None,
#             'email': request.user.email if request.user.email else None,
#             'first_name': request.user.first_name if request.user.first_name else None,
#             'last_name': request.user.last_name if request.user.last_name else None
#         }
#
#         return render(request, 'account_view.html', context)

@method_decorator(login_required(login_url='/authentication/login'), name='dispatch')
class AccountEditView(View):
    model = User
    form_class = UserForm
    template_name = 'account_edit.html'

    def get_object(self, queryset=None):
        return self.model.objects.get(username=self.request.user.username)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        form = self.form_class(instance=instance)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        form = self.form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('account_view')  # Assuming 'account_view' is the name of your account view URL
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')
