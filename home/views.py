from django.shortcuts import render , redirect , get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import (Location , Hotel , FlightTicket , Booking, Tour, CarTransfer, Promotion, UserProfile, TourImage, HotelImage)
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Min, Max, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse

def home(request):
    featured_hotels = Hotel.objects.filter(is_featured=True)[:6]
    featured_locations = Location.objects.filter(is_featured=True)[:8]
    featured_flights = FlightTicket.objects.filter(is_featured=True)[:6]
    featured_tours = Tour.objects.filter(is_featured=True)[:6]
    featured_cars = CarTransfer.objects.filter(is_featured=True)[:6]
    active_promotions = Promotion.objects.filter(is_active=True, end_date__gte=timezone.now())

    categories = [
        {'name': 'vé máy bay', 'icon': 'fas fa-plane', 'url': ' home:flight_search'},
        {'name': 'khách sạn', 'icon': 'fas fa-hotel', 'url': ' home:hotel_search'},
        {'name': 'tour', 'icon': 'fas fa-sightseeing', 'url': ' home:tour_search'},
        {'name': 'xe đưa đón', 'icon': 'fas fa-car', 'url': ' home:car_search'},
    ]
    context = {
        featured_hotels: featured_hotels,
        popular_locations: popular_locations,
        featured_flights: featured_flights,
        featured_tours: featured_tours,
        featured_cars: featured_cars,
        active_promotions: active_promotions,
        categories: categories,
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
            Q(flight_number__icontains=query) | Q(origin__name__icontains=query) | Q(destination__name__icontains=query)| Q(airline__icontains=query)
        )
    elif item_type == 'tour':
        results = Tour.objects.filter(
            Q(name__icontains=query) | Q(location__name__icontains=query)
        )
    elif item_type == 'car':
        results = CarTransfer.objects.filter(
            Q(name__icontains=query) | Q(location__name__icontains=query)
        )

    context = {
        'results' : results,
        'query' : query,
        'item_type' : item_type,
    }
    return render(request, 'home/search.html', context)

def detail(request, item_type, item_id):
    item = None
    if item_type == 'hotel':
        item = get_object_or_404(Hotel, id=item_id)
        related_items = Hotel.objects.filter(location=item.location).exclude(id=item.id)[:3]
    elif item_type == 'flight':
        item = get_object_or_404(FlightTicket, id=item_id)
        related_items = FlightTicket.objects.filter(origin=item.origin, destination=item.destination).exclude(id=item.id)[:3]
    elif item_type == 'tour':
        item = get_object_or_404(Tour, id=item_id)
        related_items = Tour.objects.filter(location=item.location).exclude(id=item.id)[:3]
    elif item_type == 'car':
        item = get_object_or_404(CarTransfer, id=item_id)
        related_items = CarTransfer.objects.filter(location=item.location).exclude(id=item.id)[:3]
    elif item_type == 'location':
        item = get_object_or_404(Location, id=item_id)
        related_items = Location.objects.filter(is_popular = True).exclude(id=item.id)[:3]

    promotion = Promotion.objects.filter(Q(promotion_type=item_type)| Q(promotion_type = 'general'), is_active=True, end_date__gt=timezone.now())[:2]

    context = {
        'item': item,
        'item_type': item_type,
        'related_items': related_items,
        'promotion': promotion,
    }
    return render(request, 'home/detail.html', context)

def booking(request, item_type, item_id):
    if request.method == 'POST':
        user = request.user
        check_in_date = request.POST.get('check_in_date')
        check_out_date = request.POST.get('check_out_date')
        number_of_guests = request.POST.get('number_of_guests')
        special_requests = request.POST.get('promo_code', '')

        booking_data = {
            'user': user,
            'booking_type': item_type,
            'check_in_date': check_in_date if check_in_date else None,
            'check_out_date': check_out_date if check_out_date else None,
            'number_of_guests': number_of_guests,
            'special_requests': special_requests,
            'status': 'confirmed',
        }

        if promo_code:
            try:
                promotion = Promotion.objects.get(code=promo_code, is_active=True, start_date_lte=timezone.now(), end_date__gte=timezone.now())
                booking_data['promotion'] = promotion   
            except Promotion.DoesNotExist:
                messages.warning(request, "Invalid promo code")

        if item_type == 'hotel':
            hotel = get_object_or_404(Hotel, id=item_id)
            booking_data['hotel'] = hotel

            if check_in_date and nights > 0:
                check_in  = datetime.strptime(check_in_date, '%Y-%m-%d').date()
                check_out = datetime.strptime(check_out_date, '%Y-%m-%d').date()
                nights = (check_out - check_in).days
                booking_data['total_price'] = hotel.price * nights * number_of_guests
            else:
                booking_data['total_price'] = hotel.price

        elif item_type == 'flight':
            flight = get_object_or_404(FlightTicket, id=item_id)
            booking_data['flight'] = flight
            booking_data['total_price'] = flight.price * number_of_guests

        elif item_type == 'tour':
            tour = get_object_or_404(Tour, id=item_id)
            booking_data['tour'] = tour
            booking_data['total_price'] = tour.price * number_of_guests

        elif item_type == 'car':
            car = get_object_or_404(CarTransfer, id=item_id)
            booking_data['car'] = car
            booking_data['total_price'] = car.price
            
        if 'promotion' in booking_data:
            promotion = booking_data['promotion']
            if promotion.discount_percent > 0:
                discount = booking_data['total_price'] * (promotion.discount_percent / 100)
                booking_data['total_price'] -= discount
            elif promotion.fixed_amount > 0:
                booking_data['total_price'] -= promotion.fixed_amount

        booking = Booking.objects.create(**booking_data)

        messages.success(request, "Booking created successfully!")
        return redirect('home:orders')
    else:
        item = None
        if item_type == 'hotel':
            item = get_object_or_404(Hotel, id=item_id)
        elif item_type == 'flight':
            item = get_object_or_404(FlightTicket, id=item_id)
        elif item_type == 'tour':
            item = get_object_or_404(Tour, id=item_id)
        elif item_type == 'car':
            item = get_object_or_404(CarTransfer, id=item_id)

        promotions = Promotion.objects.filter(Q(promotion_type=item_type) | Q(promotion_type='general'), is_active=True, start_date__lt=timezone.now(), end_date__gt=timezone.now())
    context = {
        'item': item,
        'item_type': item_type,
        'promotions': promotions,
        'today': timezone.now().date().isoformat(),
        'tomorrow': (timezone.now().date() + timedelta(days=1)).isoformat(),

    }
    return render(request, 'home/booking.html', context)