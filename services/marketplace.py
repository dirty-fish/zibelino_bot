from urllib.parse import quote_plus

DEFAULT_MARKETPLACE_LINKS: dict[str, str] = {
    "Wildberries": "https://www.wildberries.ru/brands/zibelino",
    "Ozon": "https://www.ozon.ru/brand/zibelino-78161518/",
    "Yandex Market": "https://market.yandex.ru/business–zibelino/840751",
}


def build_marketplace_links(
    brand: str | None = None,
    model: str | None = None,
) -> dict[str, str]:
    if not brand or not model:
        return DEFAULT_MARKETPLACE_LINKS.copy()

    query = quote_plus(f"ZIBELINO {brand} {model}")

    return {
        "Wildberries": f"https://www.wildberries.ru/catalog/0/search.aspx?search={query}",
        "Ozon": f"https://www.ozon.ru/search/?text={query}",
        "Yandex Market": f"https://market.yandex.ru/search?text={query}",
    }
