import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

# Configure logging
logging.basicConfig(level=logging.INFO)

# Bot token from BotFather
API_TOKEN = '8275486686:AAFnv1FWuIlRFT0gC7msBnCrKfRMu6tMaEE'

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Constants
BLOOD_TYPES = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
GOVERNORATES = [
    'بغداد', 'البصرة', 'نينوى', 'أربيل', 'السليمانية', 
    'كركوك', 'الأنبار', 'بابل', 'ذي قار', 'ديالى', 
    'كربلاء', 'ميسان', 'المثنى', 'النجف', 'القادسية', 
    'صلاح الدين', 'واسط', 'دهوك'
]

# Database setup
def init_db():
    conn = sqlite3.connect('blood_donors.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY,
            telegram_id INTEGER UNIQUE,
            name TEXT,
            phone TEXT,
            blood_type TEXT,
            governorate TEXT,
            telegram_username TEXT
        )
    ''')
    conn.commit()
    conn.close()

# States for registration
class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_blood_type = State()
    waiting_for_governorate = State()

# States for searching
class SearchStates(StatesGroup):
    waiting_for_blood_type = State()
    waiting_for_governorate = State()

# States for deleting data
class DeleteStates(StatesGroup):
    confirm_delete = State()

# --- Helper Functions for Keyboards ---

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📝 التسجيل كمتبرع", "🔍 البحث عن متبرع")
    markup.row("👤 عرض بياناتي", "❌ حذف بياناتي")
    markup.row("ℹ️ حول المشروع")
    return markup

def get_blood_types_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    markup.add(*BLOOD_TYPES)
    markup.add("🔙 إلغاء")
    return markup

def get_governorates_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(*GOVERNORATES)
    markup.add("🔙 إلغاء")
    return markup

# --- Handlers ---

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    awareness_msg = (
        "مرحباً بك في بوت مُنقذ للتبرع بالدم في العراق! 🇮🇶 🩸\n\n"
        "هل تعلم أن التبرع بالدم لمرة واحدة يمكن أن ينقذ حياة 3 أشخاص؟\n"
        "في العراق، مئات المرضى والمصابين يحتاجون إلى دمك في هذه اللحظة.\n"
        "تبرعك ليس مجرد إجراء طبي، بل هو أمل جديد وعودة للحياة لشخص ما.\n\n"
        "كن بطلاً في حياة غيرك وسجل بياناتك الآن، فربما تكون أنت المنقذ الوحيد لشخص في أمس الحاجة إليك.\n\n"
        "الرجاء اختيار أحد الخيارات من الأزرار أدناه:"
    )
    await message.reply(awareness_msg, reply_markup=get_main_keyboard())

@dp.message_handler(lambda message: message.text == "🔙 إلغاء", state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("تم إلغاء العملية والعودة للقائمة الرئيسية.", reply_markup=get_main_keyboard())

@dp.message_handler(lambda message: message.text == "ℹ️ حول المشروع")
async def about_project(message: types.Message):
    await message.reply(
        "بوت منقذ هو مبادرة تقنية تهدف لتسهيل التبرع بالدم في العراق.\n"
        "نحن نعمل على ربط المتبرعين بالمحتاجين بشكل سريع وفعال.\n"
        "جميع البيانات محمية وتستخدم فقط لغرض التبرع بالدم.\n\n"
        "للتواصل مع المطورين أو لدعم المشروع، يرجى مراسلتنا.",
        reply_markup=get_main_keyboard()
    )

@dp.message_handler(lambda message: message.text == "👤 عرض بياناتي")
async def show_my_data(message: types.Message):
    conn = sqlite3.connect('blood_donors.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, phone, blood_type, governorate, telegram_username FROM donors WHERE telegram_id = ?', (message.from_user.id,))
    donor = cursor.fetchone()
    conn.close()

    if donor:
        name, phone, blood_type, governorate, username = donor
        msg = (
            "👤 بياناتك المسجلة كمتبرع:\n\n"
            f"📝 الاسم: {name}\n"
            f"📞 الهاتف: {phone}\n"
            f"🩸 الفصيلة: {blood_type}\n"
            f"📍 المحافظة: {governorate}\n"
            f"🆔 يوزر تليجرام: @{username if username != 'غير متوفر' else 'غير متوفر'}\n\n"
            "يمكنك حذف بياناتك وإعادة التسجيل إذا أردت تعديل أي معلومة."
        )
        await message.reply(msg, reply_markup=get_main_keyboard())
    else:
        await message.reply("أنت غير مسجل كمتبرع حالياً. يمكنك التسجيل عبر زر '📝 التسجيل كمتبرع'.", reply_markup=get_main_keyboard())

# --- Registration Flow ---

@dp.message_handler(lambda message: message.text == "📝 التسجيل كمتبرع")
async def register_start(message: types.Message):
    conn = sqlite3.connect('blood_donors.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM donors WHERE telegram_id = ?', (message.from_user.id,))
    donor = cursor.fetchone()
    conn.close()

    if donor:
        await message.reply("أنت مسجل بالفعل كمتبرع. إذا أردت تحديث بياناتك، قم بحذفها أولاً ثم أعد التسجيل.")
        return

    await message.reply("للبدء، يرجى إدخال اسمك الكامل:", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("🔙 إلغاء"))
    await RegistrationStates.waiting_for_name.set()

@dp.message_handler(state=RegistrationStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.reply("شكراً لك. الآن، يرجى إدخال رقم هاتفك للتواصل:")
    await RegistrationStates.waiting_for_phone.set()

@dp.message_handler(state=RegistrationStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text
    if not phone.isdigit() or len(phone) < 10:
        await message.reply("رقم الهاتف غير صحيح. يرجى إدخال رقم هاتف صالح (أرقام فقط).")
        return
    async with state.proxy() as data:
        data['phone'] = phone
    
    await message.reply("يرجى اختيار فصيلة دمك:", reply_markup=get_blood_types_keyboard())
    await RegistrationStates.waiting_for_blood_type.set()

@dp.message_handler(state=RegistrationStates.waiting_for_blood_type)
async def process_blood_type(message: types.Message, state: FSMContext):
    blood_type = message.text.upper()
    if blood_type not in BLOOD_TYPES:
        await message.reply("يرجى اختيار فصيلة دم صحيحة من القائمة.")
        return
    async with state.proxy() as data:
        data['blood_type'] = blood_type
    
    await message.reply("يرجى اختيار محافظتك:", reply_markup=get_governorates_keyboard())
    await RegistrationStates.waiting_for_governorate.set()

@dp.message_handler(state=RegistrationStates.waiting_for_governorate)
async def process_governorate(message: types.Message, state: FSMContext):
    governorate = message.text
    if governorate not in GOVERNORATES:
        await message.reply("يرجى اختيار محافظة صحيحة من القائمة.")
        return

    async with state.proxy() as data:
        data['governorate'] = governorate  # حفظ المحافظة في البيانات المؤقتة أولاً
        telegram_username = message.from_user.username if message.from_user.username else "غير متوفر"
        conn = sqlite3.connect('blood_donors.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO donors (telegram_id, name, phone, blood_type, governorate, telegram_username) VALUES (?, ?, ?, ?, ?, ?)",
                       (message.from_user.id, data['name'], data['phone'], data['blood_type'], data['governorate'], telegram_username))
        conn.commit()
        conn.close()

    await message.reply(
        "✅ تم تسجيلك كمتبرع بنجاح! شكراً لمساهمتك الإنسانية.\n\n"
        "ملاحظة: يمكنك دائماً حذف بياناتك أو تحديثها عبر القائمة الرئيسية.",
        reply_markup=get_main_keyboard()
    )
    await state.finish()

# --- Search Flow ---

@dp.message_handler(lambda message: message.text == "🔍 البحث عن متبرع")
async def search_start(message: types.Message):
    await message.reply("للبحث عن متبرعين، يرجى اختيار فصيلة الدم المطلوبة:", reply_markup=get_blood_types_keyboard())
    await SearchStates.waiting_for_blood_type.set()

@dp.message_handler(state=SearchStates.waiting_for_blood_type)
async def search_process_blood_type(message: types.Message, state: FSMContext):
    blood_type = message.text.upper()
    if blood_type not in BLOOD_TYPES:
        await message.reply("يرجى اختيار فصيلة دم صحيحة من القائمة.")
        return
    async with state.proxy() as data:
        data['blood_type'] = blood_type
    
    await message.reply("يرجى اختيار المحافظة للبحث فيها:", reply_markup=get_governorates_keyboard())
    await SearchStates.waiting_for_governorate.set()

@dp.message_handler(state=SearchStates.waiting_for_governorate)
async def search_process_governorate(message: types.Message, state: FSMContext):
    governorate = message.text
    if governorate not in GOVERNORATES:
        await message.reply("يرجى اختيار محافظة صحيحة من القائمة.")
        return

    async with state.proxy() as data:
        blood_type = data['blood_type']
        
        conn = sqlite3.connect('blood_donors.db')
        cursor = conn.cursor()
        # تعديل الاستعلام ليشمل الجميع لغرض الاختبار والوضوح
        cursor.execute('SELECT name, phone, telegram_username FROM donors WHERE blood_type = ? AND governorate = ?', 
                       (blood_type, governorate))
        donors = cursor.fetchall()
        conn.close()

        if donors:
            response_message = f"📍 تم العثور على المتبرعين التاليين بفصيلة {blood_type} في {governorate}:\n\n"
            for donor_name, donor_phone, donor_username in donors:
                response_message += f"👤 الاسم: {donor_name}\n📞 الهاتف: {donor_phone}\n"
                if donor_username and donor_username != "غير متوفر":
                    response_message += f"🆔 يوزر: @{donor_username}\n"
                response_message += "------------------\n"
        else:
            response_message = f"❌ نعتذر، لم يتم العثور على متبرعين بفصيلة {blood_type} في محافظة {governorate} حالياً."
    
    await message.reply(response_message, reply_markup=get_main_keyboard())
    await state.finish()

# --- Delete Data Flow ---

@dp.message_handler(lambda message: message.text == "❌ حذف بياناتي")
async def delete_data_start(message: types.Message):
    conn = sqlite3.connect('blood_donors.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM donors WHERE telegram_id = ?', (message.from_user.id,))
    donor = cursor.fetchone()
    conn.close()

    if not donor:
        await message.reply("بياناتك غير مسجلة لدينا أصلاً.")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("✅ نعم، أحذف بياناتي", "🔙 إلغاء")
    await message.reply("⚠️ هل أنت متأكد من حذف بياناتك كمتبرع نهائياً؟", reply_markup=markup)
    await DeleteStates.confirm_delete.set()

@dp.message_handler(state=DeleteStates.confirm_delete)
async def delete_data_confirm(message: types.Message, state: FSMContext):
    if message.text == "✅ نعم، أحذف بياناتي":
        conn = sqlite3.connect('blood_donors.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM donors WHERE telegram_id = ?', (message.from_user.id,))
        conn.commit()
        conn.close()
        await message.reply("🗑 تم حذف جميع بياناتك بنجاح.", reply_markup=get_main_keyboard())
    else:
        await message.reply("تم إلغاء العملية.", reply_markup=get_main_keyboard())
    await state.finish()

# --- Main execution ---

import os

if __name__ == '__main__':
    init_db()
    executor.start_polling(dp, skip_updates=True)
