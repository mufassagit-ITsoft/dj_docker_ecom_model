from django.urls import path
from . import views

urlpatterns = [

    path('', views.store, name='store'),
    path('product/<slug:product_slug>/', views.product_info, name='product-info'),
    path('search/<slug:category_slug>/', views.list_category, name='list-category'),
    path('brand/<str:brand_name>/', views.list_brand, name='list-brand'),
    path('search-products/', views.search_products, name='search-products'),
    
]