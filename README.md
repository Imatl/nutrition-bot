# Nutrition Bot - Telegram bot for meal planning

A bot for calculating calories and planning meals based on personal goals.

### 👤 For users:
- 🧮 **Automatic calorie calculation** using the Mifflin-St. Jeor formula
- ✏️ **Manual entry** of target values
- 🍳 **Selection of dishes** from a ready-made database (breakfast/lunch/dinner)
- 📊 **Progress tracking** - how much has been eaten vs. the goal
- 📈 **Calculation of deficit/surplus** for each macronutrient
- 📱 **Intuitive interface** with detailed information about dishes

### 👨‍💻 For administrators:
- ➕ **Adding new dishes** with complete KBZHU information
- 🗑️ **Deleting dishes** with confirmation and usage statistics
- 📊 **Usage statistics** for the bot and dish popularity

## 📦 Installation

### 1. Clone the repository:
```bash
git clone https://github.com/your-username/nutrition-bot.git
cd nutrition-bot
```

### 2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

### 3. Set dependencies:
```bash
pip install -r requirements.txt
```

### 4. Bot configuration:

#### Create a `.env` file:
```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_user_id
```

#### Or changes in the `main.py` code:
```python
bot = Bot(token="YOUR_BOT_TOKEN")
ADMIN_IDS = [YOUR_USER_ID]  # Твой Telegram user_id
```

### 5. Launch:
```bash
python main.py
```

## ⚙️ Settings

#### Obtaining a bot token:
1. Write [@BotFather](https://t.me/BotFather) in Telegram
2. Create a new bot with the command `/newbot`
3. Copy the token you receive

### Obtaining your user_id:
1. Write to [@userinfobot](https://t.me/userinfobot)
2. Copy your ID to add it to `ADMIN_IDS`

## 📊 Database

The bot automatically creates an SQLite database with the following tables:
- `users` - user profiles and their KBZHU goals
- `meals` - database of meals with complete information
- `user_daily_meals` - selected meals by day

## 📱 Bot commands

- `/start` - launch and main menu
- `📊 Set up KBZHU` - calculation or manual entry of goals
- `🍽️ Food menu` - selection of dishes
- `📈 My progress` - statistics for the day
- `👨‍💻 Admin panel` - meal management (for admins only)

## 🔧 Development

### Project structure:
```
nutrition-bot/
├── main.py              # Main bot file
├── requirements.txt     # Dependencies
├── .env                # Configuration (not in git)
├── .gitignore          # Exclusions for git
├── README.md           # Documentation
└── nutrition_bot.db    # Database (created automatically)
```
