from django.contrib import admin
from django.urls import path, include
from expenses.views_frontend import home
from expenses.views import convert_currency_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/convert/', convert_currency_view, name='convert_currency'),
    path('api/', include('expenses.urls')),
    path('', include('expenses.urls')),
]
