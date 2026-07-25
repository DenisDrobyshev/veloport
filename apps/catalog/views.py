from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Bike, Brand, Category, Product, StockNotification

SORT_OPTIONS = {
    "popular": ("-is_bestseller", "-rating", "-id"),
    "cheap": ("price", "id"),
    "expensive": ("-price", "-id"),
    "new": ("-created_at", "-id"),
    "rating": ("-rating", "-reviews_count"),
    "discount": ("-id",),  # спец-обработка ниже
}


def _apply_filters(request, products):
    """Применяет GET-фильтры к queryset товаров."""
    g = request.GET

    q = g.get("q", "").strip()
    if q:
        products = products.filter(
            Q(title__icontains=q)
            | Q(short_description__icontains=q)
            | Q(sku__icontains=q)
            | Q(brand__name__icontains=q)
        )

    if brands := g.getlist("brand_f"):
        products = products.filter(brand__slug__in=brands)

    if (pmin := g.get("price_min")):
        if pmin.isdigit():
            products = products.filter(price__gte=pmin)
    if (pmax := g.get("price_max")):
        if pmax.isdigit():
            products = products.filter(price__lte=pmax)

    # Велофасеты
    if wheels := g.getlist("wheel"):
        products = products.filter(bike__wheel_size__in=wheels)
    if materials := g.getlist("material"):
        products = products.filter(bike__frame_material__in=materials)
    if brakes := g.getlist("brake"):
        products = products.filter(bike__brake_type__in=brakes)
    if susp := g.getlist("suspension"):
        products = products.filter(bike__suspension__in=susp)
    if genders := g.getlist("gender"):
        products = products.filter(bike__gender__in=genders)
    if sizes := g.getlist("frame_size"):
        products = products.filter(bike__frame_size__in=sizes)

    if g.get("in_stock"):
        products = products.filter(stock_qty__gt=0)
    if g.get("discount"):
        products = products.with_discount()
    if g.get("electric"):
        products = products.filter(bike__is_electric=True)

    return products.distinct()


def _render_list(request, products, base_products, current_category=None, current_brand=None, title="Каталог"):
    products = _apply_filters(request, products)

    sort = request.GET.get("sort", "popular")
    products = products.order_by(*SORT_OPTIONS.get(sort, SORT_OPTIONS["popular"]))

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()

    available_brands = (
        Brand.objects.filter(products__in=base_products).distinct().order_by("name")
    )

    context = {
        "page_obj": page_obj,
        "products": page_obj.object_list,
        "total_count": paginator.count,
        "current_category": current_category,
        "current_brand": current_brand,
        "title": title,
        "querystring": querystring,
        "sort": sort,
        "available_brands": available_brands,
        "facets": {
            "wheels": Bike.WHEEL_SIZES,
            "materials": Bike.FRAME_MATERIALS,
            "brakes": Bike.BRAKE_TYPES,
            "suspensions": Bike.SUSPENSIONS,
            "genders": Bike.GENDERS,
            "frame_sizes": Bike.FRAME_SIZES,
        },
        "selected": {
            "brand_f": request.GET.getlist("brand_f"),
            "wheel": request.GET.getlist("wheel"),
            "material": request.GET.getlist("material"),
            "brake": request.GET.getlist("brake"),
            "suspension": request.GET.getlist("suspension"),
            "gender": request.GET.getlist("gender"),
            "frame_size": request.GET.getlist("frame_size"),
            "price_min": request.GET.get("price_min", ""),
            "price_max": request.GET.get("price_max", ""),
            "in_stock": request.GET.get("in_stock", ""),
            "discount": request.GET.get("discount", ""),
            "electric": request.GET.get("electric", ""),
            "q": request.GET.get("q", ""),
        },
    }

    if request.htmx:
        return render(request, "catalog/_grid_block.html", context)
    return render(request, "catalog/list.html", context)


def product_list(request):
    base = Product.objects.active().select_related("brand", "category").prefetch_related("images", "bike")
    return _render_list(request, base, base, title="Весь каталог")


def category_view(request, category):
    current = get_object_or_404(Category, slug=category, is_active=True)
    cats = current.get_descendants(include_self=True)
    base = (
        Product.objects.active()
        .filter(category__in=cats)
        .select_related("brand", "category")
        .prefetch_related("images", "bike")
    )
    return _render_list(request, base, base, current_category=current, title=current.name)


def brand_view(request, brand):
    current = get_object_or_404(Brand, slug=brand, is_active=True)
    base = (
        Product.objects.active()
        .filter(brand=current)
        .select_related("brand", "category")
        .prefetch_related("images", "bike")
    )
    return _render_list(request, base, base, current_brand=current, title=current.name)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("brand", "category").prefetch_related(
            "images", "variants", "specs", "reviews", "questions__answers", "stocks__store"
        ),
        slug=slug,
        is_active=True,
    )
    Product.objects.filter(pk=product.pk).update(views=F("views") + 1)

    spec_groups = {}
    for spec in product.specs.all():
        spec_groups.setdefault(spec.group, []).append(spec)

    reviews = product.reviews.filter(is_published=True).select_related("author")
    rating_dist = {i: 0 for i in range(5, 0, -1)}
    for r in reviews:
        rating_dist[r.rating] = rating_dist.get(r.rating, 0) + 1

    related = (
        Product.objects.active()
        .filter(category=product.category)
        .exclude(pk=product.pk)
        .select_related("brand")
        .prefetch_related("images")[:8]
    )

    bike = getattr(product, "bike", None)

    from apps.core.views import push_recent, recent_products

    context = {
        "product": product,
        "bike": bike,
        "spec_groups": spec_groups,
        "reviews": reviews,
        "rating_dist": rating_dist,
        "questions": product.questions.filter(is_published=True),
        "variants": product.variants.filter(is_active=True),
        "stocks": product.stocks.filter(qty__gt=0).select_related("store"),
        "related": related,
        "recent": recent_products(request, exclude_id=product.id, limit=8),
    }
    push_recent(request, product.id)
    return render(request, "catalog/product_detail.html", context)


def suggest(request):
    """Живой поиск (автоподсказки) для шапки."""
    q = request.GET.get("q", "").strip()
    products = []
    if len(q) >= 2:
        products = (
            Product.objects.active()
            .filter(Q(title__icontains=q) | Q(brand__name__icontains=q) | Q(sku__icontains=q))
            .select_related("brand")
            .prefetch_related("images")[:6]
        )
    return render(request, "catalog/_suggest.html", {"products": products, "q": q})


@require_POST
def stock_notify(request, product_id):
    """Подписка «сообщить о поступлении»."""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    email = request.POST.get("email", "").strip()
    if email:
        StockNotification.objects.get_or_create(product=product, email=email)
    if request.htmx:
        return render(request, "catalog/_notify_ok.html", {})
    messages.success(request, "Мы сообщим о поступлении товара")
    return redirect(product.get_absolute_url())
