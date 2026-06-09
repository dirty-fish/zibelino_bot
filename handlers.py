from os import getenv
from pathlib import Path
from typing import Any

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, Message

import keyboards
import texts
from devices import is_supported_brand, is_supported_model

router = Router()


class DeviceSelection(StatesGroup):
    choosing_brand = State()
    choosing_model = State()
    device_selected = State()


async def send_text_with_optional_image(
    target: Message,
    text: str,
    image_path: Path,
    reply_markup: Any | None = None,
) -> None:
    if image_path.exists() and image_path.is_file():
        await target.answer_photo(
            photo=FSInputFile(image_path),
            caption=text,
            reply_markup=reply_markup,
        )
        return

    await target.answer(text, reply_markup=reply_markup)


def get_media_path(message: Message, filename: str) -> Path:
    media_dir = Path(getenv("MEDIA_DIR", "media"))
    if not media_dir.is_absolute():
        return Path(__file__).resolve().parent / media_dir / filename

    return media_dir / filename


async def show_main_menu(message: Message, state: FSMContext | None = None) -> None:
    if state:
        await state.set_state(None)

    await send_text_with_optional_image(
        message,
        texts.START,
        get_media_path(message, "start.jpg"),
        keyboards.main_menu(),
    )


async def show_shops(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    brand = data.get("brand")
    model = data.get("model")

    await send_text_with_optional_image(
        message,
        texts.SHOPS + texts.selected_device_text(brand, model),
        get_media_path(message, "shops.jpg"),
        keyboards.shops_menu(brand, model),
    )


async def show_brand_selection(message: Message, state: FSMContext) -> None:
    await state.set_state(DeviceSelection.choosing_brand)
    await message.answer(texts.CHOOSE_BRAND, reply_markup=keyboards.brand_menu())


async def show_model_selection(message: Message, state: FSMContext, brand: str) -> None:
    await state.update_data(brand=brand)
    await state.set_state(DeviceSelection.choosing_model)
    await message.answer(
        f"{texts.CHOOSE_MODEL}\n\n{brand}",
        reply_markup=keyboards.model_menu(brand),
    )


async def show_device_result(message: Message, state: FSMContext, brand: str, model: str) -> None:
    await state.update_data(brand=brand, model=model)
    await state.set_state(DeviceSelection.device_selected)
    await message.answer(
        texts.DEVICE_RESULT.format(brand=brand, model=model),
        reply_markup=keyboards.device_result_menu(brand, model),
    )


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await show_main_menu(message, state)


@router.callback_query(F.data == keyboards.CB_MAIN)
async def main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if callback.message:
        await show_main_menu(callback.message, state)


@router.callback_query(F.data == keyboards.CB_SHOPS)
async def shops(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if callback.message:
        await show_shops(callback.message, state)


@router.callback_query(F.data == keyboards.CB_PROMO)
async def promo(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await send_text_with_optional_image(
            callback.message,
            texts.PROMO,
            get_media_path(callback.message, "promo.jpg"),
            keyboards.promo_menu(),
        )


@router.callback_query(F.data == keyboards.CB_SOCIALS)
async def socials(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await send_text_with_optional_image(
            callback.message,
            texts.SOCIALS,
            get_media_path(callback.message, "socials.jpg"),
            keyboards.socials_menu(),
        )


@router.callback_query(F.data.in_({keyboards.CB_CHOOSE_BRAND, keyboards.CB_CHANGE_BRAND}))
async def choose_brand(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if callback.message:
        await show_brand_selection(callback.message, state)


@router.callback_query(F.data.startswith(keyboards.BRAND_PREFIX))
async def brand_selected(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if not callback.message or not callback.data:
        return

    brand = callback.data.removeprefix(keyboards.BRAND_PREFIX)
    if not is_supported_brand(brand):
        await show_brand_selection(callback.message, state)
        return

    await show_model_selection(callback.message, state, brand)


@router.callback_query(F.data == keyboards.CB_CHANGE_MODEL)
async def change_model(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if not callback.message:
        return

    data = await state.get_data()
    brand = data.get("brand")
    if not brand or not is_supported_brand(brand):
        await show_brand_selection(callback.message, state)
        return

    await show_model_selection(callback.message, state, brand)


@router.callback_query(F.data.startswith(keyboards.MODEL_PREFIX))
async def model_selected(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if not callback.message or not callback.data:
        return

    data = await state.get_data()
    brand = data.get("brand")
    model = callback.data.removeprefix(keyboards.MODEL_PREFIX)

    if not brand or not is_supported_model(brand, model):
        await show_brand_selection(callback.message, state)
        return

    await show_device_result(callback.message, state, brand, model)


@router.callback_query(F.data == keyboards.CB_RESET_DEVICE)
async def reset_device(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    if callback.message:
        await callback.message.answer(texts.DEVICE_RESET, reply_markup=keyboards.main_menu())


@router.message()
async def unsupported_text(message: Message, state: FSMContext) -> None:
    await state.set_state(None)
    await message.answer(texts.UNSUPPORTED_TEXT, reply_markup=keyboards.main_menu())
