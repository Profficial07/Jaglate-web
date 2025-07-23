from django.urls import path
from . import views

urlpatterns = [
    path('', views.generate_qr_page, name='generate_qr_page'),
    path('generate/', views.generate_qr_codes, name='generate_qr_codes'),
    path('qr/<str:unique_key>/enter/', views.enter_message_page, name='enter_message'),
    path('qr/<str:unique_key>/save/', views.save_message, name='save_message'),
    path('qr/<str:unique_key>/display/', views.display_message_page, name='display_message'),
    path('qr/<str:unique_key>/download/', views.download_qr, name='download_qr'),
]