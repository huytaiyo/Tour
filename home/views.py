from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import (
    Location, Hotel, FlightTicket, Booking, Tour, CarTransfer, 
    Promotion, UserProfile, TourImage, HotelImage, Room, RoomImage
)
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Min, Max, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse

def user_logout(request):
    logout(request)
    return redirect('home:home')

def home(request):
    featured_hotels = Hotel.objects.filter(is_featured=True)[:6]
    featured_flights = FlightTicket.objects.filter(is_featured=True)[:6]
    featured_tours = Tour.objects.filter(is_featured=True)[:6]
    featured_cars = CarTransfer.objects.filter(is_featured=True)[:6]
    popular_locations = Location.objects.filter(is_popular=True)[:8]
    active_promotions = Promotion.objects.filter(is_active=True, end_date__gt=timezone.now())[:4]

    categories = [
        {'name': 'Vé máy bay', 'icon': 'fas fa-plane', 'url': 'home:flight_search'},
        {'name': 'Khách sạn', 'icon': 'fas fa-hotel', 'url': 'home:hotel_search'},
        {'name': 'Tour', 'icon': 'fas fa-map-marked-alt', 'url': 'home:tour_search'},
        {'name': 'Xe đưa đón', 'icon': 'fas fa-car', 'url': 'home:car_search'}
    ]

    context = {
        'featured_hotels': featured_hotels,
        'featured_flights': featured_flights,
        'featured_tours': featured_tours,
        'featured_cars': featured_cars,
        'popular_locations': popular_locations,
        'active_promotions': active_promotions,
        'categories': categories,
    }
    return render(request, 'home/home.html', context)

def search(request):
    query = request.GET.get('q', '')
    item_type = request.GET.get('type', 'hotel')  # 'hotel', 'flight', 'tour', or 'car'
    results = []

    if item_type == 'hotel':
        results = Hotel.objects.filter(
            Q(name__icontains=query) | Q(location__name__icontains=query)
        )



    elif item_type == 'flight':
        results = FlightTicket.objects.filter(
            Q(flight_number__icontains=query) | 
            Q(airline__icontains=query) |
            Q(origin__name__icontains=query) | 
            Q(destination__name__icontains=query)
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
        'results': results,
        'query': query,
        'item_type': item_type,
    }
    return render(request, 'home/search.html', context)

def detail(request, item_type, item_id):
    item = None
    related_items = []
    rooms = []

    if item_type == 'hotel':
        item = get_object_or_404(Hotel, id=item_id)
        related_items = Hotel.objects.filter(location=item.location).exclude(id=item_id)[:3]
        rooms = Room.objects.filter(hotel=item, is_available=True).order_by('price')
    elif item_type == 'flight':
        item = get_object_or_404(FlightTicket, id=item_id)
        related_items = FlightTicket.objects.filter(
            Q(origin=item.origin) | Q(destination=item.destination)
        ).exclude(id=item_id)[:3]
    elif item_type == 'tour':
        item = get_object_or_404(Tour, id=item_id)
        related_items = Tour.objects.filter(location=item.location).exclude(id=item_id)[:3]
    elif item_type == 'car':
        item = get_object_or_404(CarTransfer, id=item_id)
        related_items = CarTransfer.objects.filter(location=item.location).exclude(id=item_id)[:3]
    elif item_type == 'location':
        item = get_object_or_404(Location, id=item_id)
        related_items = Location.objects.filter(is_popular=True).exclude(id=item_id)[:3]
    elif item_type == 'room':
        room = get_object_or_404(Room, id=item_id)
        item = room.hotel
        item_type = 'hotel'  # Switch back to hotel type for template rendering
        rooms = [room]  # Just show this specific room
        related_items = Room.objects.filter(hotel=item, is_available=True).exclude(id=item_id)[:3]

    # Get applicable promotions
    promotions = Promotion.objects.filter(
        Q(promotion_type=item_type) | Q(promotion_type='general'),
        is_active=True,
        end_date__gt=timezone.now()
    )[:2]

    context = {
        'item': item,
        'item_type': item_type,
        'related_items': related_items,
        'promotions': promotions,
        'rooms': rooms,
    }
    return render(request, 'home/detail.html', context)

@login_required
def booking(request, item_type, item_id):
    if request.method == 'POST':
        user = request.user
        check_in_date = request.POST.get('check_in_date')
        check_out_date = request.POST.get('check_out_date')
        number_of_guests = int(request.POST.get('number_of_guests', 1))
        special_requests = request.POST.get('special_requests', '')
        promo_code = request.POST.get('promo_code', '')
        room_id = request.POST.get('room_id')  # For hotel room bookings

        # Initialize booking with common fields
        booking_data = {
            'user': user,
            'booking_type': item_type,
            'check_in_date': check_in_date if check_in_date else None,
            'check_out_date': check_out_date if check_out_date else None,
            'number_of_guests': number_of_guests,
            'special_requests': special_requests,
            'status': 'confirmed'
        }

        # Apply promotion if valid
        if promo_code:
            try:
                promotion = Promotion.objects.get(
                    promo_code=promo_code,
                    is_active=True,
                    start_date__lte=timezone.now(),
                    end_date__gte=timezone.now()
                )
                booking_data['promotion'] = promotion
            except Promotion.DoesNotExist:
                messages.warning(request, 'Mã khuyến mãi không hợp lệ hoặc đã hết hạn.')

        # Set item-specific fields and calculate total price
        if item_type == 'hotel':
            hotel = get_object_or_404(Hotel, id=item_id)
            booking_data['hotel'] = hotel

            # Calculate number of nights
            if check_in_date and check_out_date:
                check_in = datetime.strptime(check_in_date, '%Y-%m-%d').date()
                check_out = datetime.strptime(check_out_date, '%Y-%m-%d').date()
                nights = (check_out - check_in).days

                # If a specific room was selected
                if room_id:
                    room = get_object_or_404(Room, id=room_id, hotel=hotel)
                    booking_data['total_price'] = room.price * nights * number_of_guests
                else:
                    booking_data['total_price'] = hotel.price * nights * number_of_guests
            else:
                if room_id:
                    room = get_object_or_404(Room, id=room_id, hotel=hotel)
                    booking_data['total_price'] = room.price
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

        # Apply discount if promotion exists
        if 'promotion' in booking_data:
            promotion = booking_data['promotion']
            if promotion.discount_percent > 0:
                discount = booking_data['total_price'] * (promotion.discount_percent / 100)
                booking_data['total_price'] -= discount
            elif promotion.discount_amount > 0:
                booking_data['total_price'] -= promotion.discount_amount

        # Create booking
        booking = Booking.objects.create(**booking_data)

        # Redirect to payment page
        return redirect('home:payment', booking_id=booking.id)
    else:
        item = None
        room = None

        if item_type == 'hotel':
            item = get_object_or_404(Hotel, id=item_id)
            # Get available rooms for this hotel
            rooms = Room.objects.filter(hotel=item, is_available=True).order_by('price')
        elif item_type == 'room':
            room = get_object_or_404(Room, id=item_id)
            item = room.hotel
            item_type = 'hotel'  # Switch back to hotel type for template rendering
        elif item_type == 'flight':
            item = get_object_or_404(FlightTicket, id=item_id)
        elif item_type == 'tour':
            item = get_object_or_404(Tour, id=item_id)
        elif item_type == 'car':
            item = get_object_or_404(CarTransfer, id=item_id)

        # Get valid promotions for this item type
        promotions = Promotion.objects.filter(
            Q(promotion_type=item_type) | Q(promotion_type='general'),
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        )

        context = {
            'item': item,
            'item_type': item_type,
            'room': room,
            'rooms': rooms if item_type == 'hotel' and not room else None,
            'promotions': promotions,
            'today': timezone.now().date().isoformat(),
            'tomorrow': (timezone.now() + timedelta(days=1)).date().isoformat(),
        }
        return render(request, 'home/booking.html', context)

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home:home')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
    return render(request, 'home/login.html')

def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email', '')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        phone_number = request.POST.get('phone_number', '')

        if password != password2:
            messages.error(request, 'Mật khẩu không khớp.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            # Create user profile
            UserProfile.objects.create(user=user, phone_number=phone_number)
            messages.success(request, 'Đăng ký thành công. Vui lòng đăng nhập.')
            return redirect('home:login')
    return render(request, 'home/register.html')

@login_required
def user_orders(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    context = {
        'bookings': bookings,
    }
    return render(request, 'home/orders.html', context)

@login_required
def user_profile(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        # Update user info
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()

        # Update profile info
        profile.phone_number = request.POST.get('phone_number', '')
        profile.address = request.POST.get('address', '')

        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        profile.save()
        messages.success(request, 'Thông tin cá nhân đã được cập nhật.')
        return redirect('home:profile')

    context = {
        'profile': profile,
    }
    return render(request, 'home/profile.html', context)

def hotel_search(request):
    # Get filter parameters
    location_id = request.GET.get('location', '')
    check_in = request.GET.get('check_in', '')
    check_out = request.GET.get('check_out', '')
    guests = request.GET.get('guests', '1')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    stars = request.GET.getlist('stars', [])

    # Base queryset
    hotels = Hotel.objects.all()

    # Apply filters
    if location_id:
        hotels = hotels.filter(location_id=location_id)

    if min_price:
        hotels = hotels.filter(price__gte=min_price)

    if max_price:
        hotels = hotels.filter(price__lte=max_price)

    if stars:
        hotels = hotels.filter(stars__in=stars)

    # Get all locations for the filter dropdown
    locations = Location.objects.all()

    # Get min and max prices for the price slider
    price_range = Hotel.objects.aggregate(min_price=Min('price'), max_price=Max('price'))

    context = {
        'hotels': hotels,
        'locations': locations,
        'price_range': price_range,
        'filters': {
            'location_id': location_id,
            'check_in': check_in,
            'check_out': check_out,
            'guests': guests,
            'min_price': min_price or price_range['min_price'],
            'max_price': max_price or price_range['max_price'],
            'stars': stars,
        }
    }
    return render(request, 'home/hotel_search.html', context)

def flight_search(request):
    # Get filter parameters
    origin_id = request.GET.get('origin', '')
    destination_id = request.GET.get('destination', '')
    departure_date = request.GET.get('departure_date', '')
    return_date = request.GET.get('return_date', '')
    passengers = request.GET.get('passengers', '1')
    seat_class = request.GET.get('seat_class', '')

    # Base queryset
    flights = FlightTicket.objects.all()
    return_flights = None

    # Apply filters
    if origin_id:
        flights = flights.filter(origin_id=origin_id)

    if destination_id:
        flights = flights.filter(destination_id=destination_id)

    if departure_date:
        departure_datetime = datetime.strptime(departure_date, '%Y-%m-%d')
        next_day = departure_datetime + timedelta(days=1)
        flights = flights.filter(
            departure_time__gte=departure_datetime,
            departure_time__lt=next_day
        )

    if seat_class:
        flights = flights.filter(seat_class=seat_class)

    # Get return flights if return date is provided
    if return_date and destination_id and origin_id:
        return_datetime = datetime.strptime(return_date, '%Y-%m-%d')
        next_day = return_datetime + timedelta(days=1)
        return_flights = FlightTicket.objects.filter(
            origin_id=destination_id,
            destination_id=origin_id,
            departure_time__gte=return_datetime,
            departure_time__lt=next_day
        )

        if seat_class:
            return_flights = return_flights.filter(seat_class=seat_class)

    # Get all locations for the filter dropdowns
    locations = Location.objects.all()

    context = {
        'flights': flights,
        'return_flights': return_flights,
        'locations': locations,
        'seat_classes': FlightTicket.SEAT_CLASS_CHOICES,
        'filters': {
            'origin_id': origin_id,
            'destination_id': destination_id,
            'departure_date': departure_date,
            'return_date': return_date,
            'passengers': passengers,
            'seat_class': seat_class,
        }
    }
    return render(request, 'home/flight_search.html', context)

def tour_search(request):
    # Get filter parameters
    location_id = request.GET.get('location', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    # Base queryset
    tours = Tour.objects.all()

    # Apply filters
    if location_id:
        tours = tours.filter(location_id=location_id)

    if min_price:
        tours = tours.filter(price__gte=min_price)

    if max_price:
        tours = tours.filter(price__lte=max_price)

    # Get all locations for the filter dropdown
    locations = Location.objects.all()

    # Get min and max prices for the price slider
    price_range = Tour.objects.aggregate(min_price=Min('price'), max_price=Max('price'))

    context = {
        'tours': tours,
        'locations': locations,
        'price_range': price_range,
        'filters': {
            'location_id': location_id,
            'min_price': min_price or price_range['min_price'],
            'max_price': max_price or price_range['max_price'],
        }
    }
    return render(request, 'home/tour_search.html', context)

def car_search(request):
    # Get filter parameters
    location_id = request.GET.get('location', '')
    car_type = request.GET.get('car_type', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    min_capacity = request.GET.get('min_capacity', '')

    # Base queryset
    cars = CarTransfer.objects.all()

    # Apply filters
    if location_id:
        cars = cars.filter(location_id=location_id)

    if car_type:
        cars = cars.filter(car_type=car_type)

    if min_price:
        cars = cars.filter(price__gte=min_price)

    if max_price:
        cars = cars.filter(price__lte=max_price)

    if min_capacity:
        cars = cars.filter(capacity__gte=min_capacity)

    # Get all locations for the filter dropdown
    locations = Location.objects.all()

    # Get min and max prices for the price slider
    price_range = CarTransfer.objects.aggregate(min_price=Min('price'), max_price=Max('price'))

    context = {
        'cars': cars,
        'locations': locations,
        'car_types': CarTransfer.CAR_TYPE_CHOICES,
        'price_range': price_range,
        'filters': {
            'location_id': location_id,
            'car_type': car_type,
            'min_price': min_price or price_range['min_price'],
            'max_price': max_price or price_range['max_price'],
            'min_capacity': min_capacity,
        }
    }
    return render(request, 'home/car_search.html', context)

def promotions(request):
    active_promotions = Promotion.objects.filter(
        is_active=True,
        end_date__gt=timezone.now()
    ).order_by('end_date')

    context = {
        'promotions': active_promotions,
    }
    return render(request, 'home/promotions.html', context)

def apply_promotion(request):
    if request.method == 'POST' and request.is_ajax():
        promo_code = request.POST.get('promo_code')
        item_type = request.POST.get('item_type')
        item_price = float(request.POST.get('item_price', 0))

        try:
            promotion = Promotion.objects.get(
                promo_code=promo_code,
                is_active=True,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            )

            # Check if promotion applies to this item type
            if promotion.promotion_type not in [item_type, 'general']:
                return JsonResponse({
                    'success': False,
                    'message': 'Mã khuyến mãi không áp dụng cho loại dịch vụ này.'
                })

            # Calculate discount
            if promotion.discount_percent > 0:
                discount = item_price * (promotion.discount_percent / 100)
                new_price = item_price - discount
                message = f'Giảm {promotion.discount_percent}%'
            elif promotion.discount_amount > 0:
                discount = promotion.discount_amount
                new_price = item_price - discount
                message = f'Giảm {int(discount):,} VND'
            else:
                discount = 0
                new_price = item_price
                message = 'Không có giảm giá'

            return JsonResponse({
                'success': True,
                'discount': discount,
                'new_price': new_price,
                'message': message
            })

        except Promotion.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Mã khuyến mãi không hợp lệ hoặc đã hết hạn.'
            })

    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == 'POST':
        # Process payment (in a real app, this would integrate with a payment gateway)
        payment_method = request.POST.get('payment_method')

        # Update booking status
        booking.status = 'confirmed'
        booking.save()

        messages.success(request, 'Thanh toán thành công! Đặt phòng của bạn đã được xác nhận.')
        return redirect('home:orders')

    context = {
        'booking': booking,
    }
    return render(request, 'home/payment.html', context)

def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    hotel = room.hotel

    # Get other rooms from the same hotel
    related_rooms = Room.objects.filter(hotel=hotel, is_available=True).exclude(id=room_id)[:3]

    context = {
        'room': room,
        'hotel': hotel,
        'related_rooms': related_rooms,
    }
    return render(request, 'home/room_detail.html', context)