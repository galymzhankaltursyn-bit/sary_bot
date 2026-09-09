import asyncio
import logging
import urllib.parse
import html
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message, BotCommand

# Консольде барлық логтарды көрсету
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s"
)

BOT_TOKEN = "8670634864:AAHQOXWUHCS9nIF2YUodlbqRTM_qm-Lg6kw" 
ADMIN_ID = 8129855972               
ADMIN_USERNAME = "from_aksh"       

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

users_db = {}
referrals_db = {}

# МІНДЕТТІ ТІРКЕЛЕТІН АРНАЛАР
# Егер арнаңыз ЖАБЫҚ (Частный) болса, chat_id орнына сандық ID (-100... деп басталатын) жазасыз!
REQUIRED_CHANNELS = [
    {
        "title": "💨 Одноразка Шымкент", 
        "url": "https://t.me/shymkent_rask", 
        "chat_id": -1003995924771,
    },
    {
        "title": "💬 Наш Отзыв канал", 
        "url": "https://t.me/otzyv_rask_shym", 
        "chat_id": -1003923733476,
    }
]

class OrderState(StatesGroup):
    waiting_for_vape = State()
    waiting_for_flavor = State()
    waiting_for_city = State()
    waiting_for_address = State()
    waiting_for_confirm = State()

PRODUCTS = {
    "et_burst": {"name": "Waka E.T Burst 41k puffs", "price": 23000, "puffs": "41k", "nicotine": "12-15%", "flavors": ["Клубника 🍓", "Киви 🥝", "Виноград 🍇"]},
    "blast": {"name": "Waka BLAST 38k puffs", "price": 21500, "puffs": "38k", "nicotine": "12-15%", "flavors": ["Манго 🥭", "Арбуз 🍉", "Яблоко 🍏", "Энергетик⚡ ~ Лимон 🍋", "Манго 🥭 ~ Ваниль 🍦", "Тройная ягода 🪐 + лёд 🧊", "Арбуз 🍉 ~ лёд 🧊", "Вишня 🍒 ~ лёд 🧊", "Клубника 🍓 ~ Киви 🥝 + лёд 🧊", "Черника 🫐 ~ Малина ⚡️ + лёд 🧊"]},
    "x_spike": {"name": "Waka XLAND SPIKE 35k puffs", "price": 20000, "puffs": "35k", "nicotine": "12-15%", "flavors": ["Виноград 🍇", "Кислое яблоко 🍏", "Клюква ~ Виноград 🍇", "Черника 🫐 ~ Вишня 🍒"]},
    "jupiter": {"name": "Waka JUPITER 30k puffs", "price": 18000, "puffs": "30k", "nicotine": "12-15%", "flavors": ["Арбуз 🍉", "Вишня 🍒", "Клубника 🍓", "Гавайский лимонад 🍹", "Клюква ~ Виноград 🍇", "Ежевика ~ Черника 🫐 ~ Малина 💫"]},
    "sopro_20": {"name": "Waka SoPro 20k puffs", "price": 15000, "puffs": "20k", "nicotine": "11%", "flavors": ["Арбуз 🍉", "Вишня 🍒", "Лимон 🍋", "Клубника 🍓", "Яблоко 🍏", "Виноград 🍇", "Зелёный Виноград 🟢🍇", "Тройная ягода 💥", "Капучино ☕", "Тёмная вишня 🍒", "Энергетик ⚡", "Клубника 🍓 ~ Виноград 🍇", "Арбуз 🍉 ~ Вишня 🍒", "Клубника 🍓 ~ Киви 🥝", "Арбуз 🍉 ~ Мята ⚡️", "Яблоко 🍏 ~ Груша 🍐", "Клубника 🍓 ~ Арбуз 🍉", "Клубника 🍓 + лёд 🧊", "Лайм 💫 + лёд 🧊"]},
    "xland": {"name": "Waka XLAND 15k puffs", "price": 14000, "puffs": "15k", "nicotine": "9-11%", "flavors": ["Арбуз 🍉", "Мята ❄️", "Виноград 🍇", "Кислое яблоко 🍏", "Зеленый Виноград 🍇", "Сакура 🌸 ~ виноград 🍇", "Клубника 🍓 ~ Киви 🥝", "Черника 🫐 ~ Малина 💫"]},
    "sopro_pa": {"name": "Waka SoPro PA 10k puffs", "price": 12500, "puffs": "10k", "nicotine": "8-9%", "flavors": ["Арбуз 🍉", "Вишня 🍒", "Киви 🥝", "Виноград 🍇", "Персик 🍑", "Гранат 💫", "Мультифрукты 🍓", "Ягодный микс 💫", "Ягодный тархун⚡️", "Клубника 🍓 ~ Банан 🍌", "Персик 🍑 ~ Манго 🥭", "Лимон 🍋 ~ Лайм 🍋", "Манго 🥭 ~ Апельсин 🍊", "Клубника 🍓 ~ Виноград 🍇", "Черника 🫐 ~ Черная смородина 🪐", "Гуава ~ Малина ⚡️", "Черника 🫐 ~ Малина ⚡️", "Арбуз 🍉 + лёд 🧊", "Вишня 🍒 + лёд 🧊", "Черника 🫐 + лёд 🧊", "Клубника 🍓 ~ Киви 🥝 + лёд 🧊", "Малина 💥 ~ Черника 🫐 +лёд 🧊", "Черника 🫐 ~ Малина 💥 ~ Лимон 🍋 + лёд 🧊"]},
    "sopro_dm": {"name": "Waka SoPro DM 8k puffs", "price": 9500, "puffs": "8k", "nicotine": "9-11%", "flavors": ["Малина 🥸", "Киви 🥝", "Виноград 🍇", "Персик 🍑", "Клубника 🍓", "Манго 🥭", "Арбуз 🍉", "Вишня 🍒", "Дюшес 💫", "Черника 🫐", "Ягодный микс 🍓", "Виноград 🍇 ~ Яблоко 🍏", "Черника 🫐 ~ Малина 💫", "Персик 🍑 ~ Клубника 🍓", "Черника 🫐 ~ Малина 💫 ~ Гранат ⚡️"]},
    "smash": {"name": "Waka Smash 6k puffs", "price": 7500, "puffs": "6k", "nicotine": "7%", "flavors": ["Арбуз 🍉", "Яблоко 🍏", "Черника 🫐", "Виноград 🍇", "Клубника 🍓", "Вишня 🍒", "Вишнёвый Лайм 🌪", "Дюшес 💥", "Алоэ ~ Виноград 🍇", "Банан 🍌 ~ Дыня 🍈", "Банан 🍌 ~ Какос 💫", "Клубника 🍓 ~ Манго 🥭", "Клубника 🍓 ~ Виноград 🍇"]},
    "solo_2": {"name": "Waka Solo 2 2.5k puffs", "price": 5500, "puffs": "2.5k", "nicotine": "5-7%", "flavors": ["Клубника 🍓", "Черника 🫐", "Мультифрукты ⚡️", "Арбуз 🍉", "Клубника 🍓 ~ Малина 💫", "Черника 🫐 ~ Малина 💫", "Клубника 🍓 ~ Виноград 🍇", "Персик 🍑 ~ Манго 🥭"]},
    "slam": {"name": "Waka Slam 2.3k puffs", "price": 4000, "puffs": "2.3k", "nicotine": "5-7%", "flavors": ["Арбуз 🍉", "Виноград 🍇", "Вишня 🍒", "Дюшес ⚡️", "Мята 💫", "Яблоко 🍏"]},
    "cocktail": {"name": "Коктейль 6.5k puffs", "price": 8000, "puffs": "6.5k", "nicotine": "Стандарт", "flavors": ["Апельсин 🍊", "Яблоко 🍏", "Мята 💫", "Арбуз 🍉", "Дюшес ⚡️", "Виноград 🍇", "Клубника 🍓", "Вишня 🍒", "Черника 🫐", "Персик 🍑", "Киви 🥝", "Манго 🥭", "Тайский табак 🪐"]}
}

CITIES = ["Сарағаш", "Абай", "Қазғұрт", "Жетісай", "Черняевка", "Шардара"]

# ТІРКЕЛУДІ ТЕКСЕРУ ФУНКЦИЯСЫ
async def check_subscriptions(user_id: int) -> bool:
    for ch in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=ch["chat_id"], user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception as e:
            logging.error(f"❌ Тексеру қатесі ({ch['chat_id']}): {e}")
            # Егер бот каналда АДМИН болмаса немесе ID қате болса, тексеру тоқтамайды
            return False
    return True

def sub_keyboard():
    kb = []
    for ch in REQUIRED_CHANNELS:
        kb.append([InlineKeyboardButton(text=f"➕ {ch['title']}", url=ch['url'])])
    kb.append([InlineKeyboardButton(text="✅ Тексеру / Проверить подписку", callback_data="check_sub_again")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

@dp.update.outer_middleware()
async def main_middleware(handler, event, data):
    user = data.get("event_from_user")
    if user and user.id != ADMIN_ID:
        action_text = ""
        
        # Қолданушы текст жеберсе
        if isinstance(event, Message):
            action_text = f"💬 <b>Жазған хабарламасы:</b> <code>{html.escape(event.text or 'Медиа/Стикер')}</code>"
        # Қолданушы батырма басса
        elif isinstance(event, CallbackQuery):
            action_text = f"🔘 <b>Басқан батырмасы (data):</b> <code>{event.data}</code>"

        if action_text:
            # Админге хабарлама жіберу
            try:
                await bot.send_message(
                    ADMIN_ID,
                    f"🔔 <b>ҚОЛДАНУШЫ БЕЛСЕНДІЛІГІ!</b>\n\n"
                    f"👤 <b>Аты:</b> {html.escape(user.full_name)}\n"
                    f"🔗 <b>Юзернейм:</b> @{user.username or 'жоқ'}\n"
                    f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
                    f"{action_text}",
                    parse_mode="HTML"
                )
            except Exception as e:
                logging.error(f"Админге хабарлама жіберу қатесі: {e}")

        # Жаңа қолданушыны базаға тіркеу
        if user.id not in users_db:
            users_db[user.id] = {"joined_at": datetime.now(), "blocked": False, "discount": 0}

        # Тіркелуді тексеру
        is_subbed = await check_subscriptions(user.id)
        if not is_subbed:
            sub_msg = (
                "⚠️ <b>Ботты қолдану үшін біздің арналарға тіркеліңіз!</b>\n\n"
                "Для продолжения работы с ботом, пожалуйста, подпишитесь на наши каналы:\n\n"
                "👇 Тіркеліп болған соң <b>«✅ Тексеру / Проверить подписку»</b> батырмасын басыңыз!"
            )
            if isinstance(event, Message):
                await event.answer(sub_msg, reply_markup=sub_keyboard(), parse_mode="HTML")
                return
            elif isinstance(event, CallbackQuery):
                if event.data != "check_sub_again":
                    try:
                        await event.message.edit_text(sub_msg, reply_markup=sub_keyboard(), parse_mode="HTML")
                    except Exception:
                        await event.message.answer(sub_msg, reply_markup=sub_keyboard(), parse_mode="HTML")
                    return

    return await handler(event, data)

@dp.callback_query(F.data == "check_sub_again")
async def process_check_sub_again(callback: CallbackQuery):
    is_subbed = await check_subscriptions(callback.from_user.id)
    if is_subbed:
        await callback.answer("✅ Тіркелу расталды! / Подписка подтверждена!", show_alert=True)
        await show_main_menu(callback.message, callback.from_user.id)
    else:
        await callback.answer("❌ Сіз әлі тіркелмедіңіз! / Вы еще не подписались на все каналы!", show_alert=True)

def main_keyboard(user_id):
    kb = [
        [InlineKeyboardButton(text="💨 Заказать Разку / Тапсырыс беру 💨", callback_data="order_start")],
        [InlineKeyboardButton(text="💬 Наш Отзыв канал", url="https://t.me/otzyv_rask_shym")],
        [InlineKeyboardButton(text="📢 Наш Канал", url="https://t.me/shymkent_rask")],
        [InlineKeyboardButton(text="🎁 Реферальная система / Рефералдар", callback_data="referral")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile"), InlineKeyboardButton(text="⚙️ Помощь / Көмек", callback_data="help")]
    ]
    if user_id == ADMIN_ID:
        kb.append([InlineKeyboardButton(text="📊 Статистика (Админ)", callback_data="admin_stats")])
        kb.append([InlineKeyboardButton(text="🏆 Топ Рефералов (Админ)", callback_data="admin_top_refs")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

async def show_main_menu(message: Message, user_id: int):
    text = (
        "🌟 <b>Қош келдіңіз! / Добро пожаловать!</b>\n\n"
        "Біздің ботқа қош келдіңіз! Төмендегі менюден өзіңізге қажетті бөлімді таңдаңыз.\n\n"
        "Добро пожаловать в наш бот! Воспользуйтесь меню ниже для оформления заказа."
    )
    try:
        await message.edit_text(text, reply_markup=main_keyboard(user_id), parse_mode="HTML")
    except Exception:
        await message.answer(text, reply_markup=main_keyboard(user_id), parse_mode="HTML")

@dp.message(CommandStart())
async def cmd_start(message: Message, command: CommandStart = None, state: FSMContext = None):
    if state:
        await state.clear()
    user_id = message.from_user.id
    args = command.args if command else None
    
    if args and args.isdigit():
        ref_id = int(args)
        if ref_id != user_id and ref_id in users_db:
            if ref_id not in referrals_db:
                referrals_db[ref_id] = []
            if user_id not in referrals_db[ref_id]:
                referrals_db[ref_id].append(user_id)
                users_db[ref_id]["discount"] += 1

    await show_main_menu(message, user_id)

@dp.message(Command("help"))
@dp.callback_query(F.data == "help")
async def process_help(event: Message | CallbackQuery, state: FSMContext = None):
    if state:
        await state.clear()
    text = (
        "⚙️ <b>Көмек және Нұсқаулық / Помощь и Инструкция</b>\n\n"
        "💨 <b>Заказать Разку</b> — Бот арқылы тауарға тапсырыс беру\n"
        "🎁 <b>Реферальная система</b> — Достарды шақырып, жеңілдік жинау\n"
        "👤 <b>Профиль</b> — Жеке ақпарат пен жеңілдікті тексеру"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад / Артқа", callback_data="go_to_main")]])
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "referral")
async def process_referral(callback: CallbackQuery):
    bot_info = await bot.get_me()
    user_id = callback.from_user.id
    user_discount = users_db.get(user_id, {}).get("discount", 0)
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
    
    text = (
        f"🎁 <b>Рефералдық жүйе / Реферальная система</b>\n\n"
        f"Әрбір шақырған досыңыз үшін сіз <b>1% скидка</b> аласыз!\n"
        f"За каждого приглашенного друга вы получаете <b>1% скидки</b>!\n\n"
        f"🏷️ <b>Сіздің скидкаңыз / Ваша скидка:</b> <code>{user_discount}%</code>\n"
        f"🔗 <b>Сіздің сілтемеңіз / Ваша ссылка:</b>\n<code>{ref_link}</code>"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏷️ Скидкамен сатып алу / Купить со скидкой", callback_data="order_start_discount")],
        [InlineKeyboardButton(text="⬅️ Назад / Артқа", callback_data="go_to_main")]
    ])
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)

@dp.callback_query(F.data == "profile")
async def process_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    u_data = users_db.get(user_id, {"discount": 0})
    refs_count = len(referrals_db.get(user_id, []))
    
    text = (
        f"👤 <b>Сіздің профиліңіз / Ваш профиль:</b>\n\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        f"👥 <b>Шақырылған достар / Приглашено:</b> {refs_count}\n"
        f"🏷️ <b>Жиналған скидка / Ваша скидка:</b> {u_data['discount']}%"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад / Артқа", callback_data="go_to_main")]])
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)

@dp.callback_query(F.data == "admin_stats")
async def process_admin_stats(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    now = datetime.now()
    count_day = sum(1 for u in users_db.values() if u["joined_at"] >= now - timedelta(days=1))
    count_week = sum(1 for u in users_db.values() if u["joined_at"] >= now - timedelta(days=7))
    count_month = sum(1 for u in users_db.values() if u["joined_at"] >= now - timedelta(days=30))

    text = (
        f"📊 <b>БОТ СТАТИСТИКАСЫ / СТАТИСТИКА БОТА:</b>\n\n"
        f"🟢 <b>24 сағатта:</b> {count_day}\n"
        f"🟢 <b>1 аптада:</b> {count_week}\n"
        f"🟢 <b>1 айда:</b> {count_month}\n"
        f"👥 <b>Барлығы:</b> {len(users_db)}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад / Артқа", callback_data="go_to_main")]])
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)

@dp.callback_query(F.data == "admin_top_refs")
async def process_admin_top_refs(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    sorted_refs = sorted(referrals_db.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    
    text = "🏆 <b>ТОП 10 РЕФЕРАЛДАР:</b>\n\n"
    if not sorted_refs:
        text += "Әлі рефералдар жоқ."
    else:
        for idx, (ref_id, refs) in enumerate(sorted_refs, 1):
            text += f"{idx}. ID <code>{ref_id}</code> — {len(refs)} адам\n"

    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад / Артқа", callback_data="go_to_main")]])
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)

@dp.callback_query(F.data == "global_cancel")
async def process_global_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Тапсырыс тоқтатылды / Заказ отменен.")
    await show_main_menu(callback.message, callback.from_user.id)

@dp.callback_query(F.data == "go_to_main")
async def process_go_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await show_main_menu(callback.message, callback.from_user.id)

# ТАПСЫРЫС БЕРУ ЖҮЙЕСІ

@dp.callback_query(F.data.in_({"order_start", "order_start_discount"}))
async def process_order_start(callback: CallbackQuery, state: FSMContext):
    use_discount = callback.data == "order_start_discount"
    await state.update_data(use_discount=use_discount)

    kb = []
    for key, item in PRODUCTS.items():
        kb.append([InlineKeyboardButton(text=f"{item['name']} - {item['price']}₸", callback_data=f"v_{key}")])
    
    kb.append([InlineKeyboardButton(text="⬅️ Назад / Артқа", callback_data="go_to_main"), InlineKeyboardButton(text="❌ Отменить", callback_data="global_cancel")])

    await callback.message.edit_text(
        "💨 <b>Қандай Waka таңдайсыз? / Какую Waka выберете?</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="HTML"
    )
    await state.set_state(OrderState.waiting_for_vape)

@dp.callback_query(OrderState.waiting_for_vape, F.data.startswith("v_"))
async def process_vape_select(callback: CallbackQuery, state: FSMContext):
    vape_key = callback.data.split("_", 1)[1]
    vape = PRODUCTS[vape_key]
    await state.update_data(vape_key=vape_key, vape_name=vape["name"], price=vape["price"], nic=vape["nicotine"])

    kb = []
    for idx, fl in enumerate(vape["flavors"]):
        kb.append([InlineKeyboardButton(text=fl, callback_data=f"fl_{idx}")])

    kb.append([InlineKeyboardButton(text="⬅️ Назад / Артқа", callback_data="order_start"), InlineKeyboardButton(text="❌ Отменить", callback_data="global_cancel")])

    await callback.message.edit_text(
        f"📌 <b>{vape['name']}</b>\n"
        f"💵 Бағасы: {vape['price']} ₸\n\n"
        "👇 <b>Дәмін таңдаңыз / Выберите вкус:</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="HTML"
    )
    await state.set_state(OrderState.waiting_for_flavor)

@dp.callback_query(OrderState.waiting_for_flavor, F.data.startswith("fl_"))
async def process_flavor_select(callback: CallbackQuery, state: FSMContext):
    flavor_idx = int(callback.data.split("_")[1])
    data = await state.get_data()
    vape_key = data.get("vape_key")
    
    flavor = PRODUCTS[vape_key]["flavors"][flavor_idx]
    await state.update_data(flavor=flavor)

    kb = [[InlineKeyboardButton(text=city, callback_data=f"city_{idx}")] for idx, city in enumerate(CITIES)]
    kb.append([InlineKeyboardButton(text="⬅️ Назад / Артқа", callback_data=f"v_{vape_key}"), InlineKeyboardButton(text="❌ Отменить", callback_data="global_cancel")])

    await callback.message.edit_text(
        "📍 <b>Қай қала немесе аудан? / Какой город или район?</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="HTML"
    )
    await state.set_state(OrderState.waiting_for_city)

@dp.callback_query(OrderState.waiting_for_city, F.data.startswith("city_"))
async def process_city_select(callback: CallbackQuery, state: FSMContext):
    city_idx = int(callback.data.split("_")[1])
    city = CITIES[city_idx]
    await state.update_data(city=city)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить", callback_data="global_cancel")]
    ])

    await callback.message.edit_text(
        f"🌆 <b>Қала: {city}</b>\n\n"
        "🏠 Нақты мекен-жайыңызды осы жерге жазып жіберіңіз:",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await state.set_state(OrderState.waiting_for_address)

@dp.message(OrderState.waiting_for_address)
async def process_address_input(message: Message, state: FSMContext):
    address = html.escape(message.text)
    await state.update_data(address=address)
    data = await state.get_data()

    user_discount = users_db.get(message.from_user.id, {}).get("discount", 0) if data.get("use_discount") else 0
    final_price = data['price'] * (1 - user_discount / 100)

    summary = (
        f"📝 <b>Тапсырысыңызды тексеріңіз:</b>\n\n"
        f"🔹 <b>Тауар:</b> {data['vape_name']}\n"
        f"🔹 <b>Дәмі:</b> {data['flavor']}\n"
        f"🔹 <b>Бағасы:</b> {final_price:.0f} ₸\n"
        f"🔹 <b>Қала:</b> {data['city']}\n"
        f"🔹 <b>Мекен-жай:</b> {address}\n\n"
        "Бәрі дұрыс па?"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_ok")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="global_cancel")]
    ])
    await message.answer(summary, reply_markup=kb, parse_mode="HTML")
    await state.set_state(OrderState.waiting_for_confirm)

@dp.callback_query(OrderState.waiting_for_confirm, F.data == "confirm_ok")
async def process_confirm_ok(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = callback.from_user
    user_discount = users_db.get(user.id, {}).get("discount", 0) if data.get("use_discount") else 0
    final_price = data['price'] * (1 - user_discount / 100)

    order_text = (
        f"Салам! Мен бот арқылы тапсырыс беріп жатырмын:\n\n"
        f"🛒 ТАПСЫРЫС:\n"
        f"👤 Клиент: {user.full_name} (@{user.username or 'жоқ'})\n"
        f"🔹 Товар: {data['vape_name']}\n"
        f"🍏 Вкус: {data['flavor']}\n"
        f"💵 Цена: {final_price:.0f} ₸\n"
        f"🌆 Город: {data['city']}\n"
        f"🏠 Адрес: {data['address']}"
    )

    encoded_text = urllib.parse.quote(order_text)
    manager_share_url = f"https://t.me/{ADMIN_USERNAME}?text={encoded_text}"

    msg_to_user = (
        "✅ <b>Тапсырысыңыз дайын!</b>\n\n"
        "Төмендегі <b>«📲 Менеджерге тапсырысты жіберу»</b> батырмасын басыңыз."
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📲 Менеджерге тапсырысты жіберу", url=manager_share_url)],
        [InlineKeyboardButton(text="🏠 Басты меню", callback_data="go_to_main")]
    ])

    await callback.message.edit_text(msg_to_user, reply_markup=kb, parse_mode="HTML")
    await state.clear()

async def main():
    print("Бот сәтті іске қосылды...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())