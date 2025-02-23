from functools import wraps
from typing import Callable

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_TG_ID


def admin_required(command: Callable[Update, ContextTypes]):
    @wraps(command)
    async def wrapper(update: Update, *args, **kwargs):
        if str(update.effective_user.id) == str(ADMIN_TG_ID):
            return await command(update, *args, **kwargs)
    return wrapper
