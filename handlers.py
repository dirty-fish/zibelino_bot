import asyncio
from os import getenv
from pathlib import Path
from typing import Any

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, Message

import keyboards
import texts
from devices import is_supported_brand, is_supported_model

router = Router()

LAST_SCREEN_MESSAGE_ID = "last_screen_message_id"


class DeviceSelection(StatesGroup):
    choosing_brand = State()
    choosing_model = State()
    device_selected = State()


async def send_text_with_optional_image(
    target: Message,
    text: str,
    image_path: Path,
    reply_markup: Any | None = None,
) -> Message:
    if image_path.exists() and image_path.is_file():
        return await target.answer_photo(
            photo=FSInputFile(image_path),
            caption=text,
            reply_markup=reply_markup,
        )

    return await target.answer(text, reply_markup=reply_markup)


async def delete_message_safely(message: Message | None) -> None:
    if not message:
        return

    delete = getattr(message, "delete", None)
    if not delete:
        return

    try:
        await delete()
    except TelegramBadRequest:
        pass


async def delete_message_by_id_safely(message: Message, message_id: int) -> None:
    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    except TelegramBadRequest:
        pass


async def disable_markup_safely(message: Message | None) -> None:
    if not message:
        return

    try:
        await message.edit_reply_markup(reply_markup=None)
    except TelegramBadRequest:
        pass


async def get_stored_screen_id(state: FSMContext) -> int | None:
    data = await state.get_data()
    message_id = data.get(LAST_SCREEN_MESSAGE_ID)
    if not isinstance(message_id, int):
        return None

    return message_id


async def remember_screen(state: FSMContext, message: Message) -> None:
    await state.update_data({LAST_SCREEN_MESSAGE_ID: message.message_id})


async def edit_screen_if_possible(
    target: Message,
    state: FSMContext,
    text: str,
    reply_markup: Any,
    image_path: Path | None,
) -> bool:
    try:
        has_image = image_path is not None and image_path.exists() and image_path.is_file()

        if has_image and target.photo:
            await target.edit_media(
                media=InputMediaPhoto(media=FSInputFile(image_path), caption=text),
                reply_markup=reply_markup,
            )
            await remember_screen(state, target)
            return True

        if not has_image and not target.photo:
            await target.edit_text(text, reply_markup=reply_markup)
            await remember_screen(state, target)
            return True
    except TelegramBadRequest:
        return False

    return False


async def send_screen(
    target: Message,
    state: FSMContext,
    text: str,
    reply_markup: Any,
    image_filename: str | None = None,
    delete_current: bool = False,
) -> None:
    old_message_id = target.message_id if delete_current else await get_stored_screen_id(state)
    image_path = get_media_path(target, image_filename) if image_filename else None

    if delete_current and await edit_screen_if_possible(
        target,
        state,
        text,
        reply_markup,
        image_path,
    ):
        return

    if delete_current:
        await disable_markup_safely(target)

    await target.bot.send_chat_action(chat_id=target.chat.id, action=ChatAction.TYPING)

    sent = await send_text_with_optional_image(target, text, image_path or Path(), reply_markup)

    await remember_screen(state, sent)

    if old_message_id and old_message_id != sent.message_id:
        await asyncio.sleep(0.15)
        await delete_message_by_id_safely(target, old_message_id)


def get_media_path(message: Message, filename: str) -> Path:
    media_dir = Path(getenv("MEDIA_DIR", "media"))
    if not media_dir.is_absolute():
        return Path(__file__).resolve().parent / media_dir / filename

    return media_dir / filename


async def show_main_menu(
    message: Message,
    state: FSMContext | None = None,
    delete_current: bool = False,
) -> None:
    if state:
        await state.set_state(None)

        await send_screen(
            message,
            state,
            texts.START,
            keyboards.main_menu(),
            "start.jpg",
            delete_current=delete_current,
        )
        return

    await send_text_with_optional_image(
        message,
        texts.START,
        get_media_path(message, "start.jpg"),
        keyboards.main_menu(),
    )


async def show_shops(message: Message, state: FSMContext, delete_current: bool = False) -> None:
    data = await state.get_data()
    brand = data.get("brand")
    model = data.get("model")

    await send_screen(
        message,
        state,
        texts.SHOPS + texts.selected_device_text(brand, model),
        keyboards.shops_menu(brand, model),
        "shops.jpg",
        delete_current=delete_current,
    )


async def show_brand_selection(
    message: Message,
    state: FSMContext,
    delete_current: bool = False,
) -> None:
    await state.set_state(DeviceSelection.choosing_brand)
    await send_screen(
        message,
        state,
        texts.CHOOSE_BRAND,
        keyboards.brand_menu(),
        delete_current=delete_current,
    )


async def show_model_selection(
    message: Message,
    state: FSMContext,
    brand: str,
    delete_current: bool = False,
) -> None:
    await state.update_data(brand=brand)
    await state.set_state(DeviceSelection.choosing_model)
    await send_screen(
        message,
        state,
        texts.CHOOSE_MODEL.format(brand=brand),
        keyboards.model_menu(brand),
        delete_current=delete_current,
    )


async def show_device_result(
    message: Message,
    state: FSMContext,
    brand: str,
    model: str,
    delete_current: bool = False,
) -> None:
    await state.update_data(brand=brand, model=model)
    await state.set_state(DeviceSelection.device_selected)
    await send_screen(
        message,
        state,
        texts.DEVICE_RESULT.format(brand=brand, model=model),
        keyboards.device_result_menu(brand, model),
        delete_current=delete_current,
    )


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await show_main_menu(message, state)


@router.callback_query(F.data == keyboards.CB_MAIN)
async def main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if callback.message:
        await show_main_menu(callback.message, state, delete_current=True)


@router.callback_query(F.data == keyboards.CB_SHOPS)
async def shops(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if callback.message:
        await show_shops(callback.message, state, delete_current=True)


@router.callback_query(F.data == keyboards.CB_PROMO)
async def promo(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if callback.message:
        await send_screen(
            callback.message,
            state,
            texts.PROMO,
            keyboards.promo_menu(),
            "promo.jpg",
            delete_current=True,
        )


@router.callback_query(F.data == keyboards.CB_SOCIALS)
async def socials(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if callback.message:
        await send_screen(
            callback.message,
            state,
            texts.SOCIALS,
            keyboards.socials_menu(),
            "socials.jpg",
            delete_current=True,
        )


@router.callback_query(F.data.in_({keyboards.CB_CHOOSE_BRAND, keyboards.CB_CHANGE_BRAND}))
async def choose_brand(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if callback.message:
        await show_brand_selection(callback.message, state, delete_current=True)


@router.callback_query(F.data.startswith(keyboards.BRAND_PREFIX))
async def brand_selected(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if not callback.message or not callback.data:
        return

    brand = callback.data.removeprefix(keyboards.BRAND_PREFIX)
    if not is_supported_brand(brand):
        await show_brand_selection(callback.message, state, delete_current=True)
        return

    await show_model_selection(callback.message, state, brand, delete_current=True)


@router.callback_query(F.data == keyboards.CB_CHANGE_MODEL)
async def change_model(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if not callback.message:
        return

    data = await state.get_data()
    brand = data.get("brand")
    if not brand or not is_supported_brand(brand):
        await show_brand_selection(callback.message, state, delete_current=True)
        return

    await show_model_selection(callback.message, state, brand, delete_current=True)


@router.callback_query(F.data.startswith(keyboards.MODEL_PREFIX))
async def model_selected(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if not callback.message or not callback.data:
        return

    data = await state.get_data()
    brand = data.get("brand")
    model = callback.data.removeprefix(keyboards.MODEL_PREFIX)

    if not brand or not is_supported_model(brand, model):
        await show_brand_selection(callback.message, state, delete_current=True)
        return

    await show_device_result(callback.message, state, brand, model, delete_current=True)


@router.callback_query(F.data == keyboards.CB_RESET_DEVICE)
async def reset_device(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    if callback.message:
        await send_screen(
            callback.message,
            state,
            texts.DEVICE_RESET,
            keyboards.main_menu(),
            delete_current=True,
        )


@router.message()
async def unsupported_text(message: Message, state: FSMContext) -> None:
    await state.set_state(None)
    old_message_id = await get_stored_screen_id(state)
    sent = await message.answer(texts.UNSUPPORTED_TEXT, reply_markup=keyboards.main_menu())
    await remember_screen(state, sent)

    if old_message_id and old_message_id != sent.message_id:
        await delete_message_by_id_safely(message, old_message_id)
