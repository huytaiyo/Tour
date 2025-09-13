from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

class Location(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='locations/', blank=True, null=True)
    is_popular = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Hotel(models.Model):
    STAR_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    name = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='hotels')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Starting price for rooms")
    rating = models.FloatField(default=0)
    stars = models.IntegerField(choices=STAR_CHOICES, default=3)
    address = models.CharField(max_length=255, blank=True)
    amenities = models.TextField(blank=True, help_text="Comma-separated list of amenities")
    is_featured = models.BooleanField(default=False)

    def get_amenities_list(self):
        return [amenity.strip() for amenity in self.amenities.split(',') if amenity.strip()]

    def get_cheapest_room(self):
        rooms = self.rooms.all()
        if rooms:
            return rooms.order_by('price').first()
        return None

    def __str__(self):
        return self.name

class Room(models.Model):
    ROOM_TYPE_CHOICES = [
        ('standard', 'Standard Room'),
        ('deluxe', 'Deluxe Room'),
        ('suite', 'Suite'),
        ('family', 'Family Room'),
        ('executive', 'Executive Room'),
        ('villa', 'Villa'),
    ]

    BED_TYPE_CHOICES = [
        ('single', 'Single Bed'),
        ('twin', 'Twin Beds'),
        ('double', 'Double Bed'),
        ('queen', 'Queen Bed'),
        ('king', 'King Bed'),
    ]

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=200)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, default='standard')
    bed_type = models.CharField(max_length=20, choices=BED_TYPE_CHOICES, default='single')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField(default=2, help_text="Maximum number of guests")
    size = models.IntegerField(default=0, help_text="Room size in square meters")
    services = models.TextField(blank=True, help_text="Comma-separated list of services")
    is_available = models.BooleanField(default=True)

    # Basic amenities
    is_non_smoking = models.BooleanField(default=True, help_text="Non-smoking room")
    has_waiting_area = models.BooleanField(default=False, help_text="Has waiting area")

    # Room amenities
    has_air_conditioning = models.BooleanField(default=True, help_text="Has air conditioning")
    has_mini_bar = models.BooleanField(default=False, help_text="Has mini bar")
    has_free_bottled_water = models.BooleanField(default=True, help_text="Provides free bottled water")
    has_refrigerator = models.BooleanField(default=False, help_text="Has refrigerator")
    has_tv = models.BooleanField(default=True, help_text="Has TV")
    has_desk = models.BooleanField(default=True, help_text="Has desk")

    # Bathroom amenities
    has_hot_water = models.BooleanField(default=True, help_text="Has hot water")
    has_private_bathroom = models.BooleanField(default=True, help_text="Has private bathroom")
    has_shower = models.BooleanField(default=True, help_text="Has shower")
    has_toiletries = models.BooleanField(default=True, help_text="Provides toiletries")
    has_bathtub = models.BooleanField(default=False, help_text="Has bathtub")
    has_hair_dryer = models.BooleanField(default=False, help_text="Has hair dryer")
    has_bathrobes = models.BooleanField(default=False, help_text="Provides bathrobes")

    def get_services_list(self):
        return [service.strip() for service in self.services.split(',') if service.strip()]

    def __str__(self):
        return f"{self.name} - {self.hotel.name}"

class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='rooms/')

    def __str__(self):
        return f"Image for {self.room.name} in {self.room.hotel.name}"

class HotelImage(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='hotels/')

    def __str__(self):
        return f"Image for {self.hotel.name}"

class FlightTicket(models.Model):
    SEAT_CLASS_CHOICES = [
        ('economy', 'Economy'),
        ('premium_economy', 'Premium Economy'),
        ('business', 'Business'),
        ('first', 'First Class'),
    ]
    flight_number = models.CharField(max_length=50)
    airline = models.CharField(max_length=100, default="Unknown Airline")
    airline_logo = models.ImageField(upload_to='airlines/', blank=True, null=True)
    origin = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='departing_flights')
    destination = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='arriving_flights')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField(default=0)
    available_seats = models.IntegerField(default=100)
    seat_class = models.CharField(max_length=20, choices=SEAT_CLASS_CHOICES, default='economy')
    is_featured = models.BooleanField(default=False)

    def get_duration(self):
        duration = self.arrival_time - self.departure_time
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{int(hours)}h {int(minutes)}m"

    def __str__(self):
        return f"{self.flight_number} from {self.origin} to {self.destination}"

class Tour(models.Model):
    name = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='tours')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50, help_text="e.g., '3 days, 2 nights'")
    included_services = models.TextField(blank=True, help_text="Comma-separated list of included services")
    rating = models.FloatField(default=0)
    is_featured = models.BooleanField(default=False)

    def get_included_services_list(self):
        return [service.strip() for service in self.included_services.split(',') if service.strip()]

    def __str__(self):
        return f"{self.name} - {self.location.name}"

class TourImage(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='tours/')

    def __str__(self):
        return f"Image for {self.tour.name}"

class CarTransfer(models.Model):
    CAR_TYPE_CHOICES = [
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('van', 'Van'),
        ('luxury', 'Luxury'),
    ]
    name = models.CharField(max_length=200)
    car_type = models.CharField(max_length=20, choices=CAR_TYPE_CHOICES, default='sedan')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='car_transfers')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField(default=4)
    image = models.ImageField(upload_to='cars/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.car_type}) - {self.location.name}"

class Promotion(models.Model):
    PROMOTION_TYPE_CHOICES = [
        ('hotel', 'Hotel'),
        ('flight', 'Flight'),
        ('tour', 'Tour'),
        ('car', 'Car Transfer'),
        ('general', 'General'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    discount_percent = models.IntegerField(default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    promo_code = models.CharField(max_length=50, unique=True,null=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now() + datetime.timedelta(days=30))
    image = models.ImageField(upload_to='promotions/', default='promotions/default.jpg')
    promotion_type = models.CharField(max_length=20, choices=PROMOTION_TYPE_CHOICES, default='general')
    is_active = models.BooleanField(default=True)

    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    def get_remaining_days(self):
        now = timezone.now()
        if now > self.end_date:
            return 0
        return (self.end_date - now).days

    def __str__(self):
        return f"{self.title} ({self.promo_code})"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

class Booking(models.Model):
    BOOKING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    booking_type = models.CharField(max_length=20, choices=[
        ('hotel', 'Hotel'), 
        ('flight', 'Flight'),
        ('tour', 'Tour'),
        ('car', 'Car Transfer')
    ])
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, blank=True, null=True)
    flight = models.ForeignKey(FlightTicket, on_delete=models.CASCADE, blank=True, null=True)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, blank=True, null=True)
    car = models.ForeignKey(CarTransfer, on_delete=models.CASCADE, blank=True, null=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    check_in_date = models.DateField(blank=True, null=True)
    check_out_date = models.DateField(blank=True, null=True)
    number_of_guests = models.IntegerField(default=1)
    special_requests = models.TextField(blank=True)
    promotion = models.ForeignKey(Promotion, on_delete=models.SET_NULL, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending')

    def __str__(self):
        if self.booking_type == 'hotel' and self.hotel:
            return f"Booking by {self.user} for hotel {self.hotel.name}"
        elif self.booking_type == 'flight' and self.flight:
            return f"Booking by {self.user} for flight {self.flight.flight_number}"
        elif self.booking_type == 'tour' and self.tour:
            return f"Booking by {self.user} for tour {self.tour.name}"
        elif self.booking_type == 'car' and self.car:
            return f"Booking by {self.user} for car {self.car.name}"
        else:
            return f"Booking by {self.user}"