import os
import telebot
import requests
from flask import Flask
import threading

app = Flask('')
@app.route('/')
def home():
    return "OK"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_flask).start()

API_TOKEN = '8905641525:AAFq_XGo2hRRZN_tHWqsdR-e9Uvxo7xuUhI'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['like'])
def handle_like(message):
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "❌ **Usage:** `/like {region} {uid}`\nExample: `/like ind 1772894853`", parse_mode='Markdown')
        return

    region = args[1].lower()
    uid = args[2]

    sent_msg = bot.reply_to(message, "⏳ <b>Processing your request...</b>", parse_mode="HTML")
    api_url = f"https://like-apii-one.vercel.app/like?uid={uid}&server_name={region}"

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(api_url, headers=headers)
        data = response.json()

        name = str(data.get('PlayerNickname', 'N/A')).strip()
        likes_before = str(data.get('LikesbeforeCommand', '0'))
        likes_given = str(data.get('LikesGivenByAPI', '0'))
        likes_after = str(data.get('LikesafterCommand', '0'))
        remaining = str(data.get('Remaining_requests', 'N/A'))

        if likes_given == "0":
            reply_text = f"""⚠️ <b>DAILY LIMIT REACHED</b> ⚠️
━━━━━━━━━━━━━━━━━━━━
👤 <b>NAME :</b> {name}
🆔 <b>UID :</b> {uid}
🌍 <b>SERVER :</b> {region.upper()}

📊 <b>STATUS :</b> 0 Likes Added
📝 <b>REASON :</b> Daily Max Limit Reached

💡 <b>Note:</b> Iss UID par aaj ke likes pehle hi poore ho chuke hain!

🚀 <b>OWNER :</b> @Momshad_00
━━━━━━━━━━━━━━━━━━━━"""
        else:
            reply_text = f"""🎉 <b>LIKE SUCCESSFUL</b> 👍
━━━━━━━━━━━━━━━━━━━━
👑 <b>Name :</b> {name}
🕹️ <b>UID :</b> {uid}
🌐 <b>Region :</b> {region.upper()}
━━━━━━━━━━━━━━━━━━━━
❤️ <b>Likes Before :</b> {likes_before}
🩵 <b>Likes Given :</b> {likes_given}
💚 <b>Likes After :</b> {likes_after}
⚡ <b>Remaining Requests :</b> {remaining}

🚀 <b>OWNER :</b> @Momshad_00
━━━━━━━━━━━━━━━━━━━━"""

        bot.edit_message_text(reply_text, chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, parse_mode="HTML")

    except Exception as e:
        bot.edit_message_text(f"❌ <b>API Error:</b>\n<code>{str(e)}</code>", chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, parse_mode="HTML")
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "🤖 Momshad Like Bot Help\n\n"
        "Aap is bot se Free Fire likes bhej sakte hain!\n\n"
        "📌 Command Format:\n"
        "/like {region} {uid}\n\n"
        "💡 Example:\n"
        "/like ind 1772894853\n\n"
        "🚀 Owner: @Momshad_00"
    )
    bot.reply_to(message, help_text)
    

    
if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True)
    
    
