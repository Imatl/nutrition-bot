import sqlite3
import asyncio
from contextlib import asynccontextmanager
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from random import sample
from datetime import datetime

bot = Bot(token="7407864836:AAF-cAr-IlMOWj-f8-bPBPz2g2oKhymK3AA")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
class UserProfile(StatesGroup):
    waiting_for_gender = State()
    waiting_for_weight = State()
    waiting_for_height = State()
    waiting_for_age = State()
    waiting_for_activity = State()
    waiting_for_goal = State()
    waiting_for_kcal = State()
    waiting_for_protein = State()
    waiting_for_fat = State()
    waiting_for_carbs = State()
    
class AddMeal(StatesGroup):
    waiting_for_meal_type = State()
    waiting_for_title = State()
    waiting_for_kcal = State()
    waiting_for_protein = State()
    waiting_for_fat = State()
    waiting_for_carbs = State()
    waiting_for_ingredients = State()
    
class DeleteMeal(StatesGroup):
    waiting_for_meal_selection = State()
class Database:
    def __init__(self, db_path="nutrition_bot.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    kcal_target INTEGER,
                    protein_target INTEGER,
                    fat_target INTEGER,
                    carbs_target INTEGER,
                    bmr INTEGER,
                    tdee INTEGER,
                    weight REAL,
                    goal TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS meals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meal_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    kcal INTEGER NOT NULL,
                    protein INTEGER NOT NULL,
                    fat INTEGER NOT NULL,
                    carbs INTEGER NOT NULL,
                    ingredients TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_daily_meals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    meal_id INTEGER,
                    meal_type TEXT,
                    date DATE DEFAULT (date('now')),
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (meal_id) REFERENCES meals (id)
                )
            ''')
            
            conn.commit()
            cursor.execute("SELECT COUNT(*) FROM meals")
            if cursor.fetchone()[0] == 0:
                self.add_initial_meals()
    
    def add_initial_meals(self):
        initial_meals = [
            ("Завтрак", "Овсянка с бананом", 350, 12, 8, 55, "Овсянка 80г, Банан 1шт, Молоко 150мл"),
            ("Завтрак", "Омлет с овощами", 270, 18, 15, 5, "Яйца 2шт, Болгарский перец 50г, Лук 30г, Масло 5мл"),
            ("Завтрак", "Творог с ягодами", 220, 20, 5, 18, "Творог 150г, Ягоды 100г, Мед 10г"),
            ("Завтрак", "Гречневые блины", 320, 15, 12, 38, "Гречневая мука 60г, Яйцо 1шт, Молоко 100мл, Масло 10мл"),
            ("Завтрак", "Смузи протеиновый", 280, 25, 8, 25, "Протеин 30г, Банан 1шт, Овсянка 30г, Молоко 200мл"),

            ("Обед", "Курица с гречкой", 450, 35, 12, 40, "Куриное филе 150г, Гречка 80г, Масло 10мл, Овощи 100г"),
            ("Обед", "Говядина с рисом", 520, 40, 15, 45, "Говядина 150г, Рис 80г, Лук 50г, Морковь 50г"),
            ("Обед", "Рыба с картофелем", 380, 30, 10, 35, "Судак 150г, Картофель 150г, Брокколи 100г, Масло 8мл"),
            ("Обед", "Индейка с макаронами", 470, 38, 14, 42, "Индейка 150г, Макароны 80г, Томаты 100г, Сыр 30г"),
            ("Обед", "Котлеты из телятины", 410, 32, 18, 28, "Телятина 150г, Булгур 70г, Лук 40г, Зелень 20г"),

            ("Ужин", "Творог с ягодами", 250, 20, 5, 15, "Творог 150г, Ягоды 80г, Орехи 15г"),
            ("Ужин", "Куриная грудка с салатом", 280, 30, 8, 12, "Куриная грудка 120г, Салат 100г, Огурцы 80г, Масло 8мл"),
            ("Ужин", "Рыба на пару", 220, 28, 6, 8, "Треска 150г, Спаржа 100г, Лимон 20г, Зелень 10г"),
            ("Ужин", "Омлет с сыром", 320, 22, 20, 6, "Яйца 2шт, Сыр 50г, Шпинат 50г, Масло 8мл"),
            ("Ужин", "Запеканка творожная", 260, 18, 10, 20, "Творог 120г, Яйцо 1шт, Манка 30г, Яблоко 80г")
        ]
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT INTO meals (meal_type, title, kcal, protein, fat, carbs, ingredients)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', initial_meals)
            conn.commit()
    
    def get_user(self, user_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            return cursor.fetchone()
    
    def save_user(self, user_id, username, first_name, kcal, protein, fat, carbs, bmr=None, tdee=None, weight=None, goal=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, username, first_name, kcal_target, protein_target, fat_target, carbs_target, bmr, tdee, weight, goal, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, username, first_name, kcal, protein, fat, carbs, bmr, tdee, weight, goal))
            conn.commit()
    
    def get_meals_by_type(self, meal_type, limit=5):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, kcal, protein, fat, carbs, ingredients
                FROM meals 
                WHERE meal_type = ?
                ORDER BY RANDOM()
                LIMIT ?
            ''', (meal_type, limit))
            return cursor.fetchall()
    
    def get_meal_by_id(self, meal_id):

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM meals WHERE id = ?", (meal_id,))
            return cursor.fetchone()
    
    def save_user_meal_choice(self, user_id, meal_id, meal_type):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM user_daily_meals 
                WHERE user_id = ? AND meal_type = ? AND date = date('now')
            ''', (user_id, meal_type))
            cursor.execute('''
                INSERT INTO user_daily_meals (user_id, meal_id, meal_type)
                VALUES (?, ?, ?)
            ''', (user_id, meal_id, meal_type))
            conn.commit()
    
    def get_user_daily_meals(self, user_id, date=None):
        if date is None:
            date = datetime.now().date()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT m.title, m.kcal, m.protein, m.fat, m.carbs, udm.meal_type
                FROM user_daily_meals udm
                JOIN meals m ON udm.meal_id = m.id
                WHERE udm.user_id = ? AND udm.date = ?
            ''', (user_id, date))
            return cursor.fetchall()
    
    def add_meal(self, meal_type, title, kcal, protein, fat, carbs, ingredients):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO meals (meal_type, title, kcal, protein, fat, carbs, ingredients)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (meal_type, title, kcal, protein, fat, carbs, ingredients))
            conn.commit()
            return cursor.lastrowid

    def delete_meal(self, meal_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_daily_meals WHERE meal_id = ?", (meal_id,))
            cursor.execute("DELETE FROM meals WHERE id = ?", (meal_id,))
            conn.commit()
            return cursor.rowcount > 0 
    
    def get_all_meals_with_count(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT m.id, m.meal_type, m.title, m.kcal, 
                       COUNT(udm.meal_id) as selection_count
                FROM meals m
                LEFT JOIN user_daily_meals udm ON m.id = udm.meal_id
                GROUP BY m.id, m.meal_type, m.title, m.kcal
                ORDER BY m.meal_type, m.title
            ''')
            return cursor.fetchall()
db = Database()
ADMIN_IDS = [479681843]

@dp.message(F.text == "/start")
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    await message.answer(f"Твой user_id: {user_id}")
    user = db.get_user(user_id)
    
    if not user:
        buttons = [
            [KeyboardButton(text="📊 Настроить КБЖУ")],
            [KeyboardButton(text="🍽️ Меню питания")],
            [KeyboardButton(text="📈 Мой прогресс")]
        ]
        if user_id in ADMIN_IDS:
            buttons.append([KeyboardButton(text="👨‍💻 Админ панель")])
        
        keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        await message.answer(
            "Добро пожаловать! 👋\n\n"
            "Я помогу тебе планировать питание по КБЖУ.\n"
            "Сначала настрой свои цели по калориям и макронутриентам.",
            reply_markup=keyboard
        )
    else:
        await show_main_menu(message)
async def show_main_menu(message: types.Message):
    user_id = message.from_user.id
    buttons = [
        [KeyboardButton(text="🍽️ Меню питания")],
        [KeyboardButton(text="📈 Мой прогресс")],
        [KeyboardButton(text="📊 Настроить КБЖУ")]
    ]
    if user_id in ADMIN_IDS:
        buttons.append([KeyboardButton(text="👨‍💻 Админ панель")])
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer("Что хочешь сделать?", reply_markup=keyboard)
@dp.message(F.text == "📊 Настроить КБЖУ")
async def setup_profile(message: types.Message, state: FSMContext):
    buttons = [
        [KeyboardButton(text="🧮 Рассчитать автоматически")],
        [KeyboardButton(text="✏️ Ввести вручную")],
        [KeyboardButton(text="🔙 Назад")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer(
        "Как хочешь настроить КБЖУ?\n\n"
        "🧮 Автоматический расчет - по формуле Миффлина-Сан Жеора\n"
        "✏️ Ручной ввод - если знаешь свои цифры",
        reply_markup=keyboard
    )
@dp.message(F.text == "🧮 Рассчитать автоматически")
async def auto_calculation(message: types.Message, state: FSMContext):
    buttons = [
        [KeyboardButton(text="👨 Мужчина"), KeyboardButton(text="👩 Женщина")],
        [KeyboardButton(text="🔙 Назад")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer("Выбери свой пол:", reply_markup=keyboard)
    await state.set_state(UserProfile.waiting_for_gender)

@dp.message(F.text == "✏️ Ввести вручную")
async def manual_setup(message: types.Message, state: FSMContext):
    await message.answer("Введи свою суточную норму калорий:")
    await state.set_state(UserProfile.waiting_for_kcal)

@dp.message(UserProfile.waiting_for_gender)
async def process_gender(message: types.Message, state: FSMContext):
    if message.text in ["👨 Мужчина", "👩 Женщина"]:
        gender = "male" if message.text == "👨 Мужчина" else "female"
        await state.update_data(gender=gender)
        await message.answer("Введи свой вес в кг (например: 70):")
        await state.set_state(UserProfile.waiting_for_weight)
    else:
        await message.answer("Пожалуйста, выбери пол с помощью кнопок:")

@dp.message(UserProfile.waiting_for_weight)
async def process_weight(message: types.Message, state: FSMContext):
    try:
        weight = float(message.text.replace(',', '.'))
        if weight <= 0 or weight > 300:
            await message.answer("Введи корректный вес (от 1 до 300 кг):")
            return
        await state.update_data(weight=weight)
        await message.answer("Введи свой рост в см (например: 175):")
        await state.set_state(UserProfile.waiting_for_height)
    except ValueError:
        await message.answer("Пожалуйста, введи число (например: 70 или 70.5):")

@dp.message(UserProfile.waiting_for_height)
async def process_height(message: types.Message, state: FSMContext):
    try:
        height = int(message.text)
        if height < 100 or height > 250:
            await message.answer("Введи корректный рост (от 100 до 250 см):")
            return
        await state.update_data(height=height)
        await message.answer("Введи свой возраст (например: 25):")
        await state.set_state(UserProfile.waiting_for_age)
    except ValueError:
        await message.answer("Пожалуйста, введи число:")

@dp.message(UserProfile.waiting_for_age)
async def process_age(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 10 or age > 100:
            await message.answer("Введи корректный возраст (от 10 до 100 лет):")
            return
        await state.update_data(age=age)
        
        buttons = [
            [KeyboardButton(text="😴 Минимальная (сидячий образ жизни)")],
            [KeyboardButton(text="🚶 Слабая (1-3 раза в неделю)")],
            [KeyboardButton(text="🏃 Умеренная (3-5 раз в неделю)")],
            [KeyboardButton(text="💪 Высокая (6-7 раз в неделю)")],
            [KeyboardButton(text="🔥 Экстремальная (2+ раза в день)")]
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        await message.answer("Выбери уровень физической активности:", reply_markup=keyboard)
        await state.set_state(UserProfile.waiting_for_activity)
    except ValueError:
        await message.answer("Пожалуйста, введи число:")

@dp.message(UserProfile.waiting_for_activity)
async def process_activity(message: types.Message, state: FSMContext):
    activity_levels = {
        "😴 Минимальная (сидячий образ жизни)": 1.2,
        "🚶 Слабая (1-3 раза в неделю)": 1.375,
        "🏃 Умеренная (3-5 раз в неделю)": 1.55,
        "💪 Высокая (6-7 раз в неделю)": 1.725,
        "🔥 Экстремальная (2+ раза в день)": 1.9
    }
    
    if message.text in activity_levels:
        activity_factor = activity_levels[message.text]
        await state.update_data(activity_factor=activity_factor)
        
        buttons = [
            [KeyboardButton(text="⬇️ Похудение (-10-20%)")],
            [KeyboardButton(text="⚖️ Поддержание веса")],
            [KeyboardButton(text="⬆️ Набор массы (+10-20%)")]
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        await message.answer("Выбери свою цель:", reply_markup=keyboard)
        await state.set_state(UserProfile.waiting_for_goal)
    else:
        await message.answer("Пожалуйста, выбери уровень активности с помощью кнопок:")

@dp.message(UserProfile.waiting_for_goal)
async def process_goal(message: types.Message, state: FSMContext):
    goal_factors = {
        "⬇️ Похудение (-10-20%)": 0.85,
        "⚖️ Поддержание веса": 1.0,
        "⬆️ Набор массы (+10-20%)": 1.15
    }
    
    if message.text in goal_factors:
        data = await state.get_data()
        user_id = message.from_user.id
        if data['gender'] == 'male':
            bmr = (10 * data['weight']) + (6.25 * data['height']) - (5 * data['age']) + 5
        else:
            bmr = (10 * data['weight']) + (6.25 * data['height']) - (5 * data['age']) - 161
        tdee = bmr * data['activity_factor']
        target_calories = int(tdee * goal_factors[message.text])
        protein = int(data['weight'] * 2)
        fat = int((target_calories * 0.25) / 9)
        remaining_calories = target_calories - (protein * 4) - (fat * 9)
        carbs = int(remaining_calories / 4)
        db.save_user(
            user_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            kcal=target_calories,
            protein=protein,
            fat=fat,
            carbs=carbs,
            bmr=int(bmr),
            tdee=int(tdee),
            weight=data['weight'],
            goal=message.text
        )
        goal_text = {
            "⬇️ Похудение (-10-20%)": "похудения",
            "⚖️ Поддержание веса": "поддержания веса",
            "⬆️ Набор массы (+10-20%)": "набора массы"
        }
        await message.answer(
            f"✅ Расчет завершен!\n\n"
            f"📊 Твои показатели:\n"
            f"⚡ Базовый метаболизм: {int(bmr)} ккал\n"
            f"🔥 Общий расход: {int(tdee)} ккал\n\n"
            f"🎯 Цель: {goal_text[message.text]}\n"
            f"📈 Рекомендуемые значения:\n"
            f"🔥 Калории: {target_calories} ккал\n"
            f"🥩 Белки: {protein}г ({protein*4} ккал)\n"
            f"🥑 Жиры: {fat}г ({fat*9} ккал)\n"
            f"🍞 Углеводы: {carbs}г ({carbs*4} ккал)"
        )
        await state.clear()
        await show_main_menu(message)
    else:
        await message.answer("Пожалуйста, выбери цель с помощью кнопок:")

@dp.message(UserProfile.waiting_for_kcal)
async def process_manual_kcal(message: types.Message, state: FSMContext):
    try:
        kcal = int(message.text)
        if kcal < 800 or kcal > 5000:
            await message.answer("Введи корректное значение калорий (от 800 до 5000):")
            return
        await state.update_data(kcal=kcal)
        await message.answer("Введи норму белка (в граммах):")
        await state.set_state(UserProfile.waiting_for_protein)
    except ValueError:
        await message.answer("Пожалуйста, введи число:")
@dp.message(UserProfile.waiting_for_protein)
async def process_manual_protein(message: types.Message, state: FSMContext):
    try:
        protein = int(message.text)
        if protein < 0 or protein > 500:
            await message.answer("Введи корректное значение белка (от 0 до 500г):")
            return
        await state.update_data(protein=protein)
        await message.answer("Введи норму жиров (в граммах):")
        await state.set_state(UserProfile.waiting_for_fat)
    except ValueError:
        await message.answer("Пожалуйста, введи число:")
@dp.message(UserProfile.waiting_for_fat)
async def process_manual_fat(message: types.Message, state: FSMContext):
    try:
        fat = int(message.text)
        if fat < 0 or fat > 300:
            await message.answer("Введи корректное значение жиров (от 0 до 300г):")
            return
        await state.update_data(fat=fat)
        await message.answer("Введи норму углеводов (в граммах):")
        await state.set_state(UserProfile.waiting_for_carbs)
    except ValueError:
        await message.answer("Пожалуйста, введи число:")
@dp.message(UserProfile.waiting_for_carbs)
async def process_manual_carbs(message: types.Message, state: FSMContext):
    try:
        carbs = int(message.text)
        if carbs < 0 or carbs > 800:
            await message.answer("Введи корректное значение углеводов (от 0 до 800г):")
            return
        
        data = await state.get_data()
        user_id = message.from_user.id
        db.save_user(
            user_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            kcal=data['kcal'],
            protein=data['protein'],
            fat=data['fat'],
            carbs=carbs
        )
        await message.answer(
            f"✅ Профиль настроен вручную!\n\n"
            f"Твои цели:\n"
            f"🔥 Калории: {data['kcal']} ккал\n"
            f"🥩 Белки: {data['protein']}г\n"
            f"🥑 Жиры: {data['fat']}г\n"
            f"🍞 Углеводы: {carbs}г"
        )
        await state.clear()
        await show_main_menu(message)
    except ValueError:
        await message.answer("Пожалуйста, введи число:")

@dp.message(F.text == "🍽️ Меню питания")
async def menu_handler(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user:
        await message.answer("Сначала настрой свой профиль с помощью '📊 Настроить КБЖУ'")
        return
    buttons = [
        [KeyboardButton(text="Завтрак 🍳")],
        [KeyboardButton(text="Обед 🍲")],
        [KeyboardButton(text="Ужин 🍗")],
        [KeyboardButton(text="🔙 Назад")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer("Выбери приём пищи:", reply_markup=keyboard)

def create_meal_keyboard(meals):
    keyboard = []
    for i, meal in enumerate(meals):
        meal_id, title, kcal, protein, fat, carbs, ingredients = meal
        keyboard.append([InlineKeyboardButton(
            text=f"{i+1}. {title} ({kcal} ккал)",
            callback_data=f"view_meal_{meal_id}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def format_meals_list(meals):
    text = ""
    for i, meal in enumerate(meals):
        meal_id, title, kcal, protein, fat, carbs, ingredients = meal
        text += f"{i+1}. **{title}** ({kcal} ккал)\n"
    return text

@dp.message(F.text == "Завтрак 🍳")
async def breakfast_handler(message: types.Message):
    meals = db.get_meals_by_type("Завтрак")
    if not meals:
        await message.answer("Пока нет блюд для завтрака. Админ может добавить через админ панель.")
        return
    meals_text = "🍳 **Варианты завтраков:**\n\n" + format_meals_list(meals)
    meals_text += "\nНажми на блюдо для подробностей:"
    keyboard = create_meal_keyboard(meals)
    await message.answer(meals_text, reply_markup=keyboard, parse_mode="Markdown")

@dp.message(F.text == "Обед 🍲")
async def lunch_handler(message: types.Message):
    meals = db.get_meals_by_type("Обед")
    if not meals:
        await message.answer("Пока нет блюд для обеда. Админ может добавить через админ панель.")
        return
    meals_text = "🍲 **Варианты обедов:**\n\n" + format_meals_list(meals)
    meals_text += "\nНажми на блюдо для подробностей:"
    keyboard = create_meal_keyboard(meals)
    await message.answer(meals_text, reply_markup=keyboard, parse_mode="Markdown")

@dp.message(F.text == "Ужин 🍗")
async def dinner_handler(message: types.Message):
    meals = db.get_meals_by_type("Ужин")
    if not meals:
        await message.answer("Пока нет блюд для ужина. Админ может добавить через админ панель.")
        return
    meals_text = "🍗 **Варианты ужинов:**\n\n" + format_meals_list(meals)
    meals_text += "\nНажми на блюдо для подробностей:"
    keyboard = create_meal_keyboard(meals)
    await message.answer(meals_text, reply_markup=keyboard, parse_mode="Markdown")
@dp.callback_query(F.data.startswith("view_meal_"))
async def view_meal_details(callback: types.CallbackQuery):
    meal_id = int(callback.data.split("_")[-1])
    meal = db.get_meal_by_id(meal_id)
    if not meal:
        await callback.answer("Блюдо не найдено!")
        return
    meal_db_id, meal_type, title, kcal, protein, fat, carbs, ingredients, created_at = meal
    recipe = "Приготовь согласно стандартному рецепту для данных ингредиентов."
    
    meal_info = (
        f"🍽️ **{title}**\n\n"
        f"📊 **КБЖУ:**\n"
        f"🔥 {kcal} ккал\n"
        f"🥩 {protein}г белка\n"
        f"🥑 {fat}г жиров\n"
        f"🍞 {carbs}г углеводов\n\n"
        f"🛒 **Ингредиенты:**\n{ingredients}\n\n"
        f"👨‍🍳 **Способ приготовления:**\n{recipe}"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✅ Выбрать это блюдо",
            callback_data=f"select_meal_{meal_id}"
        )],
        [InlineKeyboardButton(
            text="🔙 Назад к списку",
            callback_data=f"back_to_list_{meal_type}"
        )]
    ])
    await callback.message.edit_text(meal_info, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()
@dp.callback_query(F.data.startswith("back_to_list_"))
async def back_to_meal_list(callback: types.CallbackQuery):
    meal_type = callback.data.split("_")[-1]
    
    meals = db.get_meals_by_type(meal_type)
    if not meals:
        await callback.answer("Список блюд пуст!")
        return
    emoji_map = {
        "Завтрак": "🍳",
        "Обед": "🍲", 
        "Ужин": "🍗"
    }
    meals_text = f"{emoji_map.get(meal_type, '🍽️')} **Варианты {meal_type.lower()}ов:**\n\n" + format_meals_list(meals)
    meals_text += "\nНажми на блюдо для подробностей:"
    keyboard = create_meal_keyboard(meals)
    await callback.message.edit_text(meals_text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()
@dp.callback_query(F.data.startswith("select_meal_"))
async def process_meal_selection(callback: types.CallbackQuery):
    meal_id = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    meal = db.get_meal_by_id(meal_id)
    if not meal:
        await callback.answer("Блюдо не найдено!")
        return
    meal_db_id, meal_type, title, kcal, protein, fat, carbs, ingredients, created_at = meal
    
    db.save_user_meal_choice(user_id, meal_id, meal_type)
    
    meal_info = (
        f"✅ **Блюдо добавлено в рацион!**\n\n"
        f"🍽️ {title}\n"
        f"📊 КБЖУ: 🔥{kcal} ккал | 🥩{protein}г | 🥑{fat}г | 🍞{carbs}г\n\n"
        f"Можешь выбрать другие блюда или посмотреть свой прогресс в главном меню."
    )
    await callback.message.edit_text(meal_info, parse_mode="Markdown")
    await callback.answer("Блюдо добавлено в твой рацион!")

@dp.message(F.text == "📈 Мой прогресс")
async def progress_handler(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    if not user:
        await message.answer("Сначала настрой свой профиль!")
        return
    (user_id_db, username, first_name, kcal_target, protein_target, 
     fat_target, carbs_target, bmr, tdee, weight, goal, created_at, updated_at) = user
    daily_meals = db.get_user_daily_meals(user_id)
    
    if not daily_meals:
        await message.answer("Ты еще не выбрал ни одного блюда сегодня.")
        return
    total_kcal = sum(meal[1] for meal in daily_meals)
    total_protein = sum(meal[2] for meal in daily_meals)
    total_fat = sum(meal[3] for meal in daily_meals)
    total_carbs = sum(meal[4] for meal in daily_meals)
    selected_meals = [f"• {meal[0]} ({meal[5]})" for meal in daily_meals]
    kcal_diff = kcal_target - total_kcal
    protein_diff = protein_target - total_protein
    fat_diff = fat_target - total_fat
    carbs_diff = carbs_target - total_carbs
    
    progress_text = f"📊 Твой прогресс на сегодня:\n\n"
    
    if selected_meals:
        progress_text += "🍽️ Выбранные блюда:\n" + "\n".join(selected_meals) + "\n\n"
    if bmr and tdee:
        progress_text += (
            f"ℹ️ Справка:\n"
            f"⚡ Базовый метаболизм: {bmr} ккал\n"
            f"🔥 Общий расход: {tdee} ккал\n"
            f"🎯 Цель: {goal or 'не указана'}\n\n"
        )
    progress_text += (
        f"📈 КБЖУ:\n"
        f"🔥 Калории: {total_kcal}/{kcal_target} "
        f"({'недобор ' + str(abs(kcal_diff)) if kcal_diff > 0 else 'перебор ' + str(abs(kcal_diff)) if kcal_diff < 0 else 'норма ✅'})\n"
        f"🥩 Белки: {total_protein}/{protein_target}г "
        f"({'недобор ' + str(abs(protein_diff)) if protein_diff > 0 else 'перебор ' + str(abs(protein_diff)) if protein_diff < 0 else 'норма ✅'})\n"
        f"🥑 Жиры: {total_fat}/{fat_target}г "
        f"({'недобор ' + str(abs(fat_diff)) if fat_diff > 0 else 'перебор ' + str(abs(fat_diff)) if fat_diff < 0 else 'норма ✅'})\n"
        f"🍞 Углеводы: {total_carbs}/{carbs_target}г "
        f"({'недобор ' + str(abs(carbs_diff)) if carbs_diff > 0 else 'перебор ' + str(abs(carbs_diff)) if carbs_diff < 0 else 'норма ✅'})\n"
    )
    
    await message.answer(progress_text)
@dp.message(F.text == "👨‍💻 Админ панель")
async def admin_panel(message: types.Message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        await message.answer("У тебя нет доступа к админ панели!")
        return
    
    buttons = [
        [KeyboardButton(text="➕ Добавить блюдо")],
        [KeyboardButton(text="🗑️ Удалить блюдо")],
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="🔙 Назад")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer("Админ панель:", reply_markup=keyboard)
@dp.message(F.text == "➕ Добавить блюдо")
async def add_meal_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        return
    buttons = [
        [KeyboardButton(text="Завтрак"), KeyboardButton(text="Обед"), KeyboardButton(text="Ужин")],
        [KeyboardButton(text="🔙 Назад")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer("Выбери тип блюда:", reply_markup=keyboard)
    await state.set_state(AddMeal.waiting_for_meal_type)

@dp.message(AddMeal.waiting_for_meal_type)
async def process_meal_type(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.clear()
        await admin_panel(message)
        return
        
    if message.text in ["Завтрак", "Обед", "Ужин"]:
        await state.update_data(meal_type=message.text)
        await message.answer("Введи название блюда:")
        await state.set_state(AddMeal.waiting_for_title)
    else:
        await message.answer("Выбери тип блюда из предложенных:")

@dp.message(AddMeal.waiting_for_title)
async def process_meal_title(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.clear()
        await show_main_menu(message)
        return
    await state.update_data(title=message.text)
    await message.answer("Введи калорийность (ккал):")
    await state.set_state(AddMeal.waiting_for_kcal)

@dp.message(AddMeal.waiting_for_kcal)
async def process_meal_kcal(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.clear()
        await show_main_menu(message)
        return
    try:
        kcal = int(message.text)
        if kcal < 0 or kcal > 2000:
            await message.answer("Введи корректное значение калорий (от 0 до 2000):")
            return
        await state.update_data(kcal=kcal)
        await message.answer("Введи количество белка (г):")
        await state.set_state(AddMeal.waiting_for_protein)
    except ValueError:
        await message.answer("Пожалуйста, введи число:")

@dp.message(AddMeal.waiting_for_protein)
async def process_meal_protein(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.clear()
        await show_main_menu(message)
        return
    try:
        protein = int(message.text)
        if protein < 0 or protein > 200:
            await message.answer("Введи корректное значение белка (от 0 до 200г):")
            return
        await state.update_data(protein=protein)
        await message.answer("Введи количество жиров (г):")
        await state.set_state(AddMeal.waiting_for_fat)
    except ValueError:
        await message.answer("Пожалуйста, введи число:")

@dp.message(AddMeal.waiting_for_fat)
async def process_meal_fat(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.clear()
        await show_main_menu(message)
        return
    try:
        fat = int(message.text)
        if fat < 0 or fat > 100:
            await message.answer("Введи корректное значение жиров (от 0 до 100г):")
            return
        await state.update_data(fat=fat)
        await message.answer("Введи количество углеводов (г):")
        await state.set_state(AddMeal.waiting_for_carbs)
    except ValueError:
        await message.answer("Пожалуйста, введи число:")

@dp.message(AddMeal.waiting_for_carbs)
async def process_meal_carbs(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.clear()
        await show_main_menu(message)
        return
    try:
        carbs = int(message.text)
        if carbs < 0 or carbs > 200:
            await message.answer("Введи корректное значение углеводов (от 0 до 200г):")
            return
        await state.update_data(carbs=carbs)
        await message.answer("Введи ингредиенты (через запятую):")
        await state.set_state(AddMeal.waiting_for_ingredients)
    except ValueError:
        await message.answer("Пожалуйста, введи число:")

@dp.message(AddMeal.waiting_for_ingredients)
async def process_meal_ingredients(message: types.Message, state: FSMContext):
    data = await state.get_data()
    meal_id = db.add_meal(
        meal_type=data['meal_type'],
        title=data['title'],
        kcal=data['kcal'],
        protein=data['protein'],
        fat=data['fat'],
        carbs=data['carbs'],
        ingredients=message.text
    )
    await message.answer(
        f"✅ Блюдо добавлено!\n\n"
        f"📝 {data['title']} ({data['meal_type']})\n"
        f"🔥 {data['kcal']} ккал\n"
        f"🥩 {data['protein']}г белка\n"
        f"🥑 {data['fat']}г жиров\n"
        f"🍞 {data['carbs']}г углеводов\n"
        f"🛒 {message.text}"
    )
    await state.clear()
    await show_main_menu(message)
@dp.message(F.text == "🗑️ Удалить блюдо")
async def delete_meal_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        return
    meals = db.get_all_meals_with_count()
    if not meals:
        await message.answer("Нет блюд для удаления!")
        return
    grouped_meals = {}
    for meal in meals:
        meal_id, meal_type, title, kcal, selection_count = meal
        if meal_type not in grouped_meals:
            grouped_meals[meal_type] = []
        grouped_meals[meal_type].append({
            'id': meal_id,
            'title': title,
            'kcal': kcal,
            'selection_count': selection_count
        })
    delete_text = "🗑️ **Удаление блюд**\n\n"
    delete_text += "⚠️ *При удалении блюда оно исчезнет из рационов всех пользователей!*\n\n"
    
    keyboard = []
    
    for meal_type, meals_list in grouped_meals.items():
        delete_text += f"**{meal_type}:**\n"
        for meal in meals_list:
            usage_text = f"(выбирали {meal['selection_count']} раз)" if meal['selection_count'] > 0 else "(не выбирали)"
            delete_text += f"• {meal['title']} - {meal['kcal']} ккал {usage_text}\n"
            button_text = f"❌ {meal['title']}"
            if meal['selection_count'] > 0:
                button_text += f" ({meal['selection_count']})"
            keyboard.append([InlineKeyboardButton(
                text=button_text,
                callback_data=f"delete_meal_{meal['id']}"
            )])
        delete_text += "\n"
    keyboard.append([InlineKeyboardButton(
        text="🔙 Отмена",
        callback_data="cancel_delete"
    )])
    
    reply_keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(delete_text, reply_markup=reply_keyboard, parse_mode="Markdown")
    await state.set_state(DeleteMeal.waiting_for_meal_selection)
@dp.callback_query(F.data.startswith("delete_meal_"))
async def confirm_meal_deletion(callback: types.CallbackQuery):
    meal_id = int(callback.data.split("_")[-1])
    meal = db.get_meal_by_id(meal_id)
    if not meal:
        await callback.answer("Блюдо не найдено!")
        return
    meal_db_id, meal_type, title, kcal, protein, fat, carbs, ingredients, created_at = meal
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM user_daily_meals WHERE meal_id = ?", (meal_id,))
        usage_count = cursor.fetchone()[0]
    
    confirm_text = (
        f"⚠️ **Подтверждение удаления**\n\n"
        f"🍽️ **Блюдо:** {title}\n"
        f"📊 **КБЖУ:** {kcal} ккал\n"
        f"📈 **Использовалось:** {usage_count} раз\n\n"
        f"🚨 **Внимание!** Это действие нельзя отменить.\n"
        f"Блюдо исчезнет из рационов всех пользователей."
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🗑️ Да, удалить",
            callback_data=f"confirm_delete_{meal_id}"
        )],
        [InlineKeyboardButton(
            text="❌ Отмена",
            callback_data="cancel_delete"
        )]
    ])
    
    await callback.message.edit_text(confirm_text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()
@dp.callback_query(F.data.startswith("confirm_delete_"))
async def final_meal_deletion(callback: types.CallbackQuery, state: FSMContext):
    meal_id = int(callback.data.split("_")[-1])
    meal = db.get_meal_by_id(meal_id)
    if not meal:
        await callback.answer("Блюдо не найдено!")
        return
    title = meal[2] 
    success = db.delete_meal(meal_id)
    
    if success:
        await callback.message.edit_text(
            f"✅ **Блюдо удалено!**\n\n"
            f"🗑️ \"{title}\" больше не доступно в боте.\n"
            f"Все связанные записи пользователей также удалены.",
            parse_mode="Markdown"
        )
        await callback.answer("Блюдо успешно удалено!")
    else:
        await callback.message.edit_text("❌ Ошибка при удалении блюда.")
        await callback.answer("Ошибка удаления!")
    
    await state.clear()

@dp.callback_query(F.data == "cancel_delete")
async def cancel_deletion(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Удаление отменено.")
    await callback.answer("Операция отменена")
    await state.clear()
async def admin_stats(message: types.Message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        return
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM meals")
        total_meals = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM user_daily_meals WHERE date = date('now')")
        today_selections = cursor.fetchone()[0]
        cursor.execute("SELECT meal_type, COUNT(*) FROM meals GROUP BY meal_type")
        meals_by_type = cursor.fetchall()
        stats_text = (
            f"📊 Статистика бота:\n\n"
            f"👥 Всего пользователей: {total_users}\n"
            f"🍽️ Всего блюд: {total_meals}\n"
            f"📅 Выборов сегодня: {today_selections}\n\n"
            f"📈 Блюда по типам:\n"
        )
        
        for meal_type, count in meals_by_type:
            stats_text += f"• {meal_type}: {count}\n"
    
    await message.answer(stats_text)
@dp.message(F.text == "🔙 Назад")
async def back_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    await show_main_menu(message)
async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(main())