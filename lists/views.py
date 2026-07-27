# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Category, Department, Location, Status, Unit

@login_required
def lists_home(request):
    if request.user.role != 'admin':
        return render(request, 'lists/lists.html', {
            'categories': Category.objects.all(),
            'departments': Department.objects.all(),
            'locations': Location.objects.all(),
            'statuses': Status.objects.all(),
            'units': Unit.objects.all(),
            'readonly': True,
        })
    return render(request, 'lists/lists.html', {
        'categories': Category.objects.all(),
        'departments': Department.objects.all(),
        'locations': Location.objects.all(),
        'statuses': Status.objects.all(),
        'units': Unit.objects.all(),
        'readonly': False,
    })

@login_required
@require_POST
def add_category(request):
    if request.user.role != 'admin':
        messages.error(request, 'Unauthorized')
        return redirect('lists:lists_home')
    name = request.POST.get('name')
    code = request.POST.get('code')
    if not name or not code:
        messages.error(request, 'Name and code required')
        return redirect('lists:lists_home')
    if Category.objects.filter(name__iexact=name).exists() or Category.objects.filter(code__iexact=code).exists():
        messages.error(request, 'Category with this name or code already exists')
        return redirect('lists:lists_home')
    Category.objects.create(name=name, code=code)
    messages.success(request, 'Category added successfully')
    return redirect('lists:lists_home')

@login_required
@require_POST
def add_department(request):
    if request.user.role != 'admin':
        messages.error(request, 'Unauthorized')
        return redirect('lists:lists_home')
    name = request.POST.get('name')
    if not name:
        messages.error(request, 'Name required')
        return redirect('lists:lists_home')
    if Department.objects.filter(name__iexact=name).exists():
        messages.error(request, 'Department already exists')
        return redirect('lists:lists_home')
    Department.objects.create(name=name)
    messages.success(request, 'Department added successfully')
    return redirect('lists:lists_home')

@login_required
@require_POST
def add_location(request):
    if request.user.role != 'admin':
        messages.error(request, 'Unauthorized')
        return redirect('lists:lists_home')
    name = request.POST.get('name')
    if not name:
        messages.error(request, 'Name required')
        return redirect('lists:lists_home')
    if Location.objects.filter(name__iexact=name).exists():
        messages.error(request, 'Location already exists')
        return redirect('lists:lists_home')
    Location.objects.create(name=name)
    messages.success(request, 'Location added successfully')
    return redirect('lists:lists_home')

@login_required
@require_POST
def add_status(request):
    if request.user.role != 'admin':
        messages.error(request, 'Unauthorized')
        return redirect('lists:lists_home')
    name = request.POST.get('name')
    if not name:
        messages.error(request, 'Name required')
        return redirect('lists:lists_home')
    if Status.objects.filter(name__iexact=name).exists():
        messages.error(request, 'Status already exists')
        return redirect('lists:lists_home')
    Status.objects.create(name=name)
    messages.success(request, 'Status added successfully')
    return redirect('lists:lists_home')

@login_required
@require_POST
def add_unit(request):
    if request.user.role != 'admin':
        messages.error(request, 'Unauthorized')
        return redirect('lists:lists_home')
    name = request.POST.get('name')
    if not name:
        messages.error(request, 'Name required')
        return redirect('lists:lists_home')
    if Unit.objects.filter(name__iexact=name).exists():
        messages.error(request, 'Unit already exists')
        return redirect('lists:lists_home')
    Unit.objects.create(name=name)
    messages.success(request, 'Unit added successfully')
    return redirect('lists:lists_home')
