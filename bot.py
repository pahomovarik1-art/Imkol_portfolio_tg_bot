import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db  # Импортируем наш новый модуль
from aiohttp import web
import os

# --- НАСТРОЙКИ ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 8287534964

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- FSM ДЛЯ АДМИНКИ ---
class AddProject(StatesGroup):
    name = State()
    description = State()
    link = State()

# --- КЛАВИАТУРЫ ---
def get_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍💻 Обо мне", callback_data="about")],
        [InlineKeyboardButton(text="📁 Мои проекты", callback_data="projects")],
        [InlineKeyboardButton(text="📞 Контакты", callback_data="contacts")]
    ])

def get_back_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back")]
    ])

# --- ОСНОВНЫЕ ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        "Я — imkol, разработчик Telegram-ботов.\n"
        "Выбери раздел ниже:",
        reply_markup=get_main_keyboard()
    )

@dp.callback_query(F.data == "about")
async def about(callback: CallbackQuery):
    await callback.answer()
    text = (
        "👨‍💻 **Обо мне:**\n\n"
        "Меня зовут imkol. Разрабатываю ботов на Python (aiogram 3.x).\n"
        "Пишу чистый код, подключаю базы данных и делаю удобные интерфейсы."
    )
    await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "projects")
async def projects(callback: CallbackQuery):
    await callback.answer()
    
    # Достаем проекты из БД (через наш модуль)
    projects_list = db.get_projects()

    if not projects_list:
        text = "📁 **Мои проекты:**\n\nПока здесь пусто. Скоро добавлю новые работы!"
    else:
        text = "📁 **Мои проекты:**\n\n"
        for i, (name, desc, link) in enumerate(projects_list, 1):
            text += f"{i}. **{name}**\n{desc}\n🔗 {link}\n\n"

    await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "contacts")
async def contacts(callback: CallbackQuery):
    await callback.answer()
    text = (
        "Контакты:\n\n"
        "Telegram: @imkol_official\n"
        "Telegram-channel: @imkol_dev"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✉️ Написать мне", url="https://t.me/imkol_official")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("Главное меню:", reply_markup=get_main_keyboard())

# --- АДМИН-ПАНЕЛЬ ---
@dp.message(Command("add"))
async def admin_panel(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет доступа к этой команде.")
        return
    
    await state.set_state(AddProject.name)
    await message.answer("Введите название проекта (например: 'Бот-магазин'):\n\nДля отмены напишите /cancel")

@dp.message(AddProject.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddProject.description)
    await message.answer("Введите описание проекта:")

@dp.message(AddProject.description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddProject.link)
    await message.answer("Отправьте ссылку на проект (или напишите 'Нет'):")

@dp.message(AddProject.link)
async def process_link(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data['name']
    desc = data['description']
    link = message.text

    # Сохраняем в БД (через наш модуль)
    db.add_project(name, desc, link)

    await state.clear()
    await message.answer(f"✅ Проект '{name}' успешно добавлен в портфолио!")

@dp.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено.")

async def main():
    db.init_db()
    
    # --- ЗАГЛУШКА ДЛЯ RENDER ---
    async def handle(request):
        return web.Response(text="Bot is running!")
    
    app = web.Application()
    app.router.add_get('/', handle)
    
    # Render сам передаст нужный порт в переменную окружения PORT
    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    # ----------------------------

    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())