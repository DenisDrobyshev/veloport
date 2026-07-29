from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("compare/", views.compare, name="compare"),
    path("compare/add/<int:product_id>/", views.compare_add, name="compare_add"),
    path("compare/remove/<int:product_id>/", views.compare_remove, name="compare_remove"),
    path("compare/clear/", views.compare_clear, name="compare_clear"),
    path("fit/", views.fit_finder, name="fit_finder"),
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("wishlist/toggle/<int:product_id>/", views.wishlist_toggle, name="wishlist_toggle"),
    path("subscribe/", views.subscribe, name="subscribe"),
    path("contacts/", views.contacts, name="contacts"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
