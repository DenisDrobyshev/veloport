from django.urls import path

from . import views

app_name = "content"

urlpatterns = [
    path("", views.blog_list, name="blog"),
    path("guides/", views.guides, name="guides"),
    path("page/<slug:slug>/", views.page_detail, name="page"),
    path("<slug:slug>/", views.article_detail, name="article"),
]
