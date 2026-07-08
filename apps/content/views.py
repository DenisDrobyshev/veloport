from django.db.models import F
from django.shortcuts import get_object_or_404, render

from .models import FAQ, Article, Page, SizeChart


def blog_list(request):
    articles = Article.objects.filter(is_published=True)
    active_category = request.GET.get("category")
    if active_category:
        articles = articles.filter(category=active_category)
    return render(
        request,
        "content/blog_list.html",
        {
            "articles": articles,
            "categories": Article.CATEGORIES,
            "active_category": active_category,
        },
    )


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    Article.objects.filter(pk=article.pk).update(views=F("views") + 1)
    similar = (
        Article.objects.filter(is_published=True, category=article.category)
        .exclude(pk=article.pk)[:3]
    )
    return render(request, "content/article.html", {"article": article, "similar": similar})


def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, is_published=True)
    return render(request, "content/page.html", {"page": page})


def guides(request):
    return render(
        request,
        "content/guides.html",
        {
            "charts": SizeChart.objects.all(),
            "faqs": FAQ.objects.filter(is_active=True),
        },
    )
