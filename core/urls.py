from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_document, name='upload_document'),
    path('query/', views.query_document, name='query_document'),  # Add this line for the query view
]
