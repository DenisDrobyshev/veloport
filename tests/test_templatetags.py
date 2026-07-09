from apps.core.templatetags.shop_extras import NBSP, icon, num, rub, stars


def test_rub():
    assert rub(45000) == f"45{NBSP}000{NBSP}₽"
    assert rub(None) is None


def test_num():
    assert num(1234567) == f"1{NBSP}234{NBSP}567"


def test_stars():
    assert stars(3) == "★★★☆☆"
    assert stars(5) == "★★★★★"
    assert stars(0) == "☆☆☆☆☆"


def test_icon():
    out = str(icon("cart"))
    assert out.startswith("<svg") and "</svg>" in out
    assert str(icon("unknown-name")).count("<path") == 0
