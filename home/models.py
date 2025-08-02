from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

class Location(models.Model):
    name = models.CharField(max_length=100)
    description= models.TextField(blank=True)
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
    
    name= models.CharField(max_length=200)
    location =  models.ForeignKey(Location, on_delete=models.CASCADE, related_name='hotels')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField(default=0)
    star_rating = models.IntegerField(choices=STAR_CHOICES, default=3)
    address = models.CharField(max_length=255, blank=True)
    amenities = models.TextField(blank=True, help_text="Comma-separated list of amenities")
    is_featured = models.BooleanField(default=False)

    def get_amenities_list(self):
        return [amenity.strip() for amenity in self.amenities.split(',') if amenity.strip()]

    def __str__(self):
        return self.name

    
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
    airline = models.CharField(max_length=100, default='Unknown Airline')
    airline_logo = models.ImageField(upload_to='airlines/', blank=True, null=True)
    origin = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='departing_flights')
    destination =models.ForeignKey(Location, on_delete=models.CASCADE, related_name='arriving_flights')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField(default=0)
    available_seats = models.IntegerField(default=0)
    seat_class = models.CharField(max_length=20, choices=SEAT_CLASS_CHOICES, default='economy')
    is_featured = models.BooleanField(default=False)

    def get_duration(self):
        duaration = self.arrival_time - self.departure_time
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{int(hours)}h {int(minutes)}m"

    def __str__(self):
        return f"{self.flight_number} from {self.origin} to {self.destination}"
    
class Booking (models.Model):
    BOOKING_STATUS_CHOICES = [
        ('pending', 'PENDING'),
        ('confirmed','Confirmed'),
        ('cancelled','Cancelled'),
        ('completed', 'Completed'),
        
    ]
    user = models.ForeignKey(User, on_delete= models.CASCADE, related_name='bookings')
    booking_type = models.CharField(max_length=20, choices=[
        ('hotel','Hotel'),
        ('flight','Flight'),
        ('tour','Tour'),
        ('car_transfer','Car Transfer'),
        ])
     
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, blank=True, null = True)
    flight =  models.ForeignKey(FlightTicket, on_delete=models.CASCADE, blank=True, null = True)
    booking_date = models.DateTimeField(auto_now_add = True)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default= ' pending ')
    tour = models.ForeignKey('Tour', on_delete=models.CASCADE, blank=True, null=True)
    check_in_date = models.DateTimeField(blank=True, null=True)
    check_out_date = models.DateTimeField(blank=True, null=True)
    number_of_guests = models.IntegerField(default=1)
    special_requests = models.TextField(blank=True)
    promotion = models.ForeignKey('Promotion', on_delete=models.SET_NULL, blank=True, null=True)
    car = models.ForeignKey('CarTransfer', on_delete=models.CASCADE, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending')
    def __str__(self):
        if self.booking_type == 'hotel' and self.hotel:
            return f"Booking by {self.user} for hotel {self.hotel.name}"
        elif self.booking_type == 'flight' and self.flight:
            return f"Booking by {self.user} for flight {self.flight.flight_name}"
        elif self.booking_type == 'tour' and self.tour:
            return f"Booking by {self.user} for tour {self.tour.name}"
        elif self.booking_type == 'car' and self.car:
            return f"Booking by {self.user} for car transfer {self.car.name}"
        else:
            return f"Booking by {self.user}"

class Tour(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(help_text="Duration in days")
    rating = models.FloatField(default=0)
    included_services = models.TextField(blank=True, help_text="Comma-separated list of included services")
    is_featured = models.BooleanField(default=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='tours')

    def get_included_services_list(self):
        return [amenity.strip() for amenity in self.amenities.split(',') if amenity.strip()]

    def __str__(self):
        return f"{self.name} ({self.location.name})"
    
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
    car_type = models.CharField(max_length=100, default='sedan', choices=CAR_TYPE_CHOICES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField(default=1)
    image = models.ImageField(upload_to='car_transfers/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='car_transfers')


    def __str__(self):
        return f"{self.name} ({self.car_type}) - {self.location.name}"

class Promotion(models.Model):
    PROMOTION_TYPE_CHOICES = [
        ('hotel', 'Hotel'),
        ('flight', 'Flight'),
        ('tour', 'Tour'),
        ('car_transfer', 'Car Transfer'),
        ('general', 'General'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    discount_percent = models.IntegerField(default=0)
    promotion_type = models.CharField(max_length=20, choices=PROMOTION_TYPE_CHOICES)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    promo_code = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='promotions/', blank=True, null=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now()+ timezone.timedelta(days=30))
    is_active = models.BooleanField(default=True)

    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    def get_remanining_days(self):
        now = timezone.now()
        if now > self.end_date:
            return 0
        return (self.end_date - now).days

    def __str__(self):
        return f"{self.title} ({self.promo_code})"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"    