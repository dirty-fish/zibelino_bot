from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from devices import MANUFACTURERS, get_models
from services.marketplace import build_marketplace_links

CB_MAIN = "main"
CB_SHOPS = "shops"
CB_PROMO = "promo"
CB_SOCIALS = "socials"
CB_CHOOSE_BRAND = "choose_brand"
CB_CHANGE_BRAND = "change_brand"
CB_CHANGE_MODEL = "change_model"
CB_RESET_DEVICE = "reset_device"
CB_ALL_PRODUCTS = "all_products"

BRAND_PREFIX = "brand:"
MODEL_PREFIX = "model:"


def main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📱 Подобрать под устройство", callback_data=CB_CHOOSE_BRAND)
    builder.button(text="🛍 Каталог бренда", callback_data=CB_SHOPS)
    builder.button(text="🔥 Акция", callback_data=CB_PROMO)
    builder.button(text="📲 Соцсети", callback_data=CB_SOCIALS)
    builder.adjust(1)
    return builder.as_markup()


def shops_menu(brand: str | None = None, model: str | None = None) -> InlineKeyboardMarkup:
    links = build_marketplace_links(brand, model) if brand and model else build_marketplace_links()
    builder = InlineKeyboardBuilder()
    builder.button(text="🟣 Wildberries", url=links["Wildberries"])
    builder.button(text="🔵 Ozon", url=links["Ozon"])
    builder.button(text="🟡 Яндекс Маркет", url=links["Yandex Market"])
    builder.button(text="📱 Изменить устройство", callback_data=CB_CHOOSE_BRAND)
    builder.button(text="🏠 Меню", callback_data=CB_MAIN)
    builder.adjust(1)
    return builder.as_markup()


def brand_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for brand in MANUFACTURERS:
        builder.button(text=brand, callback_data=f"{BRAND_PREFIX}{brand}")
    builder.button(text="↩️ Назад", callback_data=CB_SHOPS)
    builder.button(text="🏠 Меню", callback_data=CB_MAIN)
    builder.adjust(1)
    return builder.as_markup()


def model_menu(brand: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for model in get_models(brand):
        builder.button(text=model, callback_data=f"{MODEL_PREFIX}{model}")
    builder.button(text="📱 Изменить производителя", callback_data=CB_CHANGE_BRAND)
    builder.button(text="↩️ Назад", callback_data=CB_CHANGE_BRAND)
    builder.button(text="🏠 Меню", callback_data=CB_MAIN)
    builder.adjust(1)
    return builder.as_markup()


def device_result_menu(brand: str, model: str) -> InlineKeyboardMarkup:
    links = build_marketplace_links(brand, model)
    builder = InlineKeyboardBuilder()
    builder.button(text="🟣 Wildberries", url=links["Wildberries"])
    builder.button(text="🔵 Ozon", url=links["Ozon"])
    builder.button(text="🟡 Яндекс Маркет", url=links["Yandex Market"])
    builder.button(text="✏️ Изменить модель", callback_data=CB_CHANGE_MODEL)
    builder.button(text="📱 Изменить производителя", callback_data=CB_CHANGE_BRAND)
    builder.button(text="🔄 Сбросить устройство", callback_data=CB_RESET_DEVICE)
    builder.button(text="🏠 Меню", callback_data=CB_MAIN)
    builder.adjust(1)
    return builder.as_markup()


def promo_menu() -> InlineKeyboardMarkup:
    links = build_marketplace_links()
    builder = InlineKeyboardBuilder()
    builder.button(text="🛍 Смотреть товары", url=links["Wildberries"])
    builder.button(text="📱 Подобрать устройство", callback_data=CB_CHOOSE_BRAND)
    builder.button(text="🏠 Меню", callback_data=CB_MAIN)
    builder.adjust(1)
    return builder.as_markup()


def socials_menu() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text="Telegram", url="https://t.me/zibelino_official"),
        InlineKeyboardButton(text="VK", url="https://vk.com/zibelino_cases"),
        InlineKeyboardButton(text="MAX", url="https://max.ru/id5024119950_biz"),
        InlineKeyboardButton(text="Дзен", url="https://dzen.ru/zibelino"),
        InlineKeyboardButton(text="TikTok", url="https://www.tiktok.com/@zibelino_"),
        InlineKeyboardButton(text="🏠 Меню", callback_data=CB_MAIN),
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            buttons[0:2],
            buttons[2:4],
            [buttons[4]],
            [buttons[5]],
        ],
    )
