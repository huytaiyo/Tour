from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('detail/<str:item_type>/<int:item_id>/', views.detail, name='detail'),
    path('booking/<str:item_type>/<int:item_id>/', views.booking, name='booking'),

    # User authentication and profile
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    path('profile/', views.user_profile, name='profile'),
    path('orders/', views.user_orders, name='orders'),

    # Specialized search pages
    path('hotels/', views.hotel_search, name='hotel_search'),
    path('flights/', views.flight_search, name='flight_search'),
    path('tours/', views.tour_search, name='tour_search'),
    path('cars/', views.car_search, name='car_search'),

    # Promotions
    path('promotions/', views.promotions, name='promotions'),
    path('apply-promotion/', views.apply_promotion, name='apply_promotion'),
]