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

API_TOKEN = "8591551561:AAG0HuGmuJ84qtjo9NYSjFT-jYQcqGf8QBU"
bot = telebot.TeleBot(API_TOKEN)

# Your Admin Telegram ID and UPI Details
ADMIN_ID = 8380823727
YOUR_UPI_ID = "orthodontist@airtel"
QR_CODE_URL = "https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa=orthodontist@airtel&pn=Ariful%20Islam%20Khan"

# Global variable to control bot status
bot_active = True

# --- Database Setup for Wallet & Orders ---
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_name TEXT,
            price REAL,
            status TEXT
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

def add_order_to_db(user_id, item_name, price, status="Completed"):
    conn = sqlite3.connect('bot_wallet.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO orders (user_id, item_name, price, status) VALUES (?, ?, ?, ?)', (user_id, item_name, price, status))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('bot_wallet.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_user_orders(user_id):
    conn = sqlite3.connect('bot_wallet.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT item_name, price, status FROM orders WHERE user_id = ? ORDER BY order_id DESC LIMIT 5', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

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
        btn_paid = InlineKeyboardButton("💎 220+ Likes - ₹10 (Wallet Pay)", callback_data="paid_likes")
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
        bot.answer_callback_query(call.id, "Enter your UID for Free Likes")
        msg = bot.send_message(
            call.message.chat.id, 
            "🎮 <b>Please enter your Free Fire UID:</b>\n(Example: <code>1772894853</code>)", 
            parse_mode='HTML'
        )
        bot.register_next_step_handler(msg, process_free_like_uid)
        
    elif call.data == "paid_likes":
        package_price = 10.0
        if balance >= package_price:
            update_user_balance(user.id, -package_price)
            add_order_to_db(user.id, "220+ Likes Package", package_price, "Success")
            new_bal = balance - package_price
            
            bot.answer_callback_query(call.id, "Payment Successful via Wallet! 🎉", show_alert=True)
            
            msg = bot.send_message(
                call.message.chat.id,
                f"✅ <b>PAYMENT SUCCESSFUL!</b>\n\n💎 <b>Package:</b> 220+ Likes\n💸 <b>Amount Deducted:</b> ₹{package_price}\n💰 <b>Remaining Wallet Balance:</b> ₹{new_bal}\n\n🎮 <b>Please enter your Free Fire UID to get your likes:</b>",
                parse_mode='HTML'
            )
            bot.register_next_step_handler(msg, process_paid_like_uid)
        else:
            bot.answer_callback_query(call.id, "Insufficient balance! Please add balance.", show_alert=True)
            paid_caption = f"""💎 <b>PREMIUM LIKE PACKAGE</b>

📦 <b>Package:</b> 220+ Likes
💰 <b>Price:</b> ₹10 Only
💳 <b>Your Wallet Balance:</b> ₹{balance}

❌ <b>Insufficient Balance in Wallet!</b> 
You can pay via UPI QR below and submit UTR:

1️⃣ <b>Scan QR Code above or Pay to UPI ID:</b>
📌 UPI ID: <code>{YOUR_UPI_ID}</code>
👤 Name: <b>Ariful Islam Khan</b>

2️⃣ <b>Submit UTR after payment:</b>
👉 <code>/utr [12-digit UTR] [Your UID] [Region]</code>"""
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
        orders = get_user_orders(user.id)
        if not orders:
            order_text = "📦 <b>MY ORDERS HISTORY</b>\n\nYou have no past orders right now."
        else:
            order_text = "📦 <b>MY RECENT ORDERS HISTORY</b>\n\n"
            for idx, (item, price, status) in enumerate(orders, 1):
                order_text += f"{idx}. <b>{item}</b> - ₹{price} [{status}]\n"
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("« Back to Menu", callback_data="main_menu"))
        bot.send_message(call.message.chat.id, order_text, parse_mode='HTML', reply_markup=markup)
        
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

def process_free_like_uid(message):
    uid = message.text.strip()
    region = "ind"

    if not uid.isdigit():
        bot.reply_to(message, "❌ Invalid UID! Please enter numbers only.")
        return

    sent_msg = bot.reply_to(message, "⏳ <b>Processing free likes...</b>", parse_mode='HTML')
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
            reply_text = (
                "🎉 <b>LIKE SENT SUCCESSFULLY!</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"👑 <b>Player Name:</b> {name}\n"
                f"🆔 <b>UID:</b> <code>{uid}</code>\n"
                f"🌍 <b>Region:</b> {region.upper()}\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"❤ <b>Before:</b> {likes_before}\n"
                f"💙 <b>Given:</b> {likes_given}\n"
                f"💚 <b>After:</b> {likes_after}\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"⚡ <b>Remaining:</b> {remaining}"
            )
        else:
            reply_text = (
                "⚠️ <b>LIMIT REACHED / ERROR</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"👑 <b>Player Name:</b> {name}\n"
                f"🆔 <b>UID:</b> <code>{uid}</code>\n"
                f"🌍 <b>Region:</b> {region.upper()}\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"❤ <b>Before:</b> {likes_before}\n"
                f"💙 <b>Given:</b> {likes_given}\n"
                f"💚 <b>After:</b> {likes_after}\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"⚡ <b>Remaining:</b> {remaining}"
            )

        bot.edit_message_text(reply_text, chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, parse_mode='HTML')
    except Exception as e:
        bot.edit_message_text(f"❌ <b>API Error:</b> {str(e)}", chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, parse_mode='HTML')

def process_paid_like_uid(message):
    uid = message.text.strip()
    user = message.from_user

    if not uid.isdigit():
        bot.reply_to(message, "❌ Invalid UID! Please enter numbers only.")
        return

    bot.reply_to(message, f"✅ UID <code>{uid}</code> received! Admin has been notified to send your 220+ likes.", parse_mode='HTML')
    
    bot.send_message(
        ADMIN_ID,
        f"🔔 <b>PAID LIKES - UID SUBMITTED</b>\n\n👤 User Name: {user.first_name}\n🆔 Telegram ID: <code>{user.id}</code>\n🔗 Username: @{user.username if user.username else 'None'}\n🎮 Free Fire UID: <code>{uid}</code>\n📦 Package: 220+ Likes (Paid via Wallet)",
        parse_mode='HTML'
    )

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

@bot.message_handler(commands=['broadcast'])
def admin_broadcast(message):
    if message.from_user is None or message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Only the owner can use this command!")
        return
        
    text_to_broadcast = message.text.replace('/broadcast', '').strip()
    if not text_to_broadcast:
        bot.reply_to(message, "❌ <b>Usage:</b> <code>/broadcast [Your Message]</code>", parse_mode='HTML')
        return
        
    users = get_all_users()
    sent_count = 0
    for uid in users:
        try:
            bot.send_message(uid, f"📢 <b>ANNOUNCEMENT:</b>\n\n{text_to_broadcast}", parse_mode='HTML')
            sent_count += 1
        except Exception:
            pass
            
    bot.reply_to(message, f"✅ Broadcast sent successfully to {sent_count} users!")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = f"""📖 <b>HELP & COMMANDS</b>

🔹 <code>/like [region] [uid]</code> - Free Likes
🔹 <code>/utr [utr] [uid] [region]</code> - Submit UTR
🔹 <code>/menu</code> - Open Dashboard

<b>[Admin Commands]</b>
🔸 <code>/addbalance [user_id] [amount]</code> - Add Balance
🔸 <code>/broadcast [message]</code> - Send Broadcast
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

    admin_msg = (
        "🔔 <b>NEW PAYMENT UTR SUBMITTED</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Name:</b> {user.first_name}\n"
        f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
        f"🔗 <b>Username:</b> @{user.username if user.username else 'None'}\n"
        f"💳 <b>UTR Number:</b> <code>{utr_number}</code>\n"
        f"🎮 <b>UID:</b> <code>{uid}</code>\n"
        f"🌍 <b>Region:</b> {region.upper()}"
    )

    bot.send_message(ADMIN_ID, admin_msg, parse_mode='HTML')
    bot.reply_to(message, "✅ <b>UTR Submitted Successfully!</b>\nYour payment is under verification by the admin.", parse_mode='HTML')

@bot.message_handler(commands=['like'])
def handle_like(message):
    if not bot_active:
        bot.reply_to(message, "⚠️ <b>Bot is currently inactive.</b>", parse_mode='HTML')
        return

        args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "⚠️ <b>Invalid Format!</b>\nUse this format:\n<code>/like ind 1772894853</code>", parse_mode='HTML')
        return

    region = args[1].lower()
    uid = args[2]
    user = message.from_user

    sent_msg = bot.reply_to(message, "⏳ <b>Processing your request...</b>", parse_mode='HTML')
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
            reply_text = (
                "🎉 <b>LIKE SENT SUCCESSFULLY!</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"👑 <b>Player Name:</b> {name}\n"
                f"🆔 <b>UID:</b> <code>{uid}</code>\n"
                f"🌍 <b>Region:</b> {region.upper()}\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"❤ <b>Before:</b> {likes_before}\n"
                f"💙 <b>Given:</b> {likes_given}\n"
                f"💚 <b>After:</b> {likes_after}\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"⚡ <b>Remaining:</b> {remaining}"
            )
        else:
            reply_text = (
                "⚠️ <b>LIMIT REACHED / ERROR</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"👑 <b>Player Name:</b> {name}\n"
                f"🆔 <b>UID:</b> <code>{uid}</code>\n"
                f"🌍 <b>Region:</b> {region.upper()}\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"❤ <b>Before:</b> {likes_before}\n"
                f"💙 <b>Given:</b> {likes_given}\n"
                f"💚 <b>After:</b> {likes_after}\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"⚡ <b>Remaining:</b> {remaining}"
            )

        bot.edit_message_text(reply_text, chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, parse_mode='HTML')

    except Exception as e:
        bot.edit_message_text(f"❌ <b>API Error:</b> {str(e)}", chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, parse_mode='HTML')

if __name__ == '__main__':
    bot.infinity_polling(skip_pending=True)
    
        

