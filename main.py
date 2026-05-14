import os
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

# =====================
# LOGGING
# =====================
logging.basicConfig(level=logging.INFO)

# =====================
# BOT TOKEN (Render)
# =====================
API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# =====================
# DATA
# =====================
BLOOD_TYPES = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

GOVERNORATES = [
    'بغداد','البصرة','نينوى','أربيل','السليمانية',
    'كركوك','الأنبار','بابل','ذي قار','ديالى',
    'كربلاء','ميسان','المثنى','النجف','القادسية',
    'صلاح الدين','واسط','دهوك'
]

# =====================
# DATABASE
# =====================
def init_db():
    conn = sqlite3.connect("donors.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY,
            telegram_id INTEGER UNIQUE,
            name TEXT,
            phone TEXT,
            blood_type TEXT,
            governorate TEXT,
            username TEXT
        )
    """)
    conn.commit()
    conn.close()

# =====================
# UI KEYBOARD
# =====================
def main_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📝 تسجيل متبرع", "🔍 بحث عن متبرع")
    kb.add("👤 بياناتي", "❌ حذف بياناتي")
    kb.add("ℹ️ حول المشروع")
    return kb

# =====================
# START
# =====================
@dp.message_handler(commands=['start'])
async def start(message: types.Message):

    text = (
        "🩸 بوت منقذ للتبرع بالدم\n\n"
        "💡 كل تبرع ينقذ 3 أرواح\n"
        "🇮🇶 خدمة إنسانية داخل العراق\n\n"
        "👨‍💻 المطور: المهندس الطبي إسماعيل\n\n"
        "ابدأ من القائمة 👇"
    )

    await message.answer(text, reply_markup=main_kb())

# =====================
# ABOUT
# =====================
@dp.message_handler(lambda m: m.text == "ℹ️ حول المشروع")
async def about(message: types.Message):
    await message.answer(
        "🧠 مشروع تبرع الدم\n"
        "⚡ سريع + آمن + مجاني\n"
        "👨‍💻 المطور: المهندس الطبي إسماعيل"
    )

# =====================
# SHOW DATA
# =====================
@dp.message_handler(lambda m: m.text == "👤 بياناتي")
async def my_data(message: types.Message):

    conn = sqlite3.connect("donors.db")
    c = conn.cursor()
    c.execute("SELECT name, phone, blood_type, governorate FROM donors WHERE telegram_id=?",
              (message.from_user.id,))
    data = c.fetchone()
    conn.close()

    if not data:
        await message.answer("❌ لم يتم تسجيلك بعد")
        return

    await message.answer(
        f"👤 الاسم: {data[0]}\n"
        f"📞 الهاتف: {data[1]}\n"
        f"🩸 الفصيلة: {data[2]}\n"
        f"📍 المحافظة: {data[3]}"
    )

# =====================
# CANCEL
# =====================
@dp.message_handler(lambda m: m.text == "🔙 إلغاء", state="*")
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("تم الإلغاء", reply_markup=main_kb())

# =====================
# INIT
# =====================
if __name__ == "__main__":
    init_db()
    executor.start_polling(dp, skip_updates=True)