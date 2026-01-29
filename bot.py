import os
import logging
import asyncio
from threading import Thread
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ========== КОНФИГУРАЦИЯ ==========
TOKEN = os.getenv('TELEGRAM_TOKEN', '8297599326:AAFIts64NWbahE2acjBVOWEoq84hvbHv8AU')
ADMIN_ID = 5350202227
ADMINS = [5350202227]  # Добавьте сюда ID администраторов через запятую

# ========== FLASK ДЛЯ WEBHOOK ==========
app = Flask(__name__)

# ========== СОЗДАЕМ БОТА ==========
application = Application.builder().token(TOKEN).build()

# ========== ВАШ КОД С ФУНКЦИЯМИ ==========
# Вставьте сюда ВЕСЬ ваш код из предыдущего сообщения, начиная с:
# def main_menu_keyboard():
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
# async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
# и все остальные функции...

# Но я дам УПРОЩЕННУЮ версию для начала:

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Вайтлист", callback_data='whitelist')],
        [InlineKeyboardButton("💬 Поддержка", callback_data='support')],
        [InlineKeyboardButton("💎 Донат", callback_data='donate')],
        [InlineKeyboardButton("📜 Правила", callback_data='rules')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 Привет, {update.effective_user.first_name}!\nВыбери действие:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'whitelist':
        await query.message.edit_text(
            "📝 Выберите тип заявки:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎫 Бесплатная", callback_data='free')],
                [InlineKeyboardButton("💎 Платная", callback_data='paid')],
                [InlineKeyboardButton("🔙 Назад", callback_data='back')]
            ])
        )
    elif query.data == 'support':
        user_id = query.from_user.id
        # Сохраняем, что пользователь пишет в поддержку
        context.user_data['awaiting_support'] = True
        await query.message.edit_text(
            "💬 Опишите вашу проблему. Администрация получит уведомление."
        )
    elif query.data == 'donate':
        await query.message.edit_text(
            "💎 Выберите тип доната:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔫 Лицензия на оружие", callback_data='donate_gun')],
                [InlineKeyboardButton("🔓 Разбан", callback_data='donate_unban')],
                [InlineKeyboardButton("💰 Пожертвования", callback_data='donations')],
                [InlineKeyboardButton("🔙 Назад", callback_data='back')]
            ])
        )
    elif query.data == 'rules':
        rules_text = "📜 Правила сервера... (вставьте ваши правила здесь)"
        await query.message.edit_text(rules_text[:4000])  # Ограничение Telegram

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_support'):
        user = update.effective_user
        message = update.message.text
        
        # Отправляем админам
        admin_msg = f"🆘 НОВОЕ ОБРАЩЕНИЕ:\nОт: @{user.username or user.first_name}\nID: {user.id}\n\n{message}"
        
        for admin_id in ADMINS:
            try:
                await context.bot.send_message(chat_id=admin_id, text=admin_msg)
            except:
                pass
        
        await update.message.reply_text("✅ Ваше обращение отправлено администраторам!")
        context.user_data['awaiting_support'] = False

# Регистрируем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ========== WEBHOOK РОУТЫ ==========
@app.route('/webhook', methods=['POST'])
def webhook():
    """Принимаем обновления от Telegram"""
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return 'ok'

@app.route('/')
def home():
    """Главная страница для проверки работы"""
    return """
    <h1>🤖 Бот Minecraft сервера работает!</h1>
    <p>Статус: <span style="color: green;">● Активен</span></p>
    <p>Админ: @lvumba_69 (ID: 5350202227)</p>
    <p>Проверьте бота в Telegram</p>
    """

# ========== ЗАПУСК ==========
def run_flask():
    """Запускаем Flask в отдельном потоке"""
    app.run(host='0.0.0.0', port=10000, debug=False)

async def main():
    """Основная функция запуска"""
    print("🚀 Запуск бота...")
    
    # Запускаем Flask в фоне
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Ждем немного для старта Flask
    await asyncio.sleep(2)
    
    # Устанавливаем вебхук
    webhook_url = os.getenv('RENDER_EXTERNAL_URL', '') + '/webhook'
    if webhook_url.startswith('https://'):
        await application.bot.set_webhook(webhook_url)
        print(f"✅ Webhook установлен: {webhook_url}")
    else:
        print("⚠️ Webhook URL не найден, используем локальный режим")
    
    # Запускаем обработку обновлений
    await application.initialize()
    await application.start()
    await application.updater.start_webhook(
        listen='0.0.0.0',
        port=10000,
        url_path=TOKEN,
        webhook_url=webhook_url
    )
    
    print("✅ Бот успешно запущен!")
    
    # Бесконечное ожидание
    await asyncio.Event().wait()

if __name__ == '__main__':
    # Для Render
    if os.getenv('RENDER'):
        asyncio.run(main())
    else:
        # Для локального тестирования
        print("🤖 Локальный запуск...")
        application.run_polling()