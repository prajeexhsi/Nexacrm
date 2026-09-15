from django.contrib import admin
from django.urls import path, include
from crmapp import views
urlpatterns=[path("admin/",admin.site.urls),path("",views.landing,name="landing"),path("login/",views.login_view,name="login"),path("register/",views.register_view,name="register"),path("logout/",views.logout_view,name="logout"),path("",include("crmapp.urls"))]
