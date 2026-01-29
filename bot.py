import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask, request

# Конфигурация
TOKEN = os.getenv('TELEGRAM_TOKEN', '8547051827:AAEgIj1624F5Vrpx4oXwa-qj4Hie1SwOY3g')
ADMIN_ID = 5350202227
ADMINS = [5350202227]

# Flask
app = Flask(__name__)

# Бот
application = Application.builder().token(TOKEN).build()

# ========== ФУНКЦИИ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Вайтлист", callback_data='whitelist')],
        [InlineKeyboardButton("💬 Поддержка", callback_data='support')],
        [InlineKeyboardButton("💎 Донат", callback_data='donate')],
        [InlineKeyboardButton("📜 Правила", callback_data='rules')]
    ]
    await update.message.reply_text(
        f"👋 Привет, {update.effective_user.first_name}!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'support':
        user = query.from_user
        # Отправляем админам
        for admin_id in ADMINS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"🆘 Новое обращение от @{user.username or user.first_name} (ID: {user.id})"
                )
            except:
                pass
        await query.message.edit_text("✅ Ваше обращение отправлено админам!")

# Регистрация обработчиков
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))

# ========== WEBHOOK ==========
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return 'ok'

@app.route('/')
def home():
    return "Бот работает! 🚀"

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    # Для Render - используем вебхуки
    if os.getenv('RENDER'):
        print("🤖 Запуск на Render с вебхуками...")
        # Бот запустится автоматически через Flask
        port = int(os.getenv('PORT', 10000))
        app.run(host='0.0.0.0', port=port)
    else:
        # Локально
        print("🤖 Локальный запуск (polling)...")
        application.run_polling()