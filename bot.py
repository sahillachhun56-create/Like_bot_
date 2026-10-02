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

API_TOKEN = "8591551561:AAFXq3-fzROM5BdN3xYHrrPVqgxmGbW-kXs"
bot = telebot.TeleBot(API_TOKEN)

# Your Admin Telegram ID
ADMIN_ID = 8380823727

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

@bot.message_handler(commands=['menu'])
def menu_command(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    
    btn_shop = InlineKeyboardButton("🛍️ Shop / Plans", callback_data="shop_menu")
    btn_balance = InlineKeyboardButton("💰 Add Balance", callback_data="add_balance")
    btn_profile = InlineKeyboardButton("👤 My Profile", callback_data="my_profile")
    btn_help = InlineKeyboardButton("🤖 Help Menu", callback_data="help_menu")
    
    markup.add(btn_shop, btn_balance, btn_profile, btn_help)
    
    menu_text = f"""🚀 <b>MOMSHAD STORE PANEL</b> 🚀
──────────────────
📌 <b>Choose an option below:</b>
• Browse Free & Paid Like Plans.
• Check your account details.
──────────────────
👑 <b>OWNER :</b> @Momshad_00"""
    
    bot.send_message(message.chat.id, menu_text, parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "shop_menu":
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        
        btn_free = InlineKeyboardButton("🎁 20+ Free Likes", callback_data="free_likes")
        btn_paid = InlineKeyboardButton("💎 220+ Likes - Rs.10", callback_data="paid_likes")
        btn_back = InlineKeyboardButton("⬅️ Back to Menu", callback_data="main_menu")
        
        markup.add(btn_free, btn_paid, btn_back)
        
        try:
            bot.edit_message_text(
                "🛍️ <b>SELECT LIKE PLAN</b>\n──────────────────\nचुनें आपको कौन सा पैक चाहिए:",
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
            "🎁 <b>फ्री लाइक्स लेने के लिए कमांड इस्तेमाल करें:</b>\n\n📌 फॉर्मेट: <code>/like ind [अपना UID]</code>\n💡 उदाहरण: <code>/like ind 1772894853</code>\n\n(यह बिल्कुल मुफ्त है!)", 
            parse_mode='HTML'
        )
        
    elif call.data == "paid_likes":
        bot.answer_callback_query(call.id, "Paid Plan selected")
        bot.send_message(
            call.message.chat.id, 
            "💎 <b>220+ Likes - Rs. 10</b>\n──────────────────\n1️⃣ इस UPI ID पर ₹10 पेमेंट करें: <code>your-upi@paytm</code>\n2️⃣ पेमेंट का **Screenshot** ओनर को भेजें: @Momshad_00\n3️⃣ स्क्रीनशॉट भेजते ही आपको लाइक्स मिल जाएंगे!", 
            parse_mode='HTML'
        )
        
    elif call.data == "main_menu":
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        
        btn_shop = InlineKeyboardButton("🛍️ Shop / Plans", callback_data="shop_menu")
        btn_balance = InlineKeyboardButton("💰 Add Balance", callback_data="add_balance")
        btn_profile = InlineKeyboardButton("👤 My Profile", callback_data="my_profile")
        btn_help = InlineKeyboardButton("🤖 Help Menu", callback_data="help_menu")
        
        markup.add(btn_shop, btn_balance, btn_profile, btn_help)
        
        menu_text = f"""🚀 <b>MOMSHAD STORE PANEL</b> 🚀
──────────────────
📌 <b>Choose an option below:</b>
• Browse Free & Paid Like Plans.
• Check your account details.
──────────────────
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
        bot.answer_callback_query(call.id, "Add Balance")
        bot.send_message(call.message.chat.id, "💰 To add balance or buy paid packages, message the owner: @Momshad_00")
        
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
        
    elif call.data == "help_menu":
        bot.answer_callback_query(call.id, "Opening help...")
        help_text = f"""🤖 <b>HELP MENU</b> 🤖
──────────────────
🔹 <code>/like {{region}} {{uid}}</code> - Send likes
🔹 <code>/menu</code> - Open main panel buttons
🔹 <code>/help</code> - Show text help menu
──────────────────"""
        bot.send_message(call.message.chat.id, help_text, parse_mode='HTML')

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = f"""🤖 <b>MOMSHAD BOT HELP MENU</b> 🤖
──────────────────
📌 <b>Available Commands :</b>
🔹 <code>/like {{region}} {{uid}}</code> - Send likes to a Free Fire player
🔹 <code>/menu</code> - Open interactive button panel
🔹 <code>/help</code> - Show this help menu

👑 <b>Admin Commands (Owner Only) :</b>
🔸 <code>/on</code> - Turn bot services ON
🔸 <code>/off</code> - Turn bot services OFF
──────────────────
👑 <b>ADMIN ID :</b> <code>{ADMIN_ID}</code>
🚀 <b>OWNER :</b> @Momshad_00"""
    bot.reply_to(message, help_text, parse_mode='HTML')

@bot.message_handler(commands=['like'])
def handle_like(message):
    if not bot_active:
        bot.reply_to(message, "⚠️ Bot is currently offline. Send /on to start it.")
        return

    args = message.text.split()
    if len(args) < 3:
        error_text = f"""⚠️ <b>WRONG FORMAT USAGE</b> ⚠️
──────────────────
❌ <b>Incorrect Command Structure</b>
📌 <b>Correct Format :</b> <code>/like {{region}} {{uid}}</code>
💡 <b>Example :</b> <code>/like ind 1772894853</code>
──────────────────
👑 <b>ADMIN ID :</b> <code>{ADMIN_ID}</code>
🚀 <b>OWNER :</b> @Momshad_00"""
        bot.reply_to(message, error_text, parse_mode='HTML')
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
⚡ <b>Remaining Requests :</b> {remaining}
──────────────────
👑 <b>ADMIN ID :</b> <code>{ADMIN_ID}</code>
🚀 <b>OWNER :</b> @Momshad_00"""
        else:
            reply_text = f"""⚠️ <b>DAILY LIMIT REACHED</b>
──────────────────
👤 <b>NAME :</b> {name}
🆔 <b>UID :</b> {uid}
🌍 <b>SERVER :</b> {region.upper()}
──────────────────
📊 <b>STATUS :</b> 0 Likes Added
✏️ <b>REASON :</b> Daily Max Limit Reached
──────────────────
👑 <b>ADMIN ID :</b> <code>{ADMIN_ID}</code>
🚀 <b>OWNER :</b> @Momshad_00"""

        bot.edit_message_text(reply_text, chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, parse_mode='HTML')

    except Exception as e:
        bot.edit_message_text(f"❌ <b>API Error:</b> {str(e)}", chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, parse_mode='HTML')

if __name__ == '__main__':
    bot.infinity_polling(skip_pending=True)

    
    
