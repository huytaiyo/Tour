from django.shortcuts import render , redirect , get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Location , Hotel , FlightTicket , Booking
from django.contrib.auth.decorators import login_required
from django.db.models import Q

def home(request):
    locations = Location.objects.all()
    hotels = Hotel.objects.all()
    categories = ['flight', 'hotel', 'location','tour','car rental']
    context = {
        'locations': locations,
        'hotels': hotels,
        'categories': categories,
    }
    return render(request, 'home/home.html', context)

def user_logout(request):
    logout(request)
    return redirect('home:home')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request, user)
            return redirect('home:home')
        else:
            messages.error(request, "username or password is incorrect")
    return render(request, 'home/login.html')

def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if password != password2:
            messages.error(request, "Passwords do not match")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
        else:
            user = User.objects.create_user(username=username, password=password)
            messages.success(request, "User registered successfully")
            return redirect('home:login')
    return render(request, 'home/register.html')

def search(request):
    query = request.GET.get('q', '')
    item_type = request.GET.get('type', 'hotel')
    results = []
    if item_type == 'hotel':
        results = Hotel.objects.filter(
            Q(name__icontains=query) | Q(location__name__icontains=query)
        )
    elif item_type =='flight':
        results = FlightTicket.objects.filter(
            Q(flight_number__icontains=query) | Q(origin__name__icontains=query) | Q(destination__name__icontains=query)
        )
    context = {
        'results' : results,
        'query' : query,
        'item_type' : item_type,
    }
    return render(request, 'home/search.html', context)