from django.contrib import admin
from django.urls import path,include
from .views import *


urlpatterns = [
    path('clients/', ClientListCreateAPIView.as_view(), name='client-list-create'),
    path('clients/<int:id>/', ClientRetrieveUpdateDestroyAPIView.as_view(), name='client-retrieve-update-destroy'),
    path('clients/<int:id>/projects/', ProjectCreateAPIView.as_view(), name='project-create'),
    path('projects/', ProjectListAPIView.as_view(), name='project-list'),
    
]