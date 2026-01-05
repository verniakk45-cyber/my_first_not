import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, InlineKeyboardMarkup,
    InlineKeyboardButton, CallbackQuery, ForceReply
)

TOKEN = "7742437832:AAFYZxTxajTLSQn_0R_B1HHH6PDYCiI2dGY"
ADMINS = [1628291205, 928207798, 929273339]
CHAT_ID = -1002797249188

bot = Bot(token=TOKEN)
dp = Dispatcher()

form_id = 22340
pending_declines = {}  # admin_id: (message_id, form_id)


@dp.message(F.chat.id == CHAT_ID)
async def handle_form(message: Message):
    global form_id

    # Если админ вводит причину отказа
    if message.from_user.id in pending_declines:
        form_msg_id, fid = pending_declines.pop(message.from_user.id)

        reason = message.text
        admin = message.from_user.full_name

        await bot.delete_message(message.chat.id, message.message_id)

        text = (
            f"⛔️ **[#${fid}] Форма была отклонена**\n\n"
            f"📌 Причина: {reason}\n"
            f"👮 Администратор — {admin}"
        )

        await bot.edit_message_text(
            chat_id=CHAT_ID,
            message_id=form_msg_id,
            text=text,
            parse_mode="Markdown"
        )
        return

    # Обычное сообщение игрока → форма
    await bot.delete_message(message.chat.id, message.message_id)
    form_id += 1

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept:{form_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline:{form_id}")
        ]
    ])

    text = (
        f"📄 **Форма #{form_id}**\n\n"
        f"👤 От: {message.from_user.full_name}\n"
        f"📝 Текст:\n{message.text}"
    )

    sent = await bot.send_message(
        chat_id=CHAT_ID,
        text=text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@dp.callback_query()
async def handle_decision(call: CallbackQuery):
    action, fid = call.data.split(":")
    admin = call.from_user

    if admin.id not in ADMINS:
        await call.answer("❌ У тебя нет прав", show_alert=True)
        return

    if action == "accept":
        text = (
            f"✅ **[#${fid}] Форма была принята**\n"
            f"👮 Администратор — {admin.full_name}"
        )
        await call.message.edit_text(text, parse_mode="Markdown")
        await call.answer("Форма принята")

    elif action == "decline":
        pending_declines[admin.id] = (call.message.message_id, fid)

        await call.message.reply(
            "✏️ Введите причину отказа:",
            reply_markup=ForceReply()
        )
        await call.answer("Ожидаю причину")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())