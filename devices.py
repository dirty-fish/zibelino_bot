MANUFACTURERS: tuple[str, ...] = (
    "Apple",
    "Samsung",
    "Xiaomi",
)

MODELS_BY_MANUFACTURER: dict[str, tuple[str, ...]] = {
    "Apple": (
        "iPhone 15",
        "iPhone 15 Pro",
        "iPhone 14",
        "iPhone 13",
    ),
    "Samsung": (
        "Galaxy S24",
        "Galaxy S23",
        "Galaxy A55",
    ),
    "Xiaomi": (
        "Xiaomi 14",
        "Redmi Note 13",
        "Poco X6 Pro",
    ),
}


def get_models(brand: str) -> tuple[str, ...]:
    return MODELS_BY_MANUFACTURER.get(brand, ())


def is_supported_brand(brand: str) -> bool:
    return brand in MANUFACTURERS


def is_supported_model(brand: str, model: str) -> bool:
    return model in get_models(brand)
