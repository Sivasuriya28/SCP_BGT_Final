import json
import requests
from django.shortcuts import render, get_object_or_404, redirect
from .models import Budget, Expense
from django.utils.timezone import now
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

def welcome(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'expenses/welcome.html')

@csrf_protect
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        user = User.objects.create_user(username=username, password=password)
        user.save()
        messages.success(request, "Account created successfully! Please login.")
        return redirect('login')

    return render(request, 'users/signup.html')

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        print("POST received!")
        print("CSRF token in POST:", request.POST.get('csrfmiddlewaretoken'))
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Redirect to the requested page or home if none provided
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')  # Fix: Redirect back to login, not home

    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('welcome')

@login_required
def home(request):
    return render(request, 'index.html', {'timestamp': now().timestamp()})

def budget_page(request):
    return render(request, 'expenses/budget.html')
    
def expense_page(request):
    return render(request, 'expenses/expense.html')

def analytics_page(request):
    return render(request, 'expenses/analytics.html')

def edit_expense(request, transaction_id):
    all_expenses = Expense.get_all()
    expense_data = next((e for e in all_expenses if e["transaction_id"] == transaction_id), None)

    if not expense_data:
        return render(request, '404.html', status=404)

    if request.method == 'POST':
        category = request.POST.get('category')
        amount = float(request.POST.get('amount'))
        description = request.POST.get('description')
        date = request.POST.get('date')
        currency = request.POST.get('currency')

        # Get converted amount directly from the hidden input in the form
        converted_amount = request.POST.get('converted_amount')
        converted_amount = float(converted_amount) if converted_amount else None

        updated_expense = Expense(
            transaction_id=transaction_id,
            category=category,
            amount=amount,
            description=description,
            date=date,
            converted_amount=converted_amount,
            converted_currency="EUR",
            currency=currency
        )
        updated_expense.save()
        return redirect('home')

    return render(request, 'expenses/edit_expense.html', {'expense': expense_data})

def delete_expense(request, transaction_id):
    all_expenses = Expense.get_all()
    expense_data = next((e for e in all_expenses if e["transaction_id"] == transaction_id), None)

    if not expense_data:
        return render(request, '404.html', status=404)

    if request.method == 'POST':
        Expense.delete(transaction_id)
        return redirect('home')

    return render(request, 'expenses/delete_expense.html', {'expense': expense_data})


def edit_budget(request, pk):
    # Find budget manually since we're using custom model
    budget = next((b for b in Budget.get_all() if b["budget_id"] == str(pk)), None)
    if not budget:
        return render(request, '404.html', status=404)

    if request.method == 'POST':
        new_amount = request.POST.get('allocated_amount')
        if new_amount:
            updated = Budget(budget_id=budget["budget_id"], category=budget["category"], allocated_amount=new_amount)
            updated.save()
            return redirect('home')

    return render(request, 'expenses/edit_budget.html', {'budget': budget})


def delete_budget(request, pk):
    budget = next((b for b in Budget.get_all() if b["budget_id"] == str(pk)), None)
    if not budget:
        return render(request, '404.html', status=404)

    if request.method == 'POST':
        from .models import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM budgets WHERE budget_id = ?", (str(pk),))
        conn.commit()
        conn.close()
        return redirect('home')

    return render(request, 'expenses/delete_budget.html', {'budget': budget})
