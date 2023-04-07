from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.lexicon import LEXICON
from database.database import get_user_in_status

def create_start_keyboard(status:str) -> InlineKeyboardMarkup:
    """Создает стартовую клавиатуру"""
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    if status == "Admin":
        kb_builder.row(InlineKeyboardButton(
            text=LEXICON["bd_this_month"],
            callback_data="bd_this_month"),
                    InlineKeyboardButton(
            text=LEXICON["bd_next_month"],
            callback_data="bd_next_month"),
                    InlineKeyboardButton(
            text=LEXICON["users_list"],
            callback_data="users_list"),width=1)
        kb_builder.row(InlineKeyboardButton(
            text=LEXICON["edit_phone"],
            callback_data="edit_phone"),
            InlineKeyboardButton(
            text=LEXICON["edit_bank"],
            callback_data="edit_bank"),width=2)  
        kb_builder.row(InlineKeyboardButton(
            text=LEXICON['search_user'],
            callback_data="search_user"),
                       InlineKeyboardButton(       
            text=LEXICON["exit_1"],
            callback_data="exit")
                    ,width=1)
    elif status == "SuperUser":
        kb_builder.row(InlineKeyboardButton(
            text=LEXICON["admins_list"],
            callback_data="admins_list"),
                   InlineKeyboardButton(
                       text=LEXICON["create_bd"],
                       callback_data="create_bd"),
                   InlineKeyboardButton(
                       text=LEXICON["del_bd"],
                       callback_data="del_bd"),
                   InlineKeyboardButton(
                       text=LEXICON["exit_1"],
                       callback_data="exit")
                   ,width=1)
    return kb_builder.as_markup()

def create_userlist_keyboard(status:str, now:int, all:int) -> InlineKeyboardMarkup:
    """Создает клавиатуру со списком пользователей"""
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    if status == "SuperUser":
        kb_builder.row(InlineKeyboardButton(
            text=LEXICON["add_admin"],
            callback_data="add_admin"),
                    InlineKeyboardButton(
                        text=LEXICON["del_admin"],
                        callback_data="del_admin"))
    elif status == "Admin":
        kb_builder.row(InlineKeyboardButton(
            text=f'{"<<" if now != 1 else "|"}',
            callback_data=f'{"prew" if now != 1 else "stop_prew"}'),
                       InlineKeyboardButton(
                           text=f'{now}/{all}',
                           callback_data='#'),
                       InlineKeyboardButton(
                           text=f'{">>" if now != all else "|"}',
                           callback_data=f'{"next" if now != all else "stop_next"}'))
        kb_builder.row(InlineKeyboardButton(
            text=LEXICON["add_user"],
            callback_data="add_user"))
        kb_builder.row(InlineKeyboardButton(
            text=LEXICON["edit_user"],
            callback_data="edit_user"))
        kb_builder.row(InlineKeyboardButton(
            text=LEXICON["del_user"],
            callback_data="del_user"))
    kb_builder.row(InlineKeyboardButton(
        text=LEXICON["exit"],
        callback_data="main_menu"))
    return kb_builder.as_markup()

def edit_status_user_keyboard(status:str, action:str, now:int = 0) -> InlineKeyboardMarkup:
    """Создает клавиатуру для изменения списка пользователей"""
    kb_builder:InlineKeyboardBuilder = InlineKeyboardBuilder()
    if status == "SuperUser":
        if action == "add":
            for user in get_user_in_status("User"):
                kb_builder.row(InlineKeyboardButton(
                    text=f"➕ {user[0]} {user[1]}",
                    callback_data=f"add_admin{user[2]}")
                       )
        if action == "del":
            for admin in get_user_in_status("Admin"):
                kb_builder.row(InlineKeyboardButton(
                    text=f"❌ {admin[0]} {admin[1]}",
                    callback_data=f"del_admin{admin[2]}")
                               )
    elif status == "Admin":
        if action == "del":
            prepare_list = get_user_in_status()
            all = len(prepare_list)
            for admin in prepare_list[now]:
                kb_builder.row(InlineKeyboardButton(
                    text=f"❌ {admin[0]} {admin[1]}",
                    callback_data=f"del_user{admin[3]}")
                               )
            kb_builder.row(InlineKeyboardButton(
                text=f'{"<<" if now != 1 else "|"}',
                callback_data=f'{"prew_del" if now != 1 else "stop_prew_del"}'),
                            InlineKeyboardButton(
                                text=f'{now}/{all}',
                                callback_data='#_del'),
                            InlineKeyboardButton(
                                text=f'{">>" if now != all else "|"}',
                                callback_data=f'{"next_del" if now != all else "stop_next_del"}'))
            
        if action == "edit":
            prepare_list = get_user_in_status()
            all = len(prepare_list)
            for admin in prepare_list[now]:
                kb_builder.row(InlineKeyboardButton(
                    text=f"✏️ {admin[0]} {admin[1]}",
                    callback_data=f"{admin[3]}")
                               )
            kb_builder.row(InlineKeyboardButton(
                text=f'{"<<" if now != 1 else "|"}',
                callback_data=f'{"prew_edit" if now != 1 else "stop_prew_edit"}'),
                            InlineKeyboardButton(
                                text=f'{now}/{all}',
                                callback_data='#_edit'),
                            InlineKeyboardButton(
                                text=f'{">>" if now != all else "|"}',
                                callback_data=f'{"next_edit" if now != all else "stop_next_edit"}'))
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON["exit"],
            callback_data="main_menu")
        )
    return kb_builder.as_markup()

def footer_keyboard() -> InlineKeyboardMarkup:
    """Создает базовые кнопки"""
    kb_builder:InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON["exit"],
            callback_data="main_menu")
        )
    return kb_builder.as_markup()

def edit_user_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для редактирования данных о пользователе
    id_-id пользователя для редактирования"""
    kb_builder:InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON["edit_name"],
            callback_data="edit_name"))
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON["edit_surname"],
            callback_data="edit_surname"))
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON["edit_date"],
            callback_data="edit_date"))
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON["edit_status_walley"],
            callback_data="edit_statuswalley"))
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON["edit_cash"],
            callback_data="edit_cash"))
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON["exit"],
            callback_data="main_menu"))
    return kb_builder.as_markup()

def premenu_keyboard() -> InlineKeyboardMarkup:
    kb_builder:InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(InlineKeyboardButton(
            text=LEXICON["admin_status"],
            callback_data="admin_status"),
                   InlineKeyboardButton(
                       text=LEXICON["su_status"],
                       callback_data="su_status"),
                   InlineKeyboardButton(
                       text=LEXICON["exit_1"],
                       callback_data="exit")
                   ,width=1)
    return kb_builder.as_markup()