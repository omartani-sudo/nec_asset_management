# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.core.cache import cache

LOGIN_MAX_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 15 * 60


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        ip = request.META.get('REMOTE_ADDR', '')
        lock_key = f'login_fail:{username}:{ip}'

        if cache.get(lock_key, 0) >= LOGIN_MAX_ATTEMPTS:
            messages.error(request, 'Too many failed login attempts. Please try again in 15 minutes.')
            return render(request, 'authentication/login.html', status=429)

        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            cache.delete(lock_key)
            login(request, user)
            if hasattr(user, 'role'):
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            else:
                messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard:dashboard')
        else:
            attempts = cache.get(lock_key, 0) + 1
            cache.set(lock_key, attempts, timeout=LOGIN_LOCKOUT_SECONDS)
            messages.error(request, 'Invalid username or password.')
    return render(request, 'authentication/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('authentication:login')


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Password changed successfully.')
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'authentication/change_password.html', {'form': form})
