

async def show_people(message, people, main_menu):
    for idx, person in enumerate(list(map(lambda x: '_'.join(x.split('/')[-1].split('_')[0:2]), people))):
        full_name, role = parse_filename(person)
        await message.answer(f"{idx + 1}) {full_name} -- {role}")
    await message.answer("Текущая база людей", reply_markup=main_menu)


def parse_filename(filename):
    full_name, role = filename[:filename.index('-')], filename[filename.index('-') + 1:]
    full_name = " ".join(full_name.split('_'))
    return full_name, role


async def error_message(message, details, state, main_menu):
    await message.answer(f"❗ Что-то пошло не так!\nДетали: {details}",
                         reply_markup=main_menu)
    await message.answer("Повторите попытку позже!",
                         reply_markup=main_menu)
    if state:
        await state.finish()
