from services.marketplace import build_marketplace_links


def test_default_marketplace_links() -> None:
    links = build_marketplace_links()

    assert links == {
        "Wildberries": "https://www.wildberries.ru/brands/zibelino",
        "Ozon": "https://www.ozon.ru/brand/zibelino-78161518/",
        "Yandex Market": "https://market.yandex.ru/business–zibelino/840751",
    }


def test_personalized_marketplace_links() -> None:
    links = build_marketplace_links("Apple", "iPhone 15 Pro")

    assert links == {
        "Wildberries": "https://www.wildberries.ru/catalog/0/search.aspx?search=ZIBELINO+Apple+iPhone+15+Pro",
        "Ozon": "https://www.ozon.ru/search/?text=ZIBELINO+Apple+iPhone+15+Pro",
        "Yandex Market": "https://market.yandex.ru/search?text=ZIBELINO+Apple+iPhone+15+Pro",
    }
