"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth import views as django_auth_views  # LoginView/LogoutView з Django
from django.urls import path
from django.contrib import admin
from blog import views, auth_views


urlpatterns = [
    path("", views.home_view, name="home"),
 
    #Auth
    path("register/", auth_views.register_view, name="register"),
    path(
        "login/",
        django_auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path("logout/", django_auth_views.LogoutView.as_view(), name="logout"),
 
    #Profile
    path("profile/create/", auth_views.profile_create_view, name="profile_create"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit_view, name="profile_edit"),
 
    #Diary
    path("diary/", views.diary_view, name="diary"),
    path("diary/add/", views.diary_add_view, name="diary_add"),
    path("diary/<int:pk>/delete/", views.diary_delete_view, name="diary_delete"),
    # path("seed_database/", views.seed_database),
    
    # Search
    path("search/dish/<int:dish_id>", views.dish_detail),
    path("search/product/<int:product_id>", views.product_detail),
    path("search/", views.search_panel, name="search_panel"),
    
    # Admin
    path("admin/", admin.site.urls),
    
    # 404
    path("<path:rest>", views.error),
]
