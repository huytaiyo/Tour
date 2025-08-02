from django.contrib import admin
from django.utils.html import format_html
from .models import Location, Hotel, HotelImage, FlightTicket, Booking, Tour, CarTransfer, Promotion, TourImage, UserProfile 

class ImagePreviewMixin:
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:100px;"/>', obj.image.url)
        return ""
    image_preview.short_description = 'Image Preview'

class HotelImageInline(admin.TabularInline,ImagePreviewMixin):
    model = HotelImage
    extra =1
    readonly_fields = ('image_preview',)

class TourImageInline(admin.TabularInline,ImagePreviewMixin):
    model = TourImage
    extra = 1
    readonly_fields = ('image_preview',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name','is_popular', 'image_preview')
    search_fields = ('name',)
    list_filter = ('is_popular','description',)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:100px;"/>', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'
    
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display  = ('name','location','price','rating', 'is_featured', 'stars')
    list_filter = ('location', 'is_featured', 'stars')
    search_fields = ('name', 'location__name', 'address')
    inlines = [HotelImageInline]
    list_editable = ('is_featured',)
    fieldsets = (
        (None, {
            'fields': ('name', 'location', 'description', 'price', 'rating',)
        }),
        ('Details', {
            'fields': ('stars', 'address', 'amenities', 'is_featured')
        }),
    )
@admin.register(FlightTicket)
class FlightTicketAdmin(admin.ModelAdmin):
    list_display  = ('flight_number','origin','destination','departure_time','arrival_time','price','rating')
    list_filter = ('origin','destination'   , 'seat_class', 'is_featured')
    search_fields = ('flight_number','origin__name','destination__name' , 'airline')
    list_editable = ('is_featured',)
    date_hierarchy = 'departure_time'
    fieldsets = (
        (None, {
            'fields': ('flight_number', 'airline', 'origin', 'destination','airline_logo','airline_logo_preview' )
        }),
        ('Schedule', {
            'fields': ('departure_time', 'arrival_time')
        }),
        ('Details', {
            'fields': ('price', 'rating', 'available_seats', 'seat_class', 'is_featured')
        }),
    )
    readonly_fields = ('airline_logo_preview',)

    def airline_logo_preview(self, obj):
        if obj.airline_logo:
            return format_html('<img src="{}" style="max-height:100px;"/>', obj.airline_logo.url)
        return "No Logo"
    airline_logo_preview.short_description = 'Airline Logo '

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display  = ('user','booking_type','flight','booking_date','status', 'get_item_name', 'check_in_date', 'check_out_date', 'total_price')
    list_filter = ('booking_type','status','booking_date')
    search_fields = ('user__username',  'flight__flight_number', 'hotel__name', 'tour__name', 'car__name')
    date_hierarchy = 'booking_date'
    readonly_fields = ('total_price',)

    def get_item_name(self, obj):
        if obj.booking_type == 'hotel' and obj.hotel:
            return obj.hotel.name
        elif obj.booking_type == 'flight' and obj.flight:
            return f"{obj.flight.flight_number} {obj.flight.origin} to {obj.flight.destination}"
        elif obj.booking_type == 'tour' and obj.tour:
            return obj.tour.name
        elif obj.booking_type == 'car_transfer' and obj.car:
            return obj.car.name
        return "-"
    get_item_name.short_description = 'Item'


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'price', 'rating', 'is_featured', 'duration')
    list_filter = ('location', 'is_featured')
    search_fields = ('name', 'location__name', 'description')
    inlines = [TourImageInline]
    list_editable = ('is_featured',)
    fieldsets = (
        (None, {
            'fields': ('name', 'location', 'description', 'price', 'rating')
        }),
        ('Details', {
            'fields': ('is_featured', 'rating', 'included_services',)
        }),
    )
 
@admin.register(CarTransfer)
class CarTransferAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'price', 'is_featured' , 'image_preview', 'car_type', 'capacity')
    list_filter = ('car_type', 'location', 'is_featured')
    search_fields = ('name', 'location__name', 'description')
    list_editable = ('is_featured',)
    fieldsets = (
        (None, {
            'fields': ('name', 'location', 'description', 'price', 'rating')
        }),
        ('Details', {
            'fields': ('is_featured',)
        }),
    )

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'promo_code', 'discount_percentage', 'promotion_start', 'discount_amount')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title','description', 'promo_code')
    readonly_fields = ('image_preview', 'is_valid', 'get_remaining_days')
    list_editable = ('is_active',)
    date_hierarchy = 'end_date'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:100px;"/>', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image Preview'

    def is_valid(self, obj):
        return obj.is_valid()
    is_valid.boolean = True
    is_valid.short_description = 'Is Valid'

    def get_remaining_days(self, obj):
       return obj.get_remaining_days()
    get_remaining_days.short_description = 'Remaining Days'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):   
    list_display = ('user', 'phone_number', 'address', 'profile_picture_preview')
    search_fields = ('user__username', 'phone_number', 'address')
    readonly_fields = ('profile_picture_preview',)

    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" style="max-height:100px;"/>', obj.profile_picture.url)
        return "No Profile Picture"
    profile_picture_preview.short_description = 'Profile Picture Preview'