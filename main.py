import asyncio

from telegram.ext import ApplicationBuilder, CommandHandler

from bot_commands import start, register_device, delete_device, update_device, get_devices, get_device_information
from config import BOT_TOKEN
from parameter_simulator import modbus_parameter_simulator


loop = asyncio.get_event_loop()
asyncio.ensure_future(modbus_parameter_simulator(605, 33, 10, 1))
# asyncio.ensure_future(modbus_parameter_simulator(600, 40, 100, 2))

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('reg', register_device))
app.add_handler(CommandHandler('del', delete_device))
app.add_handler(CommandHandler('upd', update_device))
app.add_handler(CommandHandler('connected', get_devices))
app.add_handler(CommandHandler('get', get_device_information))
app.run_polling()

loop.run_forever()
