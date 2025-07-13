from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.db.models import Sum
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import Transaction, Category, Goal
from .forms import TransactionForm, CategoryForm, GoalForm, CustomUserCreationForm, CustomUserChangeForm
from django.contrib import messages
import json
from decimal import Decimal
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import logout as auth_logout

class DecimalJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)
    
@login_required
def dashboard(request):
    # Calculate time periods
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    year_ago = today - timedelta(days=365)
    
    # Get transactions
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:5]
    
    # Calculate totals
    total_income = Transaction.objects.filter(user=request.user, is_income=True).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Transaction.objects.filter(user=request.user, is_income=False).aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense
    
    # Time-based totals
    income_data = {
        'today': Transaction.objects.filter(user=request.user, is_income=True, date=today).aggregate(Sum('amount'))['amount__sum'] or 0,
        'week': Transaction.objects.filter(user=request.user, is_income=True, date__gte=week_ago).aggregate(Sum('amount'))['amount__sum'] or 0,
        'month': Transaction.objects.filter(user=request.user, is_income=True, date__gte=month_ago).aggregate(Sum('amount'))['amount__sum'] or 0,
        'year': Transaction.objects.filter(user=request.user, is_income=True, date__gte=year_ago).aggregate(Sum('amount'))['amount__sum'] or 0,
    }
    
    expense_data = {
        'today': Transaction.objects.filter(user=request.user, is_income=False, date=today).aggregate(Sum('amount'))['amount__sum'] or 0,
        'week': Transaction.objects.filter(user=request.user, is_income=False, date__gte=week_ago).aggregate(Sum('amount'))['amount__sum'] or 0,
        'month': Transaction.objects.filter(user=request.user, is_income=False, date__gte=month_ago).aggregate(Sum('amount'))['amount__sum'] or 0,
        'year': Transaction.objects.filter(user=request.user, is_income=False, date__gte=year_ago).aggregate(Sum('amount'))['amount__sum'] or 0,
    }
    
    # Category breakdown for expenses
    expense_categories = Category.objects.filter(user=request.user, is_income=False)
    category_data = []
    for category in expense_categories:
        total = Transaction.objects.filter(
            user=request.user, 
            category=category, 
            is_income=False
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        if total > 0:
            category_data.append({
                'name': category.name,
                'total': float(total)  # Convert Decimal to float
            })
    
    # Goals
    goals = Goal.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'income_data': income_data,
        'expense_data': expense_data,
        'category_data': json.dumps(category_data),
        'goals': goals,
        'category_data': json.dumps(category_data, cls=DecimalJSONEncoder),
    }
    return render(request, 'tracker/dashboard.html', context)

@login_required
def transactions(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'tracker/transactions.html', {'transactions': transactions})

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.is_income = True if request.GET.get('type') == 'income' else False
            transaction.save()
            messages.success(request, "Transaction added successfully.")
            return redirect('transactions')
    else:
        form = TransactionForm()
    return render(request, 'tracker/add_transaction.html', {'form': form})
    
    # Filter categories based on transaction type if provided
    transaction_type = request.GET.get('type', '')
    if transaction_type:
        is_income = transaction_type == 'income'
        form.fields['category'].queryset = Category.objects.filter(user=request.user, is_income=is_income)
    
    return render(request, 'tracker/add_transaction.html', {'form': form})

@login_required
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('transactions')
    return render(request, 'tracker/confirm_delete.html', {'object': transaction})

@login_required
def profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'tracker/profile.html', {'form': form})

@login_required
def goals(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, 'Goal added successfully!')
            return redirect('goals')
    else:
        form = GoalForm()
    
    goals = Goal.objects.filter(user=request.user)
    return render(request, 'tracker/goals.html', {'form': form, 'goals': goals})

@login_required
def update_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Goal updated successfully!')
            return redirect('goals')
    else:
        form = GoalForm(instance=goal)
    return render(request, 'tracker/update_goal.html', {'form': form})

@login_required
def delete_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Goal deleted successfully!')
        return redirect('goals')
    return render(request, 'tracker/confirm_delete.html', {'object': goal})

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('dashboard')
    else:
        form = CategoryForm()
    return render(request, 'tracker/add_category.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # Create default categories for the new user
            default_expense_categories = ['Food', 'Transport', 'Rent', 'Entertainment', 'Utilities', 'Shopping']
            default_income_categories = ['Salary', 'Freelance', 'Gift', 'Investment']
            
            for category in default_expense_categories:
                Category.objects.create(user=user, name=category, is_income=False)
            
            for category in default_income_categories:
                Category.objects.create(user=user, name=category, is_income=True)
            
            messages.success(request, 'Registration successful! Default categories have been created.')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'tracker/register.html', {'form': form})

def logout_view(request):  # <--- Renamed from 'logout' to 'logout_view'
    auth_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

@login_required
def set_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Password updated successfully!')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'tracker/set_password.html', {
        'form': form,
        'title': 'Set Password'
    })