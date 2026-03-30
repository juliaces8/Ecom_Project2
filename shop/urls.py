from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='shop/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('dashboard/add/', views.add_product, name='add_product'),
    path('product/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('product/delete/<int:pk>/', views.delete_product,
         name='delete_product'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/update/<int:product_id>/<str:action>/', views.update_cart,
         name='update_cart'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/review/', views.add_review,
         name='add_review'),
    path('vendor/store/add/', views.add_store, name='add_store'),
    path('vendor/store/edit/<int:pk>/', views.edit_store, name='edit_store'),
    path('vendor/store/delete/<int:pk>/', views.delete_store,
         name='delete_store'),
    path('vendor/reviews/', views.vendor_review_list,
         name='vendor_review_list'),
    path('api/stores/', views.StoreListCreateAPI.as_view(), name='api-stores'),
    path('api/stores/<int:pk>/', views.StoreDetailAPI.as_view(),
         name='api-store-detail'),
    path('api/products/', views.ProductListCreateAPI.as_view(),
         name='api-products'),
    path('api/reviews/', views.ReviewListAPI.as_view(), name='api-reviews'),
]
