import asyncio

from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message

from cryptopay import CryptoPay
from cryptopay.types import Invoice

cp = CryptoPay("TOKEN")
bot = Bot("TOKEN")
dp = Dispatcher(bot)


@dp.message_handler()
async def get_invoice(message: Message) -> None:
    invoice = await cp.create_invoice(1, "USDT")
    await message.answer(f"pay: {invoice.mini_app_invoice_url}")
    invoice.await_payment(message=message)


@cp.polling_handler()
async def handle_payment(
    invoice: Invoice,
    message: Message,
) -> None:
    await message.answer(
        f"payment received: {invoice.amount} {invoice.asset.value}",
    )


async def on_startup(_) -> None:
    asyncio.create_task(cp.run_polling())


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
