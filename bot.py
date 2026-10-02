import os
import telebot
import requests
from flask import Flask
import threading
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

app = Flask('')

@app.route('/')
def home():
    return "OK"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_flask).start()

API_TOKEN = "8591551561:AAEHli4517JUJOZ_aMH_Ot7wuuueDQyJLEQ"
bot = telebot.TeleBot(API_TOKEN)

# Your Admin Telegram ID
ADMIN_ID = 8380823727
YOUR_UPI_ID = "orthodontist@airtel"

# 📌 अपने QR Code की Image का Direct Link यहाँ डालें
QR_CODE_URL = "YOUR_QR_IMAGE_DIRECT_URL_HERE" 

# Global variable to control bot status
bot_active = True

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

@bot.message_handler(commands=['start', 'menu'])
def menu_command(message):
    user_name = message.from_user.first_name if message.from_user else "User"
    
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    
    btn_open_menu = InlineKeyboardButton("⚡ Open Main Dashboard ⚡", callback_data="main_menu")
    btn_shop = InlineKeyboardButton("🛍️ Shop & Like Plans", callback_data="shop_menu")
    btn_balance = InlineKeyboardButton("💳 Add Wallet Balance", callback_data="add_balance")
    btn_profile = InlineKeyboardButton("👤 User Profile", callback_data="my_profile")
    btn_support = InlineKeyboardButton("💬 Customer Support", callback_data="support_menu")
    btn_help = InlineKeyboardButton("📖 Help & Commands", callback_data="help_menu")
    
    markup.add(btn_open_menu, btn_shop, btn_balance, btn_profile, btn_support, btn_help)
    
    # 🌟 Highly Professional & Modern Welcome Card Design
    menu_text = f"""╭━━━ <b>⚡ OFFICIAL MOMSHAD BOT ⚡</b> ━━━╮
┃
┃  👋 Welcome, <b>{user_name}</b>!
┃  🚀 Instant Free & Paid Free Fire Likes.
┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯

💎 <b>Select an option from the panel below:</b>
• 🎁 <b>Free Likes:</b> Instant daily delivery.
• ⚡ <b>Paid Plans:</b> Heavy bulk likes at low cost.
• 💳 <b>Wallet:</b> Add funds securely via UPI/QR.

────────────────────────────
👑 <b>Owner & Admin :</b> @Momshad_00
⭐ <i>Status : Active & Online 24/7</i>"""
    
    try:
        bot.send_dice(message.chat.id, emoji='🎯')
    except Exception:
        pass

    bot.send_message(message.chat.id, menu_text, parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "shop_menu":
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        
        btn_free = InlineKeyboardButton("🎁 20+ Free Likes", callback_data="free_likes")
        btn_paid = InlineKeyboardButton("💎 220+ Likes - ₹10", callback_data="paid_likes")
        btn_back = InlineKeyboardButton("« Back to Main Menu", callback_data="main_menu")
        
        markup.add(btn_free, btn_paid, btn_back)
        
        try:
            bot.edit_message_text(
                "╭━━━ 🛍️ <b>STORE & PRICING</b> ━━━╮\n┃\n┃  Select your preferred package below:\n┃\n╰━━━━━━━━━━━━━━━━━━━━━━╯",
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
        paid_text = f"""╭━━━ 💎 <b>PREMIUM LIKE PACKAGE</b> ━━━╮
┃
┃  📦 <b>Package:</b> 220+ Likes
┃  💰 <b>Price:</b> ₹10 Only
┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯

1️⃣ <b>Scan QR Code or Pay to UPI ID:</b>
📌 UPI ID: <code>{YOUR_UPI_ID}</code>
👤 Name: <b>Ariful Islam Khan</b>

2️⃣ <b>Submit UTR after payment:</b>
👉 <code>/utr [12-digit UTR] [Your UID] [Region]</code>
💡 <i>Example:</i> <code>/utr 412345678912 1772894853 ind</code>

✨ <i>Likes will be credited instantly upon manual verification!</i>"""
        
        if QR_CODE_URL and QR_CODE_URL != "YOUR_QR_IMAGE_DIRECT_URL_HERE":
            bot.send_photo(call.message.chat.id, QR_CODE_URL, caption=paid_text, parse_mode='HTML')
        else:
            bot.send_message(call.message.chat.id, paid_text, parse_mode='HTML')
        
    elif call.data == "main_menu":
        user_name = call.from_user.first_name if call.from_user else "User"
        bot.answer_callback_query(call.id, "⚡ Dashboard loaded successfully!")
        
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        
        btn_open_menu = InlineKeyboardButton("⚡ Open Main Dashboard ⚡", callback_data="main_menu")
        btn_shop = InlineKeyboardButton("🛍️ Shop & Like Plans", callback_data="shop_menu")
        btn_balance = InlineKeyboardButton("💳 Add Wallet Balance", callback_data="add_balance")
        btn_profile = InlineKeyboardButton("👤 User Profile", callback_data="my_profile")
        btn_support = InlineKeyboardButton("💬 Customer Support", callback_data="support_menu")
        btn_help = InlineKeyboardButton("📖 Help & Commands", callback_data="help_menu")
        
        markup.add(btn_open_menu, btn_shop, btn_balance, btn_profile, btn_support, btn_help)
        
        menu_text = f"""╭━━━ <b>⚡ OFFICIAL MOMSHAD BOT ⚡</b> ━━━╮
┃
┃  👋 Welcome, <b>{user_name}</b>!
┃  🚀 Instant Free & Paid Free Fire Likes.
┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯

💎 <b>Select an option from the panel below:</b>
• 🎁 <b>Free Likes:</b> Instant daily delivery.
• ⚡ <b>Paid Plans:</b> Heavy bulk likes at low cost.
• 💳 <b>Wallet:</b> Add funds securely via UPI/QR.

────────────────────────────
👑 <b>Owner & Admin :</b> @Momshad_00
⭐ <i>Status : Active & Online 24/7</i>"""
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
        btn_back = InlineKeyboardButton("« Back to Main Menu", callback_data="main_menu")
        
        markup.add(btn_50, btn_100, btn_200, btn_back)
        
        try:
            bot.edit_message_text(
                "╭━━━ 💳 <b>ADD WALLET BALANCE</b> ━━━╮\n┃\n┃  Select amount to top-up your wallet:\n┃\n╰━━━━━━━━━━━━━━━━━━━━━━╯",
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
        
        pay_text = f"""╭━━━ 💳 <b>TOP-UP ₹{amt}</b> ━━━╮
┃
┃  📦 <b>Amount:</b> ₹{amt}
┃
╰━━━━━━━━━━━━━━━━━━━━╯

1️⃣ <b>Pay using the QR Code or UPI ID:</b>
📌 UPI ID: <code>{YOUR_UPI_ID}</code>
👤 Name: <b>Ariful Islam Khan</b>

2️⃣ <b>Send Transaction UTR:</b>
👉 <code>/utr [UTR Number] [Your UID] [Region]</code>

✨ <i>Balance will be updated instantly after confirmation.</i>"""
        
        if QR_CODE_URL and QR_CODE_URL != "YOUR_QR_IMAGE_DIRECT_URL_HERE":
            bot.send_photo(call.message.chat.id, QR_CODE_URL, caption=pay_text, parse_mode='HTML')
        else:
            bot.send_message(call.message.chat.id, pay_text, parse_mode='HTML')
        
    elif call.data == "my_profile":
        bot.answer_callback_query(call.id, "Loading profile...")
        user = call.from_user
        profile_text = f"""╭━━━ 👤 <b>USER PROFILE</b> ━━━╮
┃
┃  🆔 <b>Telegram ID:</b> <code>{user.id}</code>
┃  📛 <b>Name:</b> {user.first_name}
┃  🔗 <b>Username:</b> @{user.username if user.username else 'None'}
┃
╰━━━━━━━━━━━━━━━━━━━━╯"""
        bot.send_message(call.message.chat.id, profile_text, parse_mode='HTML')

    elif call.data == "support_menu":
        bot.answer_callback_query(call.id, "Opening support...")
        support_text = f"""╭━━━ 💬 <b>CUSTOMER SUPPORT</b> ━━━╮
┃
┃  Need assistance with orders or payments? 
┃  Reach out to the admin directly:
┃
┃  👑 <b>Support Desk:</b> @Momshad_00
┃
╰━━━━━━━━━━━━━━━━━━━━━━╯"""
        bot.send_message(call.message.chat.id, support_text, parse_mode='HTML')
        
    elif call.data == "help_menu":
        bot.answer_callback_query(call.id, "Opening help...")
        help_text = f"""╭━━━ 📖 <b>BOT COMMANDS GUIDE</b> ━━━╮
┃
┃  🔹 <code>/like [region] [uid]</code> - Get Free Likes
┃  🔹 <code>/utr [utr] [uid] [region]</code> - Submit Payment
┃  🔹 <code>/menu</code> - Open Interactive Panel
┃
╰━━━━━━━━━━━━━━━━━━━━━━╯"""
        bot.send_message(call.message.chat.id, help_text, parse_mode='HTML')

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = f"""╭━━━ 📖 <b>HELP & COMMANDS</b> ━━━╮
┃
┃  🔹 <code>/like [region] [uid]</code> - Free Likes
┃  🔹 <code>/utr [utr] [uid] [region]</code> - Submit UTR
┃  🔹 <code>/menu</code> - Open Dashboard
┃
┃  <b>[Admin Commands]</b>
┃  🔸 <code>/on</code> - Start Bot Services
┃  🔸 <code>/off</code> - Stop Bot Services
┃
╰━━━━━━━━━━━━━━━━━━━━━━╯"""
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

    admin_msg = f"""╭━━━ 💰 <b>NEW PAYMENT RECEIVED</b> ━━━╮
┃
┃  👤 <b>Name:</b> {user.first_name}
┃  🆔 <b>ID:</b> <code>{user.id}</code>
┃  🔗 <b>Username:</b> @{user.username if user.username else 'None'}
┃
┃  💳 <b>UTR:</b> <code>{utr_number}</code>
┃  🎮 <b>UID:</b> <code>{uid}</code>
┃  🌍 <b>Region:</b> {region.upper()}
┃
╰━━━━━━━━━━━━━━━━━━━━━━╯"""

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
            reply_text = f"""╭━━━ 🎉 <b>LIKE SUCCESSFUL</b> ━━━╮
┃
┃  👑 <b>Name:</b> {name}
┃  🎮 <b>UID:</b> {uid}
┃  🌍 <b>Region:</b> {region.upper()}
┃
┃  ❤️ <b>Before:</b> {likes_before}
┃  💙 <b>Given:</b> {likes_given}
┃  💚 <b>After:</b> {likes_after}
┃  ⚡ <b>Remaining:</b> {remaining}
┃
╰━━━━━━━━━━━━━━━━━━━━━━╯"""
        else:
            reply_text = f"""╭━━━ ⚠️ <b>LIMIT REACHED</b> ━━━╮
┃
┃  👤 <b>Name:</b> {name}
┃  🆔 <b>UID:</b> {uid}
┃  🌍 <b>Server:</b> {region.upper()}
┃
┃  📊 <b>Status:</b> 0 Likes Added
┃
╰━━━━━━━━━━━━━━━━━━━━━━╯"""

        bot.edit_message_text(reply_text, chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, parse_mode='HTML')

    except Exception as e:
        bot.edit_message_text(f"❌ <b>API Error:</b> {str(e)}", chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, parse_mode='HTML')

if __name__ == '__main__':
    bot.infinity_polling(skip_pending=True)
    
        
