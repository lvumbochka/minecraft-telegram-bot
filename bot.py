import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask, request

# Конфигурация
TOKEN = os.getenv('TELEGRAM_TOKEN', '8297599326:AAFIts64NWbahE2acjBVOWEoq84hvbHv8AU')
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
        [InlineKeyboardButton("📜 Правила", callback_data='rules')],
        [InlineKeyboardButton("👑 Админ", callback_data='admin')]
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
                    text=f"🆘 Новое обращение от @{user.username or user.first_name} (ID: {user.id})\n\nПользователь ждет ответа!"
                )
            except:
                pass
        await query.message.edit_text("✅ Ваше обращение отправлено администраторам!")
    elif query.data == 'whitelist':
        await query.message.edit_text("📝 Выберите тип заявки:\n\n🎫 Бесплатная\n💎 Платная (приоритет)")
    elif query.data == 'donate':
        await query.message.edit_text("💎 Донат меню:\n\n🔫 Лицензия на оружие\n🔓 Разбан\n🍺 Лицензия на алкоголь")
    elif query.data == 'rules':
        await query.message.edit_text("📜 Правила сервера...")
    elif query.data == 'admin':
        if query.from_user.id in ADMINS:
            await query.message.edit_text("👑 Админ-панель")
        else:
            await query.message.edit_text("⛔ Нет доступа!")

# Регистрация обработчиков
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))

# ========== WEBHOOK ==========
@app.route('/webhook', methods=['POST'])
def webhook():
    json_data = request.get_json(force=True)
    update = Update.de_json(json_data, application.bot)
    application.update_queue.put_nowait(update)
    return 'ok'

@app.route('/')
def home():
    return """
    <h1>🤖 Minecraft Бот работает!</h1>
    <p>Статус: <span style="color: green;">● Активен</span></p>
    <p>Админ: @lvumba_69</p>
    <p>Проверьте в Telegram</p>
    """

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("🤖 Бот запущен!")
    # На Render Flask запустится сам
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port)