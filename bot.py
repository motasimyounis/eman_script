from telegram import Update

from telegram.ext import Application, MessageHandler, CommandHandler, filters, CallbackContext

TOKEN = "7844636111:AAEaXz9IuQFELRdYgQezqtZ5PvTcrqvjXCA"

GROUP_CHAT_ID = -1002179170764  
user_message_map = {}



async def start(update: Update, context: CallbackContext) -> None:
    """ترحيب عند بدء البوت"""
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"مرحبًا {user_name}! 👋\nأنا سأقوم بتحويل جميع رسائلك إلى المجموعة، وعند الرد عليها ستصلك في الخاص.")

async def help_command(update: Update, context: CallbackContext) -> None:
    """إرسال رسالة مساعدة للمستخدمين"""
    await update.message.reply_text(
        "📌 كيف تستخدم البوت؟\n\n"
        "1️⃣ أرسل لي أي رسالة في الخاص، وسوف يتم نشرها في المجموعة.\n"
        "2️⃣ عندما يتم الرد عليك في المجموعة، ستتلقى الرد في الخاص.\n"
        "3️⃣ تأكد أنك بدأت المحادثة معي أولًا عبر الضغط على اسمي في تيليجرام وكتابة `/start`."
    )
async def forward_to_group(update: Update, context: CallbackContext) -> None:
    """تحويل رسالة المستخدم إلى المجموعة وتخزين معرفه"""
    message = update.message
    if message and message.text:
        try:
            # 🔹 إرسال الرسالة إلى المجموعة
            forwarded_message = await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=f"📩 رسالة جديدة من {message.from_user.first_name}:\n\n{message.text}"
            )
            
            # 🔹 تخزين معرف المستخدم وربطه بمعرف رسالة المجموعة
            user_message_map[forwarded_message.message_id] = message.from_user.id
        except Exception as e:
            print(f"⚠️ خطأ أثناء تحويل الرسالة: {e}")
            await update.message.reply_text("⚠️ لا يمكنني إرسال الرسالة إلى المجموعة. تأكد أنني مشرف في المجموعة!")


async def reply_to_user(update: Update, context: CallbackContext) -> None:
    """إرسال الرد إلى المستخدم في الخاص ومنع الرد من الظهور في المجموعة"""
    message = update.message

    # ✅ تأكد أن الرد على رسالة البوت وليس أي رسالة أخرى
    if message.reply_to_message and message.reply_to_message.message_id in user_message_map:
        user_id = user_message_map[message.reply_to_message.message_id]  # استرجاع معرف المستخدم الأصلي
        
        try:
            # 🔹 إرسال الرد إلى المستخدم في الخاص
            await context.bot.send_message(
                chat_id=user_id,
                text=f"✉️ لديك رد على رسالتك:\n\n{message.text}"
            )

            # await message.delete()
        except Exception as e:
            print(f"⚠️ لا يمكن إرسال رسالة خاصة إلى المستخدم: {e}")
            await update.message.reply_text(f"⚠️ لا يمكنني مراسلة المستخدم في الخاص. \n\n✉️ من فضلك اطلب منه أن يبدأ محادثة معي عبر الضغط على **{context.bot.username}** وإرسال `/start`.")



def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, forward_to_group))
    app.add_handler(MessageHandler(filters.REPLY & filters.TEXT & filters.Chat(GROUP_CHAT_ID), reply_to_user))

    print("✅ البوت يعمل الآن وينقل الرسائل إلى المجموعة ويرد في الخاص فقط...")
    app.run_polling()

if __name__ == '__main__':
    main()
