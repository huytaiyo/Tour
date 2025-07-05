from django.contrib import admin
from django.utils.html import format_html
from .models import Location, Hotel, HotelImage, FlightTicket, Booking

class HotelImageInline(admin.TabularInline):
    model = HotelImage
    extra =1
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<ing str="{}" style="max-height:100px;"/>', obj.image.url)
        return""
    image_preview.short_description = 'Image Preview'

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display  = ('name','location', ' price ', ' rating ')
    list_filter = {'location',}
    search_fields = ('flight_number', 'origin_name' , 'destination_name')
    inlines = [HotelImageInline]
@admin.register(FlightTicket)
class FlightTicketAdmin(admin.ModelAdmin):
    list_display  = ('flight_number','origin', ' destination ', ' departure_time ', 'arrival_time', 'price' , 'rating')
    list_filter = {'origin','destination'}
    search_fields = ('flight_number', 'origin_name' , 'destination_name')
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display  = ('user','Booking_type', ' flight ', ' booking_date ', 'status')
    list_filter = {'booking_type','status'}
    search_fields = ('user__username')



