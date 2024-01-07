from aiogram.dispatcher.filters.state import StatesGroup, State


class ProfileStatesGroup(StatesGroup):
    reg_name = State()
    reg_password = State()

    crt_name = State()
    crt_password = State()

    add_name = State()
    add_photo = State()

    delete_photo = State()

    uri = State()
    end_rec = State()

    select_person = State()

    edit_idx = State()
    edit_name = State()

    password = State()

    set_ip = State()
    set_port = State()
    set_password = State()

    set_template = State()
