from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path("add/<int:product_id>/", views.add_review, name="add_review"),
    path("question/<int:product_id>/", views.add_question, name="add_question"),
    path("like/<int:review_id>/", views.like_review, name="like"),
]
