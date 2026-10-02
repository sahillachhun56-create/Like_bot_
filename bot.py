import os
import telebot
import requests
from flask import Flask
import threading
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

app = Flask('')

@app.route('/')
def home():
    return "OK"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_flask).start()

API_TOKEN = "8591551561:AAHdwcPBTf-j8K5quVjKcZXrvG1YJYAX-8s"
bot = telebot.TeleBot(API_TOKEN)

# Your Admin Telegram ID
ADMIN_ID = 8380823727
YOUR_UPI_ID = "orthodontist@airtel"

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
    
    # Popup with Menu option via Inline Markup inside alert/callback simulation or standard greeting with Menu Button
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    
    btn_open_menu = InlineKeyboardButton("⚡ Click Here To Open Menu ⚡", callback_data="main_menu")
    btn_shop = InlineKeyboardButton("🛍️ Shop / Plans", callback_data="shop_menu")
    btn_balance = InlineKeyboardButton("💰 Add Balance", callback_data="add_balance")
    btn_profile = InlineKeyboardButton("👤 My Profile", callback_data="my_profile")
    btn_support = InlineKeyboardButton("📞 Support", callback_data="support_menu")
    btn_help = InlineKeyboardButton("🤖 Help Menu", callback_data="help_menu")
    
    markup.add(btn_open_menu, btn_shop, btn_balance, btn_profile, btn_support, btn_help)
    
    menu_text = f"""🔥 ━━━━━━━━━━━━━━━━━━━━ 🔥
      <b>⚡ WELCOME TO MOMSHAD LIKE BOT ⚡</b>
🔥 ━━━━━━━━━━━━━━━━━━━━ 🔥

👋 Hello <b>{user_name}</b>! 
Get lightning-fast Free & Paid likes for your Free Fire account instantly.

📌 <b>Choose an option below or tap the Menu button:</b>
• Browse Free & Paid Like Plans.
• Manage your wallet balance & profile.

🔥 ━━━━━━━━━━━━━━━━━━━━ 🔥
👑 <b>OWNER :</b> @Momshad_00"""
    
    # Triggering a welcoming popup alert when /start is used
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
        btn_paid = InlineKeyboardButton("💎 220+ Likes - Rs.10", callback_data="paid_likes")
        btn_back = InlineKeyboardButton("⬅ Back to Menu", callback_data="main_menu")
        
        markup.add(btn_free, btn_paid, btn_back)
        
        try:
            bot.edit_message_text(
                "🛍️ <b>SELECT LIKE PLAN</b>\n──────────────────\nChoose your desired pack below:",
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
        paid_text = f"""💎 <b>220+ Likes - Rs. 10</b>
──────────────────
1️⃣ Pay ₹10 to the UPI ID below:
📌 UPI ID: <code>{YOUR_UPI_ID}</code>
👤 Name: <b>Ariful Islam Khan</b>

2️⃣ After payment, send the 12-digit **UTR / Transaction ID** using this format:
👉 <code>/utr [12-digit UTR] [Your UID] [Region]</code>
💡 Example: <code>/utr 412345678912 1772894853 ind</code>

3️⃣ Likes will be added to your account after verification!"""
        bot.send_message(call.message.chat.id, paid_text, parse_mode='HTML')
        
    elif call.data == "main_menu":
        user_name = call.from_user.first_name if call.from_user else "User"
        bot.answer_callback_query(call.id, "⚡ Menu opened successfully!")
        
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        
        btn_open_menu = InlineKeyboardButton("⚡ Main Menu Panel ⚡", callback_data="main_menu")
        btn_shop = InlineKeyboardButton("🛍️ Shop / Plans", callback_data="shop_menu")
        btn_balance = InlineKeyboardButton("💰 Add Balance", callback_data="add_balance")
        btn_profile = InlineKeyboardButton("👤 My Profile", callback_data="my_profile")
        btn_support = InlineKeyboardButton("📞 Support", callback_data="support_menu")
        btn_help = InlineKeyboardButton("🤖 Help Menu", callback_data="help_menu")
        
        markup.add(btn_open_menu, btn_shop, btn_balance, btn_profile, btn_support, btn_help)
        
        menu_text = f"""🔥 ━━━━━━━━━━━━━━━━━━━━ 🔥
      <b>⚡ WELCOME TO MOMSHAD LIKE BOT ⚡</b>
🔥 ━━━━━━━━━━━━━━━━━━━━ 🔥

👋 Hello <b>{user_name}</b>! 
Get lightning-fast Free & Paid likes for your Free Fire account instantly.

📌 <b>Choose an option below:</b>
• Browse Free & Paid Like Plans.
• Manage your wallet balance & profile.

🔥 ━━━━━━━━━━━━━━━━━━━━ 🔥
👑 <b>OWNER :</b> @Momshad_00"""
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
        btn_back = InlineKeyboardButton("⬅ Back to Menu", callback_data="main_menu")
        
        markup.add(btn_50, btn_100, btn_200, btn_back)
        
        try:
            bot.edit_message_text(
                "💰 <b>ADD BALANCE MENU</b>\n──────────────────\nSelect the amount you want to add to your wallet:",
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
        
        pay_text = f"""💰 <b>ADD ₹{amt} TO BALANCE</b>
──────────────────
1️⃣ Pay **₹{amt}** to the UPI ID below:
📌 UPI ID: <code>{YOUR_UPI_ID}</code>
👤 Name: <b>Ariful Islam Khan</b>

2️⃣ Send the 12-digit **UTR / Transaction ID** using this format:
👉 <code>/utr [UTR Number] [Your UID] [Region]</code>

3️⃣ Your balance will be updated after verification!"""
        bot.send_message(call.message.chat.id, pay_text, parse_mode='HTML')
        
    elif call.data == "my_profile":
        bot.answer_callback_query(call.id, "Loading profile...")
        user = call.from_user
        profile_text = f"""👤 <b>YOUR PROFILE</b>
──────────────────
🆔 <b>User ID :</b> <code>{user.id}</code>
📛 <b>Name :</b> {user.first_name}
🔗 <b>Username :</b> @{user.username if user.username else 'None'}
──────────────────"""
        bot.send_message(call.message.chat.id, profile_text, parse_mode='HTML')

    elif call.data == "support_menu":
        bot.answer_callback_query(call.id, "Opening support...")
        support_text = f"""📞 <b>CUSTOMER SUPPORT</b>
──────────────────
Need help with payment or likes? Contact the owner directly:
👑 <b>Owner:</b> @Momshad_00
──────────────────"""
        bot.send_message(call.message.chat.id, support_text, parse_mode='HTML')
        
    elif call.data == "help_menu":
        bot.answer_callback_query(call.id, "Opening help...")
        help_text = f"""🤖 <b>HELP MENU</b> 🤖
──────────────────
🔹 <code>/like {{region}} {{uid}}</code> - Send free likes
🔹 <code>/utr {{utr}} {{uid}} {{region}}</code> - Submit payment UTR
🔹 <code>/menu</code> - Open main panel buttons
──────────────────"""
        bot.send_message(call.message.chat.id, help_text, parse_mode='HTML')

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = f"""🤖 <b>MOMSHAD LIKE BOT HELP</b> 🤖
──────────────────
📌 <b>Commands :</b>
🔹 <code>/like {{region}} {{uid}}</code> - Send free likes
🔹 <code>/utr {{utr}} {{uid}} {{region}}</code> - Submit payment UTR
🔹 <code>/menu</code> - Open interactive button panel

👑 <b>Admin Commands (Owner Only) :</b>
🔸 <code>/on</code> - Turn bot services ON
🔸 <code>/off</code> - Turn bot services OFF
──────────────────"""
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

    admin_msg = f"""💰 <b>NEW PAYMENT UTR RECEIVED!</b>
──────────────────
👤 <b>User Name :</b> {user.first_name}
🆔 <b>Telegram ID :</b> <code>{user.id}</code>
🔗 <b>Username :</b> @{user.username if user.username else 'None'}
──────────────────
💳 <b>UTR Number :</b> <code>{utr_number}</code>
🎮 <b>Target UID :</b> <code>{uid}</code>
🌍 <b>Region :</b> {region.upper()}
──────────────────"""

    bot.send_message(ADMIN_ID, admin_msg, parse_mode='HTML')
    bot.reply_to(message, "✅ <b>Your UTR has been submitted successfully!</b>\nYour account/balance will be updated after verification by the owner.", parse_mode='HTML')

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
            reply_text = f"""🎉 <b>LIKE SUCCESSFUL</b> 👍
──────────────────
👑 <b>Name :</b> {name}
🎮 <b>UID :</b> {uid}
🌍 <b>Region :</b> {region.upper()}
──────────────────
❤️ <b>Likes Before :</b> {likes_before}
💙 <b>Likes Given :</b> {likes_given}
💚 <b>Likes After :</b> {likes_after}
⚡ <b>Remaining Requests :</b> {remaining}"""
        else:
            reply_text = f"""⚠️ <b>DAILY LIMIT REACHED</b>
──────────────────
👤 <b>NAME :</b> {name}
🆔 <b>UID :</b> {uid}
🌍 <b>SERVER :</b> {region.upper()}
──────────────────
📊 <b>STATUS :</b> 0 Likes Added"""

        bot.edit_message_text(reply_text, chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, parse_mode='HTML')

    except Exception as e:
        bot.edit_message_text(f"❌ <b>API Error:</b> {str(e)}", chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, parse_mode='HTML')

if __name__ == '__main__':
    bot.infinity_polling(skip_pending=True)
        
