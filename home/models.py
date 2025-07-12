from django.db import models
from django.contrib.auth.models import User

class Location(models.Model):
    name = models.CharField(max_length=100)
    description= models.TextField(blank=True)

    def __str__(self):
        return self.name

class Hotel(models.Model):
    name= models.CharField(max_length=200)
    location =  models.ForeignKey(Location, on_delete=models.CASCADE, related_name='hotels')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.name
    
class HotelImage(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='hotels/')

    def __str__(self):
        return f"Image for {self.hotel.name}"
    
class FlightTicket(models.Model):
    flight_number = models.CharField(max_length=50)
    origin = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='departing_flights')
    destination =models.ForeignKey(Location, on_delete=models.CASCADE, related_name='arriving_flights')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField(default=0)

    def __str__(self):
        return f"{self.flight_number} from {self.origin} to {self.destination}"
    
class Booking (models.Model):
    BOOKING_STATUS_CHOICES = [
        ('pending', 'PENDING'),
        ('confirmed','Confirmed'),
        ('cancelled','Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete= models.CASCADE, related_name='bookings')
    booking_type = models.CharField(max_length=20, choices=[('hotel','Hotel'),('flight','Flight')])
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, blank=True, null = True)
    flight =  models.ForeignKey(FlightTicket, on_delete=models.CASCADE, blank=True, null = True)
    booking_date = models.DateTimeField(auto_now_add = True)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default= ' pending ')

    def __str__(self):
        if self.booking_type == 'hotel' and self.hotel:
            return f"Booking by {self.user} for hotel (self.hotel.name)"
        elif self.booking_type == 'flight' and self.flight:
            return f"Booking by {self.user} for flight (self.flight.flight_name)"
        else:
            return f"Booking by {self.user}"
        