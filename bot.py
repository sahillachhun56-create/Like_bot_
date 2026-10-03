import os
import requests
import telebot
import sqlite3
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

app = Flask('')

@app.route('/')
def home():
    return "OK"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def run():
    t = Thread(target=run_flask)
    t.start()

API_TOKEN = "8591551561:AAEuvS55iN3ESHOoPm2X_pCXfSmqiEIlzWo"  # Your Bot Token
bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 8380823727
YOUR_UPI_ID = "orthodontist@airtel"
YOUR_NAME = "Ariful Islam Khan"
QR_CODE_URL = "https://i.postimg.cc/fL70RzQD/IMG-20261003-114641-767.jpg"

bot_active = True

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

def get_user_balance(user_id, name=None, username=None):
    conn = sqlite3.connect('bot_wallet.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    
    if row is None:
        cursor.execute("INSERT INTO users (user_id, name, username, balance) VALUES (?, ?, ?, 0.0)", (user_id, name, username))
        conn.commit()
        balance = 0.0
    else:
        balance = row[0]
        
    conn.close()
    return balance

def update_user_balance(user_id, amount):
    conn = sqlite3.connect('bot_wallet.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if row is None:
        cursor.execute("INSERT INTO users (user_id, name, username, balance) VALUES (?, ?, ?, ?)", (user_id, "User", "NoUsername", amount))
    else:
        new_balance = row[0] + amount
        cursor.execute("UPDATE users SET balance=? WHERE user_id=?", (new_balance, user_id))
    conn.commit()
    conn.close()

def add_order_to_db(user_id, item_name, price, status="Pending"):
    conn = sqlite3.connect('bot_wallet.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (user_id, item_name, price, status) VALUES (?, ?, ?, ?)", (user_id, item_name, price, status))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('bot_wallet.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_user_orders(user_id):
    conn = sqlite3.connect('bot_wallet.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT item_name, price, status FROM orders WHERE user_id=?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def reply_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("📁 Menu / Dashboard"))
    return markup

@bot.message_handler(commands=['off'])
def off_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    global bot_active
    bot_active = False
    bot.reply_to(message, "🔴 Bot service has been stopped by admin.")

@bot.message_handler(commands=['on'])
def on_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    global bot_active
    bot_active = True
    bot.reply_to(message, "🟢 Bot service has been resumed by admin.")

@bot.message_handler(func=lambda message: message.text in ["📁 Menu / Dashboard", "/menu", "/start"])
def menu_command(message):
    if not bot_active and message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⚠️ Bot is currently under maintenance. Please try again later.")
        return

    user = message.from_user
    balance = get_user_balance(user.id, user.first_name, user.username)

    markup = InlineKeyboardMarkup(row_width=2)
    btn_shop = InlineKeyboardButton("🛍️ Buy Likes", callback_data="shop_menu")
    btn_balance = InlineKeyboardButton("💰 Add Balance", callback_data="add_balance")
    btn_orders = InlineKeyboardButton("📦 My Orders", callback_data="my_orders")
    btn_profile = InlineKeyboardButton("👤 Profile", callback_data="my_profile")
    btn_support = InlineKeyboardButton("💬 Support", callback_data="support_menu")

    markup.add(btn_shop, btn_balance)
    markup.add(btn_orders, btn_profile)
    markup.add(btn_support)

    menu_text = (
        "⚡ <b>OFFICIAL GAMING ID STORE</b> ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👋 Hello, <b>{user.first_name}</b>!\n\n"
        "💎 Premium digital keys, instant delivery & secure store.\n\n"
        "✨ <b>Wide product catalog</b>\n"
        "⚡ <b>Instant key delivery</b>\n"
        "💳 <b>Multiple payment gateways</b>\n"
        f"💵 <b>Wallet Balance: ₹{balance}</b>\n\n"
        "👇 <i>Tap any button below to begin:</i>"
    )
    bot.send_message(message.chat.id, menu_text, parse_mode='HTML', reply_markup=reply_keyboard())
    bot.send_message(message.chat.id, "👇 <b>Main Dashboard Menu:</b>", parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user = call.from_user
    balance = get_user_balance(user.id, user.first_name, user.username)

    if call.data == "shop_menu":
        markup = InlineKeyboardMarkup(row_width=1)
        btn_free = InlineKeyboardButton("🎁 Free Likes", callback_data="free_likes")
        btn_paid = InlineKeyboardButton("🔥 Paid Likes", callback_data="paid_likes")
        btn_back = InlineKeyboardButton("« Main Menu", callback_data="main_menu")
        markup.add(btn_free, btn_paid, btn_back)
        
        try:
            bot.edit_message_text(
                "🛍️ <b>STORE & PRICING</b>\n\nChoose a category below:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='HTML',
                reply_markup=markup
            )
        except Exception:
            pass

    elif call.data == "free_likes":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "🎁 <b>FREE LIKES GENERATOR</b>\n\n"
            "To send free likes, use the command format below:\n"
            "<code>/like [Region] [UID]</code>\n\n"
            "<i>Example:</i> <code>/like ind 1772894853</code>",
            parse_mode='HTML'
        )

    elif call.data == "paid_likes":
        markup = InlineKeyboardMarkup(row_width=1)
        btn_sample = InlineKeyboardButton("📦 220 Likes - ₹10", callback_data="buy_package_10")
        btn_back = InlineKeyboardButton("« Back", callback_data="shop_menu")
        markup.add(btn_sample, btn_back)

        try:
            bot.edit_message_text(
                "🔥 <b>PAID LIKES PACKAGES</b>\n\nSelect a package:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='HTML',
                reply_markup=markup
            )
        except Exception:
            pass

    elif call.data == "buy_package_10":
        package_price = 10.0
        item_name = "220 Likes Package"
        if balance >= package_price:
            update_user_balance(user.id, -package_price)
            add_order_to_db(user.id, item_name, package_price, "Paid")
            new_bal = get_user_balance(user.id)
            
            admin_notification = (
                "🔔 <b>NEW LIKES PACKAGE PURCHASED!</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 <b>User Name:</b> {user.first_name}\n"
                f"🔗 <b>Username:</b> @{user.username if user.username else 'None'}\n"
                f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
                f"📦 <b>Package:</b> {item_name}\n"
                f"💵 <b>Price Paid:</b> ₹{package_price}\n"
                f"💰 <b>User's Remaining Balance:</b> ₹{new_bal}\n\n"
                f"👉 <b>To deliver likes, use command:</b>\n"
                f"<code>/like [Region] [UID]</code>"
            )
            try:
                bot.send_message(ADMIN_ID, admin_notification, parse_mode='HTML')
            except Exception:
                pass
            
            bot.answer_callback_query(call.id, "✅ Purchase Successful!")
            bot.send_message(
                call.message.chat.id,
                f"💳 <b>PAYMENT SUCCESSFUL!</b>\n\n"
                f"📦 Package: <b>220 Likes</b>\n"
                f"💵 Price: <b>₹10</b>\n"
                f"💰 Your Wallet Balance: <b>₹{new_bal}</b>\n\n"
                f"👉 <b>To deliver likes, please provide your UID using:</b>\n"
                f"<code>/order [Region] [UID]</code>",
                parse_mode='HTML'
            )
        else:
            bot.answer_callback_query(call.id)
            pay_text = (
                "❌ <b>Insufficient Balance in Wallet!</b>\n\n"
                f"Please pay ₹{package_price} via QR Code or direct UPI ID below, then submit your UTR and UID details.\n\n"
                f"🌐 <b>Scan QR Code or Pay to UPI ID:</b>\n"
                f"🆔 <b>UPI ID:</b> <code>{YOUR_UPI_ID}</code>\n"
                f"👤 <b>Name:</b> {YOUR_NAME}\n\n"
                f"2️⃣ <b>Submit Details Format:</b>\n"
                f"<code>utr [UTR Number] [Region] [UID]</code>\n"
                f"<i>Example:</i> <code>/utr 123456789 ind 1772894853</code>"
            )
            try:
                bot.send_photo(call.message.chat.id, QR_CODE_URL, caption=pay_text, parse_mode='HTML')
            except Exception:
                bot.send_message(call.message.chat.id, pay_text, parse_mode='HTML')

    elif call.data == "add_balance":
        markup = InlineKeyboardMarkup(row_width=3)
        btn_50 = InlineKeyboardButton("₹50", callback_data="add_50")
        btn_100 = InlineKeyboardButton("₹100", callback_data="add_100")
        btn_200 = InlineKeyboardButton("₹200", callback_data="add_200")
        btn_back = InlineKeyboardButton("« Main Menu", callback_data="main_menu")
        markup.add(btn_50, btn_100, btn_200)
        markup.add(btn_back)

        try:
            bot.edit_message_text(
                "💰 <b>ADD WALLET BALANCE</b>\n\nSelect amount to top-up:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='HTML',
                reply_markup=markup
            )
        except Exception:
            pass

    elif call.data.startswith("add_"):
        amounts = {"add_50": 50, "add_100": 100, "add_200": 200}
        amt = amounts.get(call.data, 50)
        
        pay_caption = (
            f"💰 <b>TOP-UP AMOUNT: ₹{amt}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💳 <b>Current Balance: ₹{balance}</b>\n\n"
            f"🌐 <b>Scan QR Code or Pay to UPI ID:</b>\n"
            f"🆔 <b>UPI ID:</b> <code>{YOUR_UPI_ID}</code>\n"
            f"👤 <b>Name:</b> {YOUR_NAME}\n\n"
            f"2️⃣ <b>Send Transaction UTR / Transfer ID:</b>\n"
            f"Type and send:\n"
            f"<code>utr [UTR Number]</code>"
        )
        try:
            bot.send_photo(call.message.chat.id, QR_CODE_URL, caption=pay_caption, parse_mode='HTML')
        except Exception:
            bot.send_message(call.message.chat.id, pay_caption, parse_mode='HTML')

    elif call.data == "my_orders":
        bot.answer_callback_query(call.id)
        orders = get_user_orders(user.id)
        if not orders:
            order_text = "📦 <b>MY ORDERS</b>\n\nYou have no past orders."
        else:
            order_text = "📦 <b>MY RECENT ORDERS:</b>\n\n"
            for idx, (item, price, status) in enumerate(orders, 1):
                order_text += f"{idx}. <b>{item}</b> - ₹{price} [{status}]\n"
        bot.send_message(call.message.chat.id, order_text, parse_mode='HTML')

    elif call.data == "my_profile":
        bot.answer_callback_query(call.id)
        profile_text = (
            f"👤 <b>MY PROFILE</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 <b>Telegram ID:</b> <code>{user.id}</code>\n"
            f"👤 <b>Name:</b> {user.first_name}\n"
            f"🔗 <b>Username:</b> @{user.username if user.username else 'None'}\n"
            f"💳 <b>Wallet Balance: ₹{balance}</b>"
        )
        bot.send_message(call.message.chat.id, profile_text, parse_mode='HTML')

    elif call.data == "support_menu":
        bot.answer_callback_query(call.id)
        support_text = (
            "💬 <b>CUSTOMER SUPPORT</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Need assistance with orders or payments?\n"
            "Reach out to the admin directly:\n\n"
            "💬 <b>Support Desk:</b> @Momshad_00"
        )
        bot.send_message(call.message.chat.id, support_text, parse_mode='HTML')

    elif call.data == "main_menu":
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        menu_command(call.message)

@bot.message_handler(commands=['utr'])
def handle_utr(message):
    if not bot_active and message.from_user.id != ADMIN_ID:
        return
    args = message.text.split(maxsplit=3)
    if len(args) < 2:
        bot.reply_to(message, "❌ Correct format: <code>utr [UTR Number] [Region] [UID]</code>", parse_mode='HTML')
        return
    
    user = message.from_user
    utr_number = args[1]
    region = args[2] if len(args) > 2 else "Not Provided"
    uid = args[3] if len(args) > 3 else "Not Provided"
    
    admin_msg = (
        f"🔔 <b>NEW PAYMENT & UID SUBMITTED!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>User Name:</b> {user.first_name}\n"
        f"🆔 <b>User Telegram ID:</b> <code>{user.id}</code>\n"
        f"🔗 <b>Username:</b> @{user.username if user.username else 'None'}\n"
        f"🎟 <b>UTR / Transfer ID:</b> <code>{utr_number}</code>\n"
        f"🌍 <b>Game Region:</b> {region.upper()}\n"
        f"🎮 <b>Game UID:</b> <code>{uid}</code>\n\n"
        f"👉 <b>To add balance, send command:</b>\n"
        f"<code>/addbalance {user.id} [Amount]</code>\n"
        f"👉 <b>To send likes, use command:</b>\n"
        f"<code>/like {region} {uid}</code>"
    )
    bot.send_message(ADMIN_ID, admin_msg, parse_mode='HTML')
    bot.reply_to(message, "✅ Your UTR and UID have been successfully submitted to the admin!")

@bot.message_handler(commands=['order'])
def handle_order_uid(message):
    if not bot_active and message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "❌ Correct format: <code>/order [Region] [UID]</code>", parse_mode='HTML')
        return
    
    user = message.from_user
    region = args[1]
    uid = args[2]
    
    admin_msg = (
        f"🔔 <b>NEW LIKES ORDER SUBMITTED!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>User Name:</b> {user.first_name}\n"
        f"🆔 <b>User Telegram ID:</b> <code>{user.id}</code>\n"
        f"🔗 <b>Username:</b> @{user.username if user.username else 'None'}\n"
        f"🌍 <b>Game Region:</b> {region.upper()}\n"
        f"🎮 <b>Game UID:</b> <code>{uid}</code>\n\n"
        f"👉 <b>To send likes, use command:</b>\n"
        f"<code>/like {region} {uid}</code>"
    )
    bot.send_message(ADMIN_ID, admin_msg, parse_mode='HTML')
    bot.reply_to(message, "✅ Your UID has been received! Admin will process your likes shortly.")

@bot.message_handler(commands=['addbalance'])
def add_balance_admin(message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "❌ Correct format: <code>/addbalance [User_ID] [Amount]</code>", parse_mode='HTML')
        return
    try:
        target_user_id = int(args[1])
        amount = float(args[2])
        update_user_balance(target_user_id, amount)
        bot.send_message(target_user_id, f"🎉 <b>Success!</b> Admin added <b>₹{amount}</b> to your wallet.", parse_mode='HTML')
        bot.reply_to(message, "✅ Balance successfully added to user wallet!")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(commands=['broadcast'])
def admin_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return
    text_to_broadcast = message.text.replace('/broadcast', '').strip()
    if not text_to_broadcast:
        bot.reply_to(message, "❌ Please provide text to broadcast.")
        return
    users = get_all_users()
    sent_count = 0
    for uid in users:
        try:
            bot.send_message(uid, text_to_broadcast, parse_mode='HTML')
            sent_count += 1
        except Exception:
            pass
    bot.reply_to(message, f"✅ Broadcast sent to {sent_count} users successfully!")

@bot.message_handler(commands=['help'])
def help_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    help_text = (
        "🛠️ <b>HELP & COMMANDS</b>\n\n"
        "<code>/like [region] [uid]</code> - Free Fire Like Bot\n"
        "<code>/addbalance [user_id] [amount]</code> - Add balance\n"
        "<code>/broadcast [text]</code> - Send message to all users\n"
        "<code>/on</code> / <code>/off</code> - Toggle bot service"
    )
    bot.reply_to(message, help_text, parse_mode='HTML')

@bot.message_handler(commands=['like'])
def handle_like(message):
    if not bot_active and message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⚠️ Bot service is currently disabled.")
        return
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(
            message,
            "❌ <b>Incorrect Command Structure!</b>\n"
            "📌 <b>Correct Format :</b> <code>/like {region} {uid}</code>\n"
            "💡 <b>Example :</b> <code>/like ind 1772894853</code>\n\n"
            f"👑 <b>ADMIN ID :</b> <code>{ADMIN_ID}</code>\n"
            f"🚀 <b>OWNER :</b> @Momshad_00",
            parse_mode='HTML'
        )
        return

    region = args[1].lower()
    uid = args[2]

    if not uid.isdigit():
        bot.reply_to(message, "❌ Invalid UID! Only numbers allowed.")
        return

    sent_msg = bot.reply_to(message, "⏳ Processing your request...", parse_mode='HTML')
    
    api_url = f"https://like-apii-one.vercel.app/like?uid={uid}&server_name={region}"
    try:
        response = requests.get(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        data = response.json()
        
        name = str(data.get('PlayerNickname', 'Unknown'))
        likes_before = str(data.get('LikesbeforeCommand', '0'))
        likes_given = str(data.get('LikesGivenByAPI', '0'))
        likes_after = str(data.get('LikesafterCommand', '0'))
        remaining = str(data.get('Remaining_requests', '0'))
  
if int(likes_after) > int(likes_before):
        reply_text = (
            "🎉 <b>LIKE SUCCESSFUL!</b> 👈\n"
            "_________________________\n"
            f"👑 <b>Name :</b> {name}\n"
            f"🎮 <b>UID :</b> {uid}\n"
            f"🌍 <b>Region :</b> {region.upper()}\n"
            "_________________________\n"
            f"❤️ <b>Likes Before :</b> {likes_before}\n"
            f"💙 <b>Likes Given :</b> {likes_given}\n"
            f"💚 <b>Likes After :</b> {likes_after}\n"
            f"⚡ <b>Remaining :</b> {remaining}\n"
        )
    else:
        reply_text = (
            "⚠️ <b>LIMIT REACHED!</b>\n"
            "_________________________\n"
            f"👑 <b>Name :</b> {name}\n"
            f"🎮 <b>UID :</b> {uid}\n"
            f"🌍 <b>Region :</b> {region.upper()}\n"
            "_________________________\n"
            f"❤️ <b>Likes Before :</b> {likes_before}\n"
            f"💙 <b>Likes Given :</b> {likes_given}\n"
            f"💚 <b>Likes After :</b> {likes_after}\n"
            f"⚡ <b>Remaining :</b> {remaining}\n"
        )
    except Exception as e:
        reply_text = f"❌ <b>API Error:</b> Could not process request. ({e})"

    bot.edit_message_text(
        reply_text,
        chat_id=sent_msg.chat.id,
        message_id=sent_msg.message_id,
        parse_mode='HTML'
    )

if __name__ == '__main__':
    run()
    bot.infinity_polling(skip_pending=True)
    
