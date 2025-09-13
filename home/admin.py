from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Location, Hotel, HotelImage, FlightTicket, Booking, Tour, TourImage,
    CarTransfer, Promotion, UserProfile, Room, RoomImage
)

class ImagePreviewMixin:
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
        return ""
    image_preview.short_description = 'Image Preview'

class HotelImageInline(admin.TabularInline, ImagePreviewMixin):
    model = HotelImage
    extra = 1
    readonly_fields = ('image_preview',)

class RoomImageInline(admin.TabularInline, ImagePreviewMixin):
    model = RoomImage
    extra = 1
    readonly_fields = ('image_preview',)

class RoomInline(admin.TabularInline):
    model = Room
    extra = 1
    fields = ('name', 'room_type', 'bed_type', 'price', 'capacity', 'is_available')

class TourImageInline(admin.TabularInline, ImagePreviewMixin):
    model = TourImage
    extra = 1
    readonly_fields = ('image_preview',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_popular', 'image_preview')
    list_filter = ('is_popular',)
    search_fields = ('name', 'description')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'stars', 'price', 'rating', 'is_featured')
    list_filter = ('location', 'stars', 'is_featured')
    search_fields = ('name', 'location__name', 'address')
    inlines = [HotelImageInline, RoomInline]
    list_editable = ('is_featured',)
    fieldsets = (
        (None, {
            'fields': ('name', 'location', 'description', 'price', 'rating')
        }),
        ('Details', {
            'fields': ('stars', 'address', 'amenities', 'is_featured')
        }),
    )

@admin.register(FlightTicket)
class FlightTicketAdmin(admin.ModelAdmin):
    list_display = ('flight_number', 'airline', 'origin', 'destination', 'departure_time', 'arrival_time', 'seat_class', 'price', 'is_featured')
    list_filter = ('origin', 'destination', 'seat_class', 'is_featured')
    search_fields = ('flight_number', 'airline', 'origin__name', 'destination__name')
    list_editable = ('is_featured',)
    date_hierarchy = 'departure_time'
    fieldsets = (
        (None, {
            'fields': ('flight_number', 'airline', 'airline_logo', 'airline_logo_preview', 'origin', 'destination')
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
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.airline_logo.url)
        return "No Logo"
    airline_logo_preview.short_description = 'Airline Logo'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'booking_type', 'get_item_name', 'booking_date', 'check_in_date', 'check_out_date', 'total_price', 'status')
    list_filter = ('booking_type', 'status', 'booking_date')
    search_fields = ('user__username', 'hotel__name', 'flight__flight_number', 'tour__name', 'car__name')
    date_hierarchy = 'booking_date'
    readonly_fields = ('total_price',)

    def get_item_name(self, obj):
        if obj.booking_type == 'hotel' and obj.hotel:
            return obj.hotel.name
        elif obj.booking_type == 'flight' and obj.flight:
            return f"{obj.flight.flight_number} ({obj.flight.origin} to {obj.flight.destination})"
        elif obj.booking_type == 'tour' and obj.tour:
            return obj.tour.name
        elif obj.booking_type == 'car' and obj.car:
            return obj.car.name
        return "-"
    get_item_name.short_description = 'Item'

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'price', 'duration', 'rating', 'is_featured')
    list_filter = ('location', 'is_featured')
    search_fields = ('name', 'location__name', 'description')
    list_editable = ('is_featured',)
    inlines = [TourImageInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'location', 'description', 'price', 'duration')
        }),
        ('Details', {
            'fields': ('included_services', 'rating', 'is_featured')
        }),
    )

@admin.register(CarTransfer)
class CarTransferAdmin(admin.ModelAdmin):
    list_display = ('name', 'car_type', 'location', 'capacity', 'price', 'is_featured', 'image_preview')
    list_filter = ('car_type', 'location', 'is_featured')
    search_fields = ('name', 'location__name', 'description')
    list_editable = ('is_featured',)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'promotion_type', 'promo_code', 'discount_percent', 'discount_amount', 'start_date', 'end_date', 'is_active', 'is_valid')
    list_filter = ('promotion_type', 'is_active')
    search_fields = ('title', 'description', 'promo_code')
    list_editable = ('is_active',)
    date_hierarchy = 'end_date'
    readonly_fields = ('image_preview', 'is_valid', 'get_remaining_days')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image Preview'

    def is_valid(self, obj):
        return obj.is_valid()
    is_valid.boolean = True
    is_valid.short_description = 'Is Valid'

    def get_remaining_days(self, obj):
        return obj.get_remaining_days()
    get_remaining_days.short_description = 'Remaining Days'

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'hotel', 'room_type', 'bed_type', 'price', 'capacity', 'is_available')
    list_filter = ('hotel', 'room_type', 'bed_type', 'is_available', 'has_bathtub', 'has_refrigerator', 'has_air_conditioning', 'has_hot_water')
    search_fields = ('name', 'hotel__name', 'description')
    inlines = [RoomImageInline]
    list_editable = ('is_available',)
    fieldsets = (
        (None, {
            'fields': ('hotel', 'name', 'room_type', 'bed_type', 'description')
        }),
        ('Details', {
            'fields': ('price', 'capacity', 'size', 'services', 'is_available')
        }),
        ('Basic Amenities', {
            'fields': ('is_non_smoking', 'has_waiting_area'),
            'classes': ('collapse',),
        }),
        ('Room Amenities', {
            'fields': ('has_air_conditioning', 'has_mini_bar', 'has_free_bottled_water', 
                      'has_refrigerator', 'has_tv', 'has_desk'),
            'classes': ('collapse',),
        }),
        ('Bathroom Amenities', {
            'fields': ('has_hot_water', 'has_private_bathroom', 'has_shower', 
                      'has_toiletries', 'has_bathtub', 'has_hair_dryer', 'has_bathrobes'),
            'classes': ('collapse',),
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address', 'profile_picture_preview')
    search_fields = ('user__username', 'user__email', 'phone_number', 'address')
    readonly_fields = ('profile_picture_preview',)

    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.profile_picture.url)
        return "No Image"
    profile_picture_preview.short_description = 'Profile Picture'