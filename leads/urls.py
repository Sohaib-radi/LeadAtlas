from django.urls import path

from . import views

app_name = "leads"

urlpatterns = [
    path("", views.home, name="home"),
    path("leads/", views.business_list, name="business_list"),
    path("leads/export/", views.export_csv, name="export_csv"),
    path("leads/<int:pk>/", views.business_detail, name="business_detail"),
    path("searches/", views.search_list, name="search_list"),
    path("searches/<int:pk>/", views.search_detail, name="search_detail"),
    path("searches/<int:pk>/rerun/", views.search_rerun, name="search_rerun"),
]
