from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.catalog.models import Brand, Category, Product

from .forms import STYLE_TO_CATEGORY, FitFinderForm, SubscriberForm
from .models import Banner


def home(request):
    products = (
        Product.objects.active()
        .select_related("brand")
        .prefetch_related("images", "bike")
    )
    velo = Category.objects.filter(slug="velosipedy").first()
    bike_categories = velo.get_children().filter(is_active=True) if velo else Category.objects.none()

    context = {
        "banners": Banner.objects.filter(is_active=True),
        "featured": products.filter(is_featured=True)[:8],
        "new_arrivals": products.filter(is_new=True)[:8],
        "bestsellers": products.filter(is_bestseller=True)[:8],
        "discounted": products.with_discount()[:8],
        "bike_categories": bike_categories,
        "categories": Category.objects.filter(is_active=True, level=0),
        "brands": Brand.objects.filter(is_active=True, is_featured=True)[:12],
        "recent": recent_products(request, limit=8),
    }
    return render(request, "core/home.html", context)


# --- Сравнение товаров ---

def _compare_ids(request):
    return request.session.get(settings.COMPARE_SESSION_ID, [])


def _save_compare_ids(request, ids):
    request.session[settings.COMPARE_SESSION_ID] = ids
    request.session.modified = True


def compare(request):
    ids = _compare_ids(request)
    products = list(
        Product.objects.filter(id__in=ids)
        .select_related("brand", "category")
        .prefetch_related("bike", "images")
    )
    products.sort(key=lambda p: ids.index(p.id))

    # строки сравнения по велоспецификациям
    rows = []
    if products:
        def bike_attr(p, getter):
            b = getattr(p, "bike", None)
            return getter(b) if b else "—"

        rows = [
            ("Цена", [f"{int(p.price)} ₽" for p in products]),
            ("Бренд", [p.brand.name if p.brand else "—" for p in products]),
            ("Категория", [p.category.name for p in products]),
            ("Размер колёс", [bike_attr(p, lambda b: b.get_wheel_size_display() or "—") for p in products]),
            ("Материал рамы", [bike_attr(p, lambda b: b.get_frame_material_display() or "—") for p in products]),
            ("Ростовка", [bike_attr(p, lambda b: b.get_frame_size_display() or "—") for p in products]),
            ("Тормоза", [bike_attr(p, lambda b: b.get_brake_type_display() or "—") for p in products]),
            ("Амортизация", [bike_attr(p, lambda b: b.get_suspension_display() or "—") for p in products]),
            ("Скоростей", [bike_attr(p, lambda b: b.speeds) for p in products]),
            ("Вес, кг", [bike_attr(p, lambda b: b.weight_kg or "—") for p in products]),
            ("Рейтинг", [f"{p.rating} ★" for p in products]),
        ]
    return render(request, "core/compare.html", {"products": products, "rows": rows})


@require_POST
def compare_add(request, product_id):
    ids = _compare_ids(request)
    if product_id not in ids:
        if len(ids) >= 4:
            ids.pop(0)
        ids.append(product_id)
    _save_compare_ids(request, ids)
    if request.htmx:
        return render(request, "core/_compare_toggle.html",
                      {"product_id": product_id, "in_compare": True, "count": len(ids)})
    return redirect("core:compare")


@require_POST
def compare_remove(request, product_id):
    ids = _compare_ids(request)
    if product_id in ids:
        ids.remove(product_id)
    _save_compare_ids(request, ids)
    if request.htmx:
        return redirect("core:compare")
    return redirect("core:compare")


@require_POST
def compare_clear(request):
    _save_compare_ids(request, [])
    return redirect("core:compare")


# --- Умный подборщик велосипеда ---

def _recommend_size(height: int) -> str:
    table = [
        (150, "XS"), (160, "S"), (170, "S/M"), (178, "M"),
        (186, "L"), (195, "XL"), (999, "XXL"),
    ]
    for max_h, size in table:
        if height < max_h:
            return size
    return "XL"


def fit_finder(request):
    form = FitFinderForm(request.GET or None)
    results = None
    recommended_size = None

    if request.GET and form.is_valid():
        height = form.cleaned_data["height"]
        style = form.cleaned_data["style"]
        budget = form.cleaned_data["budget"]

        qs = (
            Product.objects.active()
            .filter(product_type__in=[Product.TYPE_BIKE, Product.TYPE_EBIKE])
            .select_related("brand")
            .prefetch_related("images", "bike")
        )

        if style == "electro":
            qs = qs.filter(bike__is_electric=True)
        elif slug := STYLE_TO_CATEGORY.get(style):
            cat = Category.objects.filter(slug=slug).first()
            if cat:
                qs = qs.filter(category__in=cat.get_descendants(include_self=True))

        lo, hi = budget.split("-")
        if lo != "0":
            qs = qs.filter(price__gte=lo)
        if hi != "0":
            qs = qs.filter(price__lte=hi)

        # фильтр по подходящему росту (если данные заполнены)
        qs = qs.filter(
            Q(bike__rider_height_min__isnull=True) | Q(bike__rider_height_min__lte=height),
            Q(bike__rider_height_max__isnull=True) | Q(bike__rider_height_max__gte=height),
        )

        recommended_size = _recommend_size(height)
        results = list(qs.distinct()[:12])

    return render(
        request,
        "core/fit_finder.html",
        {"form": form, "results": results, "recommended_size": recommended_size},
    )


# --- Подписка ---

@require_POST
def subscribe(request):
    form = SubscriberForm(request.POST)
    if form.is_valid():
        form.save()
        msg = "Спасибо за подписку! 🎉"
    elif "email" in form.errors and Subscriber_exists(request.POST.get("email")):
        msg = "Вы уже подписаны 🙌"
    else:
        msg = "Проверьте, пожалуйста, email"
    if request.htmx:
        return HttpResponse(f'<p class="text-sm text-white/90">{msg}</p>')
    return redirect("core:home")


def Subscriber_exists(email):
    from .models import Subscriber
    return Subscriber.objects.filter(email=email).exists()


def contacts(request):
    from apps.stores.models import Store
    return render(request, "core/contacts.html", {"stores": Store.objects.filter(is_active=True)})


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /cart/",
        "Disallow: /order/",
        "Disallow: /account/",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


# --- Избранное (wishlist) ---

def _wishlist_ids(request):
    return request.session.get(settings.WISHLIST_SESSION_ID, [])


@require_POST
def wishlist_toggle(request, product_id):
    ids = _wishlist_ids(request)
    if product_id in ids:
        ids.remove(product_id)
        added = False
    else:
        ids.append(product_id)
        added = True
    request.session[settings.WISHLIST_SESSION_ID] = ids
    request.session.modified = True
    product = get_object_or_404(Product, id=product_id)
    if request.htmx:
        return render(request, "core/_wishlist_button.html", {"product": product, "in_wishlist": added})
    return redirect(request.META.get("HTTP_REFERER") or "core:home")


def wishlist_view(request):
    ids = _wishlist_ids(request)
    products = Product.objects.filter(id__in=ids).select_related("brand").prefetch_related("images")
    by_id = {p.id: p for p in products}
    ordered = [by_id[i] for i in ids if i in by_id]
    return render(request, "core/wishlist.html", {"products": ordered})


# --- Недавно просмотренные ---

def push_recent(request, product_id):
    ids = request.session.get(settings.RECENT_SESSION_ID, [])
    ids = [product_id] + [i for i in ids if i != product_id]
    request.session[settings.RECENT_SESSION_ID] = ids[:12]
    request.session.modified = True


def recent_products(request, exclude_id=None, limit=8):
    ids = [i for i in request.session.get(settings.RECENT_SESSION_ID, []) if i != exclude_id]
    products = Product.objects.filter(id__in=ids).select_related("brand").prefetch_related("images")
    by_id = {p.id: p for p in products}
    return [by_id[i] for i in ids if i in by_id][:limit]
