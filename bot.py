import os
import telebot
import requests
from flask import Flask
import threading
import sqlite3
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

app = Flask('')

@app.route('/')
def home():
    return "OK"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_flask).start()

API_TOKEN = "8591551561:AAG__1Pmpjx0HuYvEnR3K3mC_uaAS6ZTjm8"
bot = telebot.TeleBot(API_TOKEN)

# Your Admin Telegram ID and UPI Details
ADMIN_ID = 8380823727
YOUR_UPI_ID = "orthodontist@airtel"

# यहाँ आप अपने QR कोड का डायरेक्ट इमेज लिंक (Direct Image URL) या Telegram File ID डाल सकते हैं। 
# अभी यहाँ एक स्टैंडर्ड UPI QR जनरेटर लिंक लगा दिया गया है ताकि यह ऑटोमैटिक काम करे!
QR_CODE_URL = "https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa=orthodontist@airtel&pn=Ariful%20Islam%20Khan"

# Global variable to control bot status
bot_active = True

# --- Database Setup for Wallet Balance ---
def init_db():
    conn = sqlite3.connect('bot_wallet.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            username TEXT,
            balance REAL DEFAULT 0.0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_user_balance(user_id, name="User", username="None"):
    conn = sqlite3.connect('bot_wallet.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    if row is None:
        cursor.execute('INSERT INTO users (user_id, name, username, balance) VALUES (?, ?, ?, ?)', (user_id, name, username, 0.0))
        conn.commit()
        balance = 0.0
    else:
        balance = row[0]
    conn.close()
    return balance

def update_user_balance(user_id, amount):
    conn = sqlite3.connect('bot_wallet.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    if row is None:
        cursor.execute('INSERT INTO users (user_id, name, username, balance) VALUES (?, ?, ?, ?)', (user_id, "User", "None", amount))
    else:
        new_balance = row[0] + amount
        cursor.execute('UPDATE users SET balance = ? WHERE user_id = ?', (new_balance, user_id))
    conn.commit()
    conn.close()

def get_reply_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn_menu = KeyboardButton("📂 Menu / Dashboard")
    markup.add(btn_menu)
    return markup

@bot.message_handler(commands=['off'])
def off_command(message):
    if message.from_user is None or message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Only the owner can use this command!")
        return
    global bot_active
    bot_active = False
    bot.reply_to(message, "🔴 Bot services are now OFF.")

@bot.message_handler(commands=['on'])
def on_command(message):
    if message.from_user is None or message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Only the owner can use this command!")
        return
    global bot_active
    bot_active = True
    bot.reply_to(message, "🟢 Bot services are now ON.")

@bot.message_handler(func=lambda message: message.text == "📂 Menu / Dashboard")
@bot.message_handler(commands=['start', 'menu'])
def menu_command(message):
    user = message.from_user
    user_name = user.first_name if user else "User"
    username = user.username if user and user.username else "None"
    
    balance = get_user_balance(user.id, user_name, username)
    
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    
    btn_shop = InlineKeyboardButton("🛒 Shop", callback_data="shop_menu")
    btn_balance = InlineKeyboardButton("💳 Add Balance", callback_data="add_balance")
    btn_orders = InlineKeyboardButton("📦 My Orders", callback_data="my_orders")
    btn_profile = InlineKeyboardButton("👤 Profile", callback_data="my_profile")
    btn_support = InlineKeyboardButton("💬 Support", callback_data="support_menu")
    
    markup.add(btn_shop, btn_balance, btn_orders, btn_profile, btn_support)
    
    menu_text = f"""🛒 <b>— OFFICIAL MOMSHAD STORE —</b> 🛒

✨ <i>Hello, {user_name}!</i>

🔑 Premium digital keys, instant delivery.

• 🛍️ Wide product catalog
• ⚡ Instant key delivery
• 💳 Multiple payment gateways
• 💰 <b>Wallet Balance: ₹{balance}</b>
• 🔒 24/7 admin support

<i>Tap any button below to begin.</i>"""
    
    bot.send_message(message.chat.id, menu_text, parse_mode='HTML', reply_markup=markup)
    bot.send_message(message.chat.id, "👇 Tap the Menu button below anytime:", reply_markup=get_reply_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user = call.from_user
    balance = get_user_balance(user.id, user.first_name, user.username if user.username else "None")

    if call.data == "shop_menu":
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        
        btn_free = InlineKeyboardButton("🎁 20+ Free Likes", callback_data="free_likes")
        btn_paid = InlineKeyboardButton("💎 220+ Likes - ₹10", callback_data="paid_likes")
        btn_back = InlineKeyboardButton("« Back to Menu", callback_data="main_menu")
        
        markup.add(btn_free, btn_paid, btn_back)
        
        try:
            bot.edit_message_text(
                f"🛍️ <b>STORE & PRICING PLAN</b>\n💰 Wallet Balance: ₹{balance}\n\nSelect your preferred package below:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='HTML',
                reply_markup=markup
            )
        except Exception:
            pass
            
    elif call.data == "free_likes":
        bot.answer_callback_query(call.id, "Free Likes selected!")
        bot.send_message(
            call.message.chat.id, 
            "🎁 <b>How to get Free Likes:</b>\n\n📌 Format: <code>/like ind [Your UID]</code>\n💡 Example: <code>/like ind 1772894853</code>\n\n(This is completely free!)", 
            parse_mode='HTML'
        )
        
    elif call.data == "paid_likes":
        bot.answer_callback_query(call.id, "Paid Plan selected")
        paid_caption = f"""💎 <b>PREMIUM LIKE PACKAGE</b>

📦 <b>Package:</b> 220+ Likes
💰 <b>Price:</b> ₹10 Only
💳 <b>Your Wallet Balance:</b> ₹{balance}

1️⃣ <b>Scan QR Code above or Pay to UPI ID:</b>
📌 UPI ID: <code>{YOUR_UPI_ID}</code>
👤 Name: <b>Ariful Islam Khan</b>

2️⃣ <b>Submit UTR after payment:</b>
👉 <code>/utr [12-digit UTR] [Your UID] [Region]</code>
💡 <i>Example:</i> <code>/utr 412345678912 1772894853 ind</code>

✨ <i>Likes will be credited after manual verification!</i>"""
        bot.send_photo(call.message.chat.id, QR_CODE_URL, caption=paid_caption, parse_mode='HTML')
        
    elif call.data == "main_menu":
        user_name = user.first_name if user else "User"
        bot.answer_callback_query(call.id, "⚡ Dashboard loaded successfully!")
        
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        
        btn_shop = InlineKeyboardButton("🛒 Shop", callback_data="shop_menu")
        btn_balance = InlineKeyboardButton("💳 Add Balance", callback_data="add_balance")
        btn_orders = InlineKeyboardButton("📦 My Orders", callback_data="my_orders")
        btn_profile = InlineKeyboardButton("👤 Profile", callback_data="my_profile")
        btn_support = InlineKeyboardButton("💬 Support", callback_data="support_menu")
        
        markup.add(btn_shop, btn_balance, btn_orders, btn_profile, btn_support)
        
        menu_text = f"""🛒 <b>— OFFICIAL MOMSHAD STORE —</b> 🛒

✨ <i>Hello, {user_name}!</i>

🔑 Premium digital keys, instant delivery.

• 🛍️ Wide product catalog
• ⚡ Instant key delivery
• 💳 Multiple payment gateways
• 💰 <b>Wallet Balance: ₹{balance}</b>
• 🔒 24/7 admin support

<i>Tap any button below to begin.</i>"""
        try:
            bot.edit_message_text(
                menu_text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='HTML',
                reply_markup=markup
            )
        except Exception:
            pass

    elif call.data == "add_balance":
        bot.answer_callback_query(call.id, "Select amount to add")
        markup = InlineKeyboardMarkup()
        markup.row_width = 3
        
        btn_50 = InlineKeyboardButton("➕ ₹50", callback_data="add_50")
        btn_100 = InlineKeyboardButton("➕ ₹100", callback_data="add_100")
        btn_200 = InlineKeyboardButton("➕ ₹200", callback_data="add_200")
        btn_back = InlineKeyboardButton("« Back to Menu", callback_data="main_menu")
        
        markup.add(btn_50, btn_100, btn_200, btn_back)
        
        try:
            bot.edit_message_text(
                f"💳 <b>ADD WALLET BALANCE</b>\n💰 Current Balance: ₹{balance}\n\nSelect amount to top-up your wallet:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='HTML',
                reply_markup=markup
            )
        except Exception:
            pass

    elif call.data in ["add_50", "add_100", "add_200"]:
        amounts = {"add_50": "50", "add_100": "100", "add_200": "200"}
        amt = amounts[call.data]
        bot.answer_callback_query(call.id, f"Rs. {amt} selected")
        
        pay_caption = f"""💳 <b>TOP-UP ₹{amt}</b>

📦 <b>Amount:</b> ₹{amt}
💰 <b>Current Balance:</b> ₹{balance}

1️⃣ <b>Scan QR Code above or Pay to UPI ID:</b>
📌 UPI ID: <code>{YOUR_UPI_ID}</code>
👤 Name: <b>Ariful Islam Khan</b>

2️⃣ <b>Send Transaction UTR:</b>
👉 <code>/utr [UTR Number] [Your UID] [Region]</code>

✨ <i>Balance will be updated after confirmation.</i>"""
        
        bot.send_photo(call.message.chat.id, QR_CODE_URL, caption=pay_caption, parse_mode='HTML')

    elif call.data == "my_orders":
        bot.answer_callback_query(call.id, "Loading orders...")
        bot.send_message(call.message.chat.id, "📦 <b>MY ORDERS</b>\n\nYou have no active orders right now.", parse_mode='HTML')
        
    elif call.data == "my_profile":
        bot.answer_callback_query(call.id, "Loading profile...")
        profile_text = f"""👤 <b>USER PROFILE</b>

🆔 <b>Telegram ID:</b> <code>{user.id}</code>
📛 <b>Name:</b> {user.first_name}
🔗 <b>Username:</b> @{user.username if user.username else 'None'}
💰 <b>Wallet Balance: ₹{balance}</b>"""
        bot.send_message(call.message.chat.id, profile_text, parse_mode='HTML')

    elif call.data == "support_menu":
        bot.answer_callback_query(call.id, "Opening support...")
        support_text = f"""💬 <b>CUSTOMER SUPPORT</b>

Need assistance with orders or payments? 
Reach out to the admin directly:

👑 <b>Support Desk:</b> @Momshad_00"""
        bot.send_message(call.message.chat.id, support_text, parse_mode='HTML')

@bot.message_handler(commands=['addbalance'])
def admin_add_balance(message):
    if message.from_user is None or message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Only the owner can use this command!")
        return
        
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "❌ <b>Usage:</b> <code>/addbalance [User ID] [Amount]</code>", parse_mode='HTML')
        return
        
    try:
        target_user_id = int(args[1])
        amount = float(args[2])
        
        update_user_balance(target_user_id, amount)
        bot.reply_to(message, f"✅ Successfully added ₹{amount} to user ID <code>{target_user_id}</code>", parse_mode='HTML')
        
        try:
            bot.send_message(target_user_id, f"🎉 <b>WALLET UPDATED!</b>\n\nAdmin has added <b>₹{amount}</b> to your wallet balance.", parse_mode='HTML')
        except Exception:
            pass
            
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = f"""📖 <b>HELP & COMMANDS</b>

🔹 <code>/like [region] [uid]</code> - Free Likes
🔹 <code>/utr [utr] [uid] [region]</code> - Submit UTR
🔹 <code>/menu</code> - Open Dashboard

<b>[Admin Commands]</b>
🔸 <code>/addbalance [user_id] [amount]</code> - Add Balance
🔸 <code>/on</code> - Start Bot Services
🔸 <code>/off</code> - Stop Bot Services"""
    bot.reply_to(message, help_text, parse_mode='HTML')

@bot.message_handler(commands=['utr'])
def handle_utr(message):
    args = message.text.split()
    if len(args) < 4:
        bot.reply_to(message, "❌ <b>Invalid Format!</b>\nCorrect usage: <code>/utr [UTR Number] [UID] [Region]</code>", parse_mode='HTML')
        return

    utr_number = args[1]
    uid = args[2]
    region = args[3].lower()
    user = message.from_user

    admin_msg = f"""💰 <b>NEW PAYMENT RECEIVED</b>

👤 <b>Name:</b> {user.first_name}
🆔 <b>ID:</b> <code>{user.id}</code>
🔗 <b>Username:</b> @{user.username if user.username else 'None'}

💳 <b>UTR:</b> <code>{utr_number}</code>
🎮 <b>UID:</b> <code>{uid}</code>
🌍 <b>Region:</b> {region.upper()}

👉 <i>Use <code>/addbalance {user.id} [Amount]</code> to credit money.</i>"""

    bot.send_message(ADMIN_ID, admin_msg, parse_mode='HTML')
    bot.reply_to(message, "✅ <b>UTR Submitted Successfully!</b>\nYour payment is under verification by the admin.", parse_mode='HTML')

@bot.message_handler(commands=['like'])
def handle_like(message):
    if not bot_active:
        bot.reply_to(message, "⚠️ Bot is currently offline. Send /on to start it.")
        return

    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "⚠️ <b>Invalid Format!</b>\nUse: <code>/like ind [Your UID]</code>", parse_mode='HTML')
        return

    region = args[1].lower()
    uid = args[2]

    sent_msg = bot.reply_to(message, "⏳ Processing your request...")
    api_url = f"https://like-apii-one.vercel.app/like?uid={uid}&server_name={region}"

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(api_url, headers=headers)
        data = response.json()

        name = str(data.get('PlayerNickname', 'Unknown'))
        likes_before = str(data.get('LikesbeforeCommand', '0'))
        likes_given = str(data.get('LikesGivenByAPI', '0'))
        likes_after = str(data.get('LikesafterCommand', '0'))
        remaining = str(data.get('Remaining_requests', '0'))

        if int(likes_after) > int(likes_before) or int(likes_given) > 0:
            reply_text = f"""🎉 <b>LIKE SUCCESSFUL</b>

👑 <b>Name:</b> {name}
🎮 <b>UID:</b> {uid}
🌍 <b>Region:</b> {region.upper()}

❤️ <b>Before:</b> {likes_before}
💙 <b>Given:</b> {likes_given}
💚 <b>After:</b> {likes_after}
⚡ <b>Remaining:</b> {remaining}"""
        else:
            reply_text = f"""⚠️ <b>LIMIT REACHED</b>

👤 <b>Name:</b> {name}
🆔 <b>UID:</b> {uid}
🌍 <b>Server:</b> {region.upper()}

📊 <b>Status:</b> 0 Likes Added"""

        bot.edit_message_text(reply_text, chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, parse_mode='HTML')

    except Exception as e:
        bot.edit_message_text(f"❌ <b>API Error:</b> {str(e)}", chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, parse_mode='HTML')

if __name__ == '__main__':
    bot.infinity_polling(skip_pending=True)
    
