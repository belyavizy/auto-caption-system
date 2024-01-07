import nest_asyncio
import sys
import os

sys.path.insert(0, os.getcwd())

import src.app as app

from telegram.bot import AutoCaptionTelegramBot, ProfileStatesGroup
from aiogram import executor, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import API_TOKEN
from aiogram.dispatcher.filters import Text

nest_asyncio.apply()

storage = MemoryStorage()
bot = Bot(API_TOKEN)
dp = Dispatcher(bot=bot, storage=storage)
auto_caption_bot = AutoCaptionTelegramBot()

if __name__ == '__main__':
    app.run()
    dp.register_message_handler(auto_caption_bot.cmd_start,
                                commands=['start'])
    dp.register_message_handler(auto_caption_bot.cmd_help,
                                commands=['help'])
    dp.register_message_handler(auto_caption_bot.cmd_reg,
                                commands=['reg'])
    dp.register_message_handler(auto_caption_bot.cmd_reg_name,
                                state=ProfileStatesGroup.reg_name)
    dp.register_message_handler(auto_caption_bot.cmd_reg_password,
                                state=ProfileStatesGroup.reg_password)
    dp.register_message_handler(auto_caption_bot.cmd_create,
                                commands=['create'])
    dp.register_message_handler(auto_caption_bot.cmd_create_name,
                                state=ProfileStatesGroup.crt_name)
    dp.register_message_handler(auto_caption_bot.cmd_create_password,
                                state=ProfileStatesGroup.crt_password)
    dp.register_message_handler(auto_caption_bot.cmd_add,
                                Text(equals="Добавить фото 📷"))
    dp.register_message_handler(auto_caption_bot.cmd_add_name,
                                state=ProfileStatesGroup.add_name)
    dp.register_message_handler(auto_caption_bot.cmd_add_photo,
                                content_types=['photo'],
                                state=ProfileStatesGroup.add_photo)
    dp.register_message_handler(auto_caption_bot.cmd_del,
                                Text(equals="Удалить фото ✋🏻"))
    dp.register_message_handler(auto_caption_bot.del_photo,
                                state=ProfileStatesGroup.delete_photo)
    dp.register_message_handler(auto_caption_bot.cmd_show_all_people,
                                Text(equals="Вывести внесенных людей 👀"))
    dp.register_message_handler(auto_caption_bot.cmd_show_person,
                                Text(equals="Вывести человека с фото 👁️"))
    dp.register_message_handler(auto_caption_bot.cmd_show_person_photo,
                                state=ProfileStatesGroup.select_person)
    dp.register_message_handler(auto_caption_bot.cmd_show_obs,
                                Text(equals="Показать OBS config"))
    dp.register_message_handler(auto_caption_bot.cmd_choose_template,
                                Text(equals="Выбрать шаблон титра 🖼"))
    dp.register_message_handler(auto_caption_bot.cmd_choose_template_set,
                                state=ProfileStatesGroup.set_template)
    dp.register_message_handler(auto_caption_bot.cmd_edit, Text(equals="Редактировать инф-ию о человеке 📝"))
    dp.register_message_handler(auto_caption_bot.cmd_edit_idx, state=ProfileStatesGroup.edit_idx)
    dp.register_message_handler(auto_caption_bot.cmd_edit_name, state=ProfileStatesGroup.edit_name)
    dp.register_message_handler(auto_caption_bot.cmd_end_rec, Text(equals="Закончить распознавание 🚫"), state='*')
    dp.register_message_handler(auto_caption_bot.cmd_obs,
                                Text(equals="Настроить OBS ⚙️"))
    dp.register_message_handler(auto_caption_bot.cmd_obs_host,
                                state=ProfileStatesGroup.set_ip)
    dp.register_message_handler(auto_caption_bot.cmd_obs_port,
                                state=ProfileStatesGroup.set_port)
    dp.register_message_handler(auto_caption_bot.cmd_obs_password,
                                state=ProfileStatesGroup.set_password)
    dp.register_message_handler(auto_caption_bot.cmd_start_rec, Text(equals="Начать распознавание 🔍"))
    dp.register_message_handler(auto_caption_bot.cmd_start_rec_rtsp, state=ProfileStatesGroup.uri)
    dp.register_callback_query_handler(auto_caption_bot.callback_cancel, state='*')
    dp.register_message_handler(auto_caption_bot.cmd_strange_message, state='*')
    executor.start_polling(dp,skip_updates=True)
