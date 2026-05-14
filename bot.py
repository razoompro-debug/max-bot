import asyncio
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from openpyxl import Workbook, load_workbook

# =========================================
# НАСТРОЙКИ
# =========================================

TOKEN = "8873197701:AAEgP61xiVJfepjsYUDSr6VAtynKRAU9Eqo"
ADMIN_ID = 816279118

EXCEL_FILE = "orders.xlsx"

# =========================================
# EXCEL
# =========================================

def create_excel():

    if not os.path.exists(EXCEL_FILE):

        wb = Workbook()
        ws = wb.active

        ws.title = "Orders"

        ws.append([
            "Дата",
            "Модель",
            "Размер",
            "Цвет футболки",
            "Надпись",
            "Цвет надписи",
            "Размер надписи",
            "ФИО",
            "Телефон",
            "Адрес"
        ])

        wb.save(EXCEL_FILE)

create_excel()

# =========================================
# СОХРАНЕНИЕ ЗАКАЗА
# =========================================

def save_order(data):

    wb = load_workbook(EXCEL_FILE)
    ws = wb.active

    ws.append([
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        data["gender"],
        data["format_size"],
        data["tshirt_color"],
        data["text"],
        data["text_color"],
        data["text_size"],
        data["name"],
        data["phone"],
        data["address"]
    ])

    wb.save(EXCEL_FILE)

# =========================================
# FSM
# =========================================

class OrderState(StatesGroup):

    gender = State()
    format_size = State()
    tshirt_color = State()
    text = State()
    text_color = State()
    text_size = State()
    name = State()
    phone = State()
    address = State()

# =========================================
# BOT
# =========================================

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# =========================================
# КНОПКИ
# =========================================

def gender_kb():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👔 Мужская",
                    callback_data="male"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👚 Женская",
                    callback_data="female"
                )
            ]
        ]
    )

def size_kb():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📏 MINI",
                    callback_data="mini"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📏 MAXI",
                    callback_data="maxi"
                )
            ]
        ]
    )

def tshirt_color_kb():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚪ Белый",
                    callback_data="white"
                ),
                InlineKeyboardButton(
                    text="⚫ Чёрный",
                    callback_data="black"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔴 Красный",
                    callback_data="red"
                ),
                InlineKeyboardButton(
                    text="🔵 Синий",
                    callback_data="blue"
                )
            ]
        ]
    )

def text_color_kb():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚪ Белый",
                    callback_data="white_text"
                ),
                InlineKeyboardButton(
                    text="⚫ Чёрный",
                    callback_data="black_text"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔴 Красный",
                    callback_data="red_text"
                ),
                InlineKeyboardButton(
                    text="🟡 Золотой",
                    callback_data="gold_text"
                )
            ]
        ]
    )

def text_size_kb():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔹 Маленькая",
                    callback_data="small"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔸 Средняя",
                    callback_data="medium"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⭐ Большая",
                    callback_data="large"
                )
            ]
        ]
    )

# =========================================
# START
# =========================================

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):

    await state.clear()

    await message.answer(
        "👕 <b>Именные футболки</b>\n\n"
        "Создайте уникальную футболку всего за пару минут ✨\n\n"
        "👇 Выберите модель:",
        parse_mode="HTML",
        reply_markup=gender_kb()
    )

    await state.set_state(OrderState.gender)

# =========================================
# ВЫБОР МОДЕЛИ
# =========================================

@dp.callback_query(OrderState.gender)
async def choose_gender(callback: CallbackQuery, state: FSMContext):

    gender = "Мужская 👔" \
        if callback.data == "male" \
        else "Женская 👚"

    await state.update_data(gender=gender)

    await callback.message.edit_text(
        "📏 Выберите размер футболки:",
        reply_markup=size_kb()
    )

    await state.set_state(OrderState.format_size)

    await callback.answer()

# =========================================
# РАЗМЕР
# =========================================

@dp.callback_query(OrderState.format_size)
async def choose_size(callback: CallbackQuery, state: FSMContext):

    size = "MINI" if callback.data == "mini" else "MAXI"

    await state.update_data(format_size=size)

    await callback.message.edit_text(
        "🎨 Выберите цвет футболки:",
        reply_markup=tshirt_color_kb()
    )

    await state.set_state(OrderState.tshirt_color)

    await callback.answer()

# =========================================
# ЦВЕТ ФУТБОЛКИ
# =========================================

@dp.callback_query(OrderState.tshirt_color)
async def choose_tshirt_color(
    callback: CallbackQuery,
    state: FSMContext
):

    colors = {
        "white": "Белый",
        "black": "Чёрный",
        "red": "Красный",
        "blue": "Синий"
    }

    await state.update_data(
        tshirt_color=colors[callback.data]
    )

    await callback.message.edit_text(
        "✍️ Введите текст надписи:"
    )

    await state.set_state(OrderState.text)

    await callback.answer()

# =========================================
# ТЕКСТ
# =========================================

@dp.message(OrderState.text)
async def get_text(message: Message, state: FSMContext):

    await state.update_data(text=message.text)

    await message.answer(
        "🎨 Выберите цвет надписи:",
        reply_markup=text_color_kb()
    )

    await state.set_state(OrderState.text_color)

# =========================================
# ЦВЕТ НАДПИСИ
# =========================================

@dp.callback_query(OrderState.text_color)
async def choose_text_color(
    callback: CallbackQuery,
    state: FSMContext
):

    colors = {
        "white_text": "Белый",
        "black_text": "Чёрный",
        "red_text": "Красный",
        "gold_text": "Золотой"
    }

    await state.update_data(
        text_color=colors[callback.data]
    )

    await callback.message.edit_text(
        "📏 Выберите размер надписи:",
        reply_markup=text_size_kb()
    )

    await state.set_state(OrderState.text_size)

    await callback.answer()

# =========================================
# РАЗМЕР НАДПИСИ
# =========================================

@dp.callback_query(OrderState.text_size)
async def choose_text_size(
    callback: CallbackQuery,
    state: FSMContext
):

    sizes = {
        "small": "Маленькая",
        "medium": "Средняя",
        "large": "Большая"
    }

    await state.update_data(
        text_size=sizes[callback.data]
    )

    await callback.message.edit_text(
        "👤 Введите ФИО:"
    )

    await state.set_state(OrderState.name)

    await callback.answer()

# =========================================
# ФИО
# =========================================

@dp.message(OrderState.name)
async def get_name(message: Message, state: FSMContext):

    await state.update_data(name=message.text)

    await message.answer(
        "📱 Введите номер телефона:"
    )

    await state.set_state(OrderState.phone)

# =========================================
# ТЕЛЕФОН
# =========================================

@dp.message(OrderState.phone)
async def get_phone(message: Message, state: FSMContext):

    await state.update_data(phone=message.text)

    await message.answer(
        "🏠 Введите адрес доставки:"
    )

    await state.set_state(OrderState.address)

# =========================================
# АДРЕС
# =========================================

@dp.message(OrderState.address)
async def get_address(message: Message, state: FSMContext):

    await state.update_data(address=message.text)

    data = await state.get_data()

    # СОХРАНЕНИЕ
    save_order(data)

    # СООБЩЕНИЕ АДМИНУ
    order_text = f"""
✅ <b>НОВЫЙ ЗАКАЗ</b>

👔 Модель: {data['gender']}
📏 Размер: {data['format_size']}

🎨 Цвет футболки: {data['tshirt_color']}

✍️ Надпись: {data['text']}
🎨 Цвет надписи: {data['text_color']}
📏 Размер надписи: {data['text_size']}

👤 ФИО: {data['name']}
📱 Телефон: {data['phone']}
🏠 Адрес: {data['address']}
"""

    # КЛИЕНТУ
    await message.answer(
        "✅ <b>Спасибо за заказ!</b>\n\n"
        "Наш менеджер скоро свяжется с Вами ✨",
        parse_mode="HTML"
    )

    # АДМИНУ
    await bot.send_message(
        ADMIN_ID,
        order_text,
        parse_mode="HTML"
    )

    await state.clear()

# =========================================
# ЗАПУСК
# =========================================

async def main():

    print("BOT STARTED")

    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())