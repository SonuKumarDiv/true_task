"""parking_bud URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  #path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  #path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, #path
    2. Add a URL to urlpatterns:  #path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views

app_name='account'

urlpatterns = [
#librarian--------------------
path('login_librarian_api',views.login_labrarian_api.as_view(), name='login_librarian_api'),
path('logout_librarian_api',views.logout_labrarian_api.as_view(),name='logout_librarian_api'),
path('signup_librarian_api',views.signup_labrarian_api.as_view(),name='signup_librarian_api'),
]
