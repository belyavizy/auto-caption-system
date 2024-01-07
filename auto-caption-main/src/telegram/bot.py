import os
import re

import requests as rq

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from src.telegram.constants import HELP, API_URL
from src.telegram.markups import main_menu, inline_menu, inline_edit_menu
from src.telegram.states_group import ProfileStatesGroup
from src.telegram.utils import show_people, error_message, parse_filename
import src.app as app


class AutoCaptionTelegramBot:
    async def cmd_start(self, message: types.Message):
        await message.answer(f"Boom! 💥 Выберите из меню ниже 👇. Если что-то не понятно, напиши /help",
                             reply_markup=main_menu)
        await message.delete()

    async def cmd_help(self, message: types.Message):
        await message.answer(HELP, reply_markup=main_menu, parse_mode='HTML')
        await message.delete()

# --------------------------------------------Регистрация в команду-----------------------------------------------------
    async def cmd_reg(self, message: types.Message):
        await message.answer("Введите название команды!",
                             reply_markup=inline_menu)
        await ProfileStatesGroup.reg_name.set()

    async def cmd_reg_name(self, message: types.Message, state: FSMContext):
        is_team = rq.get(API_URL + 'check/is_team', params={'name': message.text}).json()
        if is_team['status'] == 'success':
            if is_team['data']:
                async with state.proxy() as data:
                    data['reg_name'] = message.text
                await message.answer("А теперь введите пароль для входа в команду!",
                                     reply_markup=inline_menu)
                await ProfileStatesGroup.next()
            else:
                await message.answer("⚠️ Такой команды не существует! Введите другое название!",
                                     reply_markup=inline_menu)
        else:
            await error_message(message, is_team['details'], state, main_menu)

    async def cmd_reg_password(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            reg_name = data['reg_name']
            is_password = rq.get(API_URL + 'check/password',
                                 params={'password': message.text,
                                         'name': reg_name}
                                 ).json()
        if is_password['status'] == 'success':
            if is_password['data']['is_password']:
                resp = rq.post(API_URL + 'update/user',
                               params={
                                   'team_id': is_password['data']['team_id'],
                                   'user_id': message.from_id
                               }
                               ).json()
                if resp['status'] == 'success':
                    await message.answer("Вы вошли!", reply_markup=main_menu)
                    await state.finish()
                else:
                    await error_message(message, resp['details'], state, main_menu)
            else:
                await message.answer("⚠️ Неверный пароль! Повторите попытку!", reply_markup=inline_menu)
        else:
            await error_message(message, is_password['details'], state, main_menu)
# --------------------------------------------Регистрация в команду-----------------------------------------------------

# --------------------------------------------Создание команды----------------------------------------------------------
    async def cmd_create(self, message: types.Message):
        await message.answer("Придумайте название команды!",
                             reply_markup=inline_menu)
        await ProfileStatesGroup.crt_name.set()

    async def cmd_create_name(self, message: types.Message, state: FSMContext):
        is_team = rq.get(API_URL + 'check/is_team', params={'name': message.text}).json()
        if is_team['status'] == 'success':
            if is_team['data']:
                await message.answer("⚠️ Такая команда существует! Введите другое название!",
                                     reply_markup=inline_menu)
            else:
                async with state.proxy() as data:
                    data['crt_name'] = message.text
                await message.answer("А теперь придумайте пароль для входа в команду!",
                                     reply_markup=inline_menu)
                await ProfileStatesGroup.next()
        else:
            await error_message(message, is_team['details'], state, main_menu)

    async def cmd_create_password(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            add_team = rq.post(API_URL + 'update/add_team',
                               params={
                                   'user_id': message.from_id,
                                   'name': data['crt_name'],
                                   'password': message.text
                               }).json()
        if add_team['status'] == 'success':
            await message.answer("Вы создали команду!",
                                 reply_markup=main_menu)
            await state.finish()
        else:
            await error_message(message, add_team['details'], state, main_menu)
# --------------------------------------------Создание команды----------------------------------------------------------

# --------------------------------------------Добавление фото-----------------------------------------------------------
    async def cmd_add(self, message: types.Message):
        get_team = rq.get(API_URL + 'get/team_by_user', params={'user_id': message.from_id}).json()
        if get_team['status'] == 'success':
            if get_team['data'] is None:
                await message.answer("⚠️ Вы не вошли в команду!",
                                     reply_markup=main_menu)
            else:
                await message.reply("Введи данные человека в формате: Имя Фамилия-Роль (e.g. Иван Иванов-Программист)",
                                    reply_markup=inline_menu)
                await ProfileStatesGroup.add_name.set()
                state = Dispatcher.get_current().current_state()
                async with state.proxy() as data:
                    data['team_id'] = get_team['data']
        else:
            await error_message(message, get_team['details'], None, main_menu)

    async def cmd_add_name(self, message: types.Message, state: FSMContext):
        check_name = rq.get(API_URL + 'check/name', params={'name': message.text}).json()
        if check_name['status'] == 'success':
            if check_name['data']:
                async with state.proxy() as data:
                    data['add_name'] = message.text
                await message.answer("Теперь прикрепите фото, на котором хорошо видно лицо человека!",
                                     reply_markup=inline_menu)
                await ProfileStatesGroup.next()
            else:
                await message.answer(
                    "Неверный формат! Введи данные человека в формате: Имя Фамилия-Роль (e.g. Иван Иванов-Программист)",
                    reply_markup=inline_menu)
        else:
            await error_message(message, check_name['details'], state, main_menu)

    async def cmd_add_photo(self, message: types.Message, state: FSMContext):
        photo_file = await message.photo[-1].download()
        photo_file.close()
        check_photo = rq.get(API_URL + 'check/photo', params={'path': photo_file.name}).json()
        if check_photo['status'] == 'success':
            if check_photo['data'] > 1:
                await message.answer(f"⚠️ В кадре больше 1 человека! Выберите другое фото!",
                                     reply_markup=inline_menu)
            elif check_photo['data'] == 0:
                await message.answer(f"⚠️ Лицо не было распознано! Выберите другое фото!",
                                     reply_markup=inline_menu)
            else:
                async with state.proxy() as data:
                    add_photo = rq.post(API_URL + 'update/photo',
                                        params={
                                            'path': os.path.abspath(photo_file.name),
                                            'name': data['add_name'],
                                            'team_id': data['team_id']
                                        }).json()
                if add_photo['status'] == 'success':
                    await message.answer("Фото успешно добавлено!",
                                         reply_markup=main_menu)
                    await state.finish()
                else:
                    await error_message(message, add_photo['details'], state, main_menu)
        else:
            await error_message(message, check_photo['details'], state, main_menu)

# --------------------------------------------Добавление фото-----------------------------------------------------------

# --------------------------------------------Удаление фото-------------------------------------------------------------
    async def cmd_del(self, message: types.Message):
        get_team = rq.get(API_URL + 'get/team_by_user', params={'user_id': message.from_id}).json()
        if get_team['status'] == 'success':
            if get_team['data'] is None:
                await message.answer("⚠️ Вы не вошли в команду!",
                                     reply_markup=main_menu)
            else:
                get_people = rq.get(API_URL + 'get/people', params={'team_id': get_team['data']}).json()
                if get_people['status'] == 'success':
                    if len(get_people['data']) > 0:
                        await show_people(message, get_people['data'], main_menu)
                        await message.answer(
                            f"Введите порядковый номер человека (от 1 до {len(get_people['data'])}), "
                            f"которого хотите удалить",
                            reply_markup=inline_menu)
                        await ProfileStatesGroup.delete_photo.set()

                        state = Dispatcher.get_current().current_state()
                        async with state.proxy() as data:
                            data['people'] = get_people['data']
                    else:
                        await message.answer("⚠️ Вы не добавляли фото людей!", reply_markup=main_menu)
                else:
                    await error_message(message, get_people['details'], None, main_menu)
        else:
            await error_message(message, get_team['details'], None, main_menu)

    async def del_photo(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            people = data['people']

        if re.fullmatch('\\d+', message.text):
            idx = int(message.text) - 1

            if idx <= -1 or idx >= len(people):
                await message.answer(f"⚠️ Число не попадает в интервал от 1 до {len(people)}",
                                     reply_markup=inline_menu)
            else:
                delete_photo = rq.delete(API_URL + 'delete/photo',
                                         params={
                                             'path': people[idx]
                                         }).json()
                if delete_photo['status'] == 'success':
                    person = '_'.join(people[idx].split('/')[-1].split('_')[0:2])
                    await message.answer(f"Фото №{idx + 1}({person}) успешно удалено",
                                         reply_markup=main_menu)
                    await state.finish()
                else:
                    await error_message(message, delete_photo['details'], state, main_menu)
        else:
            await message.answer(
                f"Неверный формат! Введите порядковый номер человека (от 1 до {len(people)}), которого хотите удалить",
                reply_markup=inline_menu)

# --------------------------------------------Удаление фото-------------------------------------------------------------

# --------------------------------------------Вывод всех----------------------------------------------------------------
    async def cmd_show_all_people(self, message: types.Message):
        get_team = rq.get(API_URL + 'get/team_by_user', params={'user_id': message.from_id}).json()
        if get_team['status'] == 'success':
            if get_team['data'] is None:
                await message.answer("⚠️ Вы не вошли в команду!",
                                     reply_markup=main_menu)
            else:
                get_people = rq.get(API_URL + 'get/people', params={'team_id': get_team['data']}).json()
                if get_people['status'] == 'success':
                    if len(get_people['data']) > 0:
                        await show_people(message, get_people['data'], main_menu)
                    else:
                        await message.answer("⚠️ Вы не добавляли фото людей!", reply_markup=main_menu)
                else:
                    await error_message(message, get_people['details'], None, main_menu)
        else:
            await error_message(message, get_team['details'], None, main_menu)

# --------------------------------------------Вывод всех----------------------------------------------------------------

# --------------------------------------------Вывести человека с фото---------------------------------------------------
    async def cmd_show_person(self, message: types.Message):
        get_team = rq.get(API_URL + 'get/team_by_user', params={'user_id': message.from_id}).json()
        if get_team['status'] == 'success':
            if get_team['data'] is None:
                await message.answer("⚠️ Вы не вошли в команду!",
                                     reply_markup=main_menu)
            else:
                get_people = rq.get(API_URL + 'get/people', params={'team_id': get_team['data']}).json()
                if get_people['status'] == 'success':
                    if len(get_people['data']) > 0:
                        await show_people(message, get_people['data'], main_menu)
                        await message.answer(
                            f"Введите порядковый номер человека (от 1 до {len(get_people['data'])}),"
                            f"фото которого хотите посмотреть",
                            reply_markup=inline_menu)
                        await ProfileStatesGroup.select_person.set()
                        state = Dispatcher.get_current().current_state()
                        async with state.proxy() as data:
                            data['people'] = get_people['data']
                    else:
                        await message.answer("⚠️ Вы не добавляли фото людей!", reply_markup=main_menu)
                else:
                    await error_message(message, get_people['details'], None, main_menu)
        else:
            await error_message(message, get_team['details'], None, main_menu)

    async def cmd_show_person_photo(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            people = data['people']

        if re.fullmatch('\\d+', message.text):
            idx = int(message.text) - 1

            if idx <= -1 or idx >= len(people):
                await message.answer(f"⚠️ Число не попадает в интервал от 1 до {len(people)}",
                                     reply_markup=inline_menu)
            else:
                print(people[idx])
                with open(people[idx], "rb") as photo:
                    full_name, role = parse_filename('_'.join(people[idx].split('/')[-1].split('_')[0:2]))
                    await message.answer_photo(photo, caption=f"{full_name} -- {role}")
                await state.finish()
        else:
            await message.answer(
                f"Неверный формат! Введите порядковый номер человека (от 1 до {len(people)}), "
                f"фото которого хотите посмотреть",
                reply_markup=inline_menu)

# --------------------------------------------Вывести человека с фото---------------------------------------------------

# --------------------------------------------Редактировать имя---------------------------------------------------------
    async def cmd_edit(self, message: types.Message):
        await message.answer("Кнопка ещё не доделана!", reply_markup=main_menu)
        # get_team = rq.get(API_URL + 'get/team_by_user',params={'user_id': message.from_id}).json()
        # if get_team['status'] == 'success':
        #     if get_team['data'] is None:
        #         await message.answer("⚠️ Вы не вошли в команду!",
        #                              reply_markup=main_menu)
        #     else:
        #         get_people = rq.get(API_URL + 'get/people', params={'team_id': get_team['data']}).json()
        #         if get_people['status'] == 'success':
        #             if len(get_people['data']) > 0:
        #                 await show_people(message, get_people['data'], main_menu)
        #                 await message.answer(
        #                     f"Введите порядковый номер человека (от 1 до {len(get_people['data'])}),"
        #                     f"фото которого хотите посмотреть",
        #                     reply_markup=inline_menu)
        #                 await ProfileStatesGroup.edit_idx.set()
        #                 state = Dispatcher.get_current().current_state()
        #                 async with state.proxy() as data:
        #                     data['people'] = get_people['data']
        #             else:
        #                 await message.answer("⚠️ Вы не добавляли фото людей!", reply_markup=main_menu)
        #         else:
        #             await error_message(message, get_people['details'], None, main_menu)
        # else:
        #     await error_message(message, get_team['details'], None, main_menu)

    async def cmd_edit_idx(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            people = data['people']

        if re.fullmatch('\\d+', message.text):
            idx = int(message.text) - 1

            if idx <= -1 or idx >= len(people):
                await message.answer(f"⚠️ Число не попадает в интервал от 1 до {len(people)}",
                                     reply_markup=inline_menu)
            else:
                async with state.proxy() as data:
                    data['edit_name'] = people[idx]
                await message.answer("Выберете, что вы хотите изменить",
                                     reply_markup=inline_edit_menu)
        else:
            await message.answer(
                f"Неверный формат! Введите порядковый номер человека (от 1 до {len(people)}),"
                f" фото которого хотите посмотреть",
                reply_markup=inline_menu)

    async def cmd_edit_name(self, message: types.Message, state: FSMContext):
        check_name = rq.get(API_URL + 'check/name', params={'name': message.text}).json()
        if check_name['status'] == 'success':
            if check_name['data']:
                async with state.proxy() as data:
                    pass
                await message.answer("Имя изменено!")
                await state.finish()
            else:
                await message.answer(
                    "Неверный формат! Введи данные человека в формате: Имя Фамилия-Роль (e.g. Иван Иванов-Программист)",
                    reply_markup=inline_menu)
        else:
            await error_message(message, check_name['details'], state, main_menu)

# --------------------------------------------Редактировать имя---------------------------------------------------------

# --------------------------------------------OBS config----------------------------------------------------------------
    async def cmd_obs(self, message: types.Message):
        get_team = rq.get(API_URL + 'get/team_by_user', params={'user_id': message.from_id}).json()
        if get_team['status'] == 'success':
            if get_team['data'] is None:
                await message.answer("⚠️ Вы не вошли в команду!",
                                     reply_markup=main_menu)
            else:
                state = Dispatcher.get_current().current_state()
                async with state.proxy() as data:
                    data['team_id'] = get_team['data']
                await message.answer("Введите ip OBS сервера! (Пример: 192.168.12.197)",
                                     reply_markup=inline_menu)
                await ProfileStatesGroup.set_ip.set()
        else:
            await error_message(message, get_team['details'], None, main_menu)

    async def cmd_obs_host(self, message: types.Message, state: FSMContext):
        check_host = rq.get(API_URL + 'check/ipv4', params={'ip': message.text}).json()
        if check_host['status'] == 'success':
            if check_host['data']:
                async with state.proxy() as data:
                    data['host'] = message.text
                await message.answer("Введите порт OBS сервера от 1 до 65535! (Пример: 4445)", reply_markup=inline_menu)
                await ProfileStatesGroup.next()
            else:
                await message.answer("⚠️ Неправильный формат ip! Введите ip OBS сервера! (Пример: 192.168.12.197)",
                                     reply_markup=inline_menu)
        else:
            await error_message(message, check_host['details'], state, main_menu)

    async def cmd_obs_port(self, message: types.Message, state: FSMContext):
        check_host = rq.get(API_URL + 'check/port', params={'port': message.text}).json()
        if check_host['status'] == 'success':
            if check_host['data']:
                async with state.proxy() as data:
                    data['port'] = int(message.text)
                await message.answer("Введите пароль к OBS серверу!", reply_markup=inline_menu)
                await ProfileStatesGroup.next()
            else:
                await message.answer(
                    "⚠️ Неправильный формат порта! Введите порт OBS сервера от 1 до 65535! (Пример: 4445)",
                    reply_markup=inline_menu)
        else:
            await error_message(message, check_host['details'], state, main_menu)

    async def cmd_obs_password(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            set_obs_config = rq.post(API_URL + 'update/obs_config',
                                     params={
                                         'host': data['host'],
                                         'port': data['port'],
                                         'password': message.text,
                                         'team_id': data['team_id']
                                     }).json()
            if set_obs_config['status'] == 'success':
                await message.answer("OBS подключение настроено!",
                                     reply_markup=main_menu)
                await message.answer(
                    f"Текущие настройки: host:\n{data['host']},\nport: {data['port']},\nпароль: {message.text[0]}***"
                )
                await message.delete()
                await state.finish()
            else:
                await error_message(message, set_obs_config['details'], state, main_menu)

# --------------------------------------------OBS config----------------------------------------------------------------

# --------------------------------------------OBS config show-----------------------------------------------------------
    async def cmd_show_obs(self, message: types.Message):
        get_team = rq.get(API_URL + 'get/team_by_user', params={'user_id': message.from_id}).json()
        if get_team['status'] == 'success':
            if get_team['data'] is None:
                await message.answer("⚠️ Вы не вошли в команду!",
                                     reply_markup=main_menu)
            else:
                get_obs = rq.get(API_URL + 'get/obs_config', params={'team_id': get_team['data']}).json()
                if get_obs['status'] == 'success':
                    if len(get_obs['data']) == 0:
                        await message.answer("⚠️ Вы не установили obs config!",
                                             reply_markup=main_menu)
                    else:
                        dct = get_obs['data'][0]
                        host, port = dct['host'], dct['port']
                        await message.answer(f"Host: {host}, port: {port}!")
                else:
                    await error_message(message, get_obs['details'], None, main_menu)
        else:
            await error_message(message, get_team['details'], None, main_menu)
# --------------------------------------------OBS config show-----------------------------------------------------------

# --------------------------------------------Choose template-----------------------------------------------------------
    async def cmd_choose_template(self, message: types.Message):
        get_team = rq.get(API_URL + 'get/team_by_user', params={'user_id': message.from_id}).json()
        if get_team['status'] == 'success':
            if get_team['data'] is None:
                await message.answer("⚠️ Вы не вошли в команду!",
                                     reply_markup=main_menu)
            else:
                get_templates = rq.get(API_URL + 'get/templates').json()
                if get_templates['status'] == 'success':
                    state = Dispatcher.get_current().current_state()
                    async with state.proxy() as data:
                        data['team_id'] = get_team['data']
                        data['templates'] = get_templates['data']
                    for i, template in enumerate(get_templates['data']):
                        path = 'src/templates/' + template + '.jpg'
                        with open(path, 'rb') as photo:
                            await message.answer_photo(photo, caption=f"{i + 1}) {template}")
                    await message.answer(f"Введите число от 1 до {len(get_templates['data'])}!",
                                         reply_markup=inline_menu)
                    await ProfileStatesGroup.set_template.set()
                else:
                    await error_message(message, get_templates['details'], None, main_menu)
        else:
            await error_message(message, get_team['details'], None, main_menu)

    async def cmd_choose_template_set(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            team_id = data['team_id']
            templates = data['templates']
        if re.fullmatch('\\d+', message.text):
            idx = int(message.text) - 1

            if idx <= -1 or idx >= 3:
                await message.answer(f"⚠️ Число не попадает в интервал от 1 до {len(templates)}",
                                     reply_markup=inline_menu)
            else:
                set_template = rq.post(API_URL + 'update/template_team',
                                       params={
                                           'team_id': team_id,
                                           'template_id': idx
                                       }).json()
                if set_template['status'] == 'success':
                    await message.answer("Вы поменяли шаблон!", reply_markup=main_menu)
                    await state.finish()
                else:
                    await error_message(message, set_template['details'], state, main_menu)
        else:
            await message.answer(
                f"Неверный формат! Введите порядковый номер шаблона (от 1 до {len(templates)}),"
                f" фото которого хотите посмотреть",
                reply_markup=inline_menu)

# --------------------------------------------Choose template-----------------------------------------------------------

# --------------------------------------------Начать распознавание------------------------------------------------------
    async def cmd_start_rec(self, message: types.Message):
        get_team = rq.get(API_URL + 'get/team_by_user', params={'user_id': message.from_id}).json()
        if get_team['status'] == 'success':
            if get_team['data'] is None:
                await message.answer("⚠️ Вы не вошли в команду!",
                                     reply_markup=main_menu)
            else:
                get_people = rq.get(API_URL + 'get/people', params={'team_id': get_team['data']}).json()
                if get_people['status'] == 'success':
                    if len(get_people['data']) > 0:
                        get_template = rq.get(API_URL + 'get/template_by_team',
                                              params={'team_id': get_team['data']}).json()
                        if get_template['status'] == 'success':
                            if get_template['data'] is not None:
                                app.add_rec(get_team['data'], get_people['data'], get_template['data'])
                                await message.answer("Введите uri вашей камеры (Пример: rtsp://192.168.1.11:554/live)",
                                                     reply_markup=inline_menu)
                                await ProfileStatesGroup.uri.set()

                                state = Dispatcher.get_current().current_state()
                                async with state.proxy() as data:
                                    data['team_id'] = get_team['data']
                            else:
                                await message.answer("У команды нет шаблона!",
                                                     reply_markup=main_menu)
                        else:
                            await error_message(message, get_template['details'], None, main_menu)
                    else:
                        await message.answer("⚠️ Вы не добавляли фото людей!", reply_markup=main_menu)
                else:
                    await error_message(message, get_people['details'], None, main_menu)
        else:
            await error_message(message, get_team['details'], None, main_menu)

    async def cmd_start_rec_rtsp(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            start_rec = rq.post(API_URL + 'start_recognition',
                                params={
                                    'rtsp': message.text,
                                    'team_id': data['team_id']
                                }).json()
        if start_rec['status'] == 'success':
            await message.answer("Распознавание началось", reply_markup=main_menu)
            await ProfileStatesGroup.next()
        else:
            await error_message(message, start_rec['details'], state, main_menu)

# --------------------------------------------Начать распознавание-----------------------------------------------------

# --------------------------------------------Закончить распознавание---------------------------------------------------
    async def cmd_end_rec(self, message: types.Message, state: FSMContext):
        get_team = rq.get(API_URL + 'get/team_by_user', params={'user_id': message.from_id}).json()
        if get_team['status'] == 'success':
            end_rec = rq.post(API_URL + 'end_recognition',
                              params={
                                  'team_id': get_team['data']
                              }).json()
            if end_rec['status'] == 'success':
                app.del_rec(get_team['data'])
                await message.answer("Распознавание закончилось!",
                                     reply_markup=main_menu)
                await state.finish()
            else:
                await error_message(message, end_rec['details'], state, main_menu)
        else:
            await error_message(message, get_team['details'], None, main_menu)

# --------------------------------------------Закончить распознавание---------------------------------------------------

    async def callback_cancel(self, callback: types.CallbackQuery, state: FSMContext):
        if callback.data == 'cancel':
            await state.finish()
            await callback.answer("Действие отменено!")
        elif callback.data == 'name':
            await callback.answer(
                "А теперь введи данные человека в формате: Имя Фамилия-Роль (e.g. Иван Иванов-Программист)")
            await ProfileStatesGroup.edit_name.set()

    async def cmd_strange_message(self, message: types.Message):
        await message.answer("Я не знаю такую команду! Не пиши сам команды, кнопки для кого сделаны?😡",
                             reply_markup=main_menu)
