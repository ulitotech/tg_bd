from aiogram import Router, F
from aiogram.filters import Text, StateFilter
from aiogram.types import CallbackQuery, Message
from database.database import change_user, creating_db, add_user, del_db, del_user, get_user_in_status, get_month_bd, get_notif_param, change_notif, get_user_in_surname
from lexicon.lexicon import LEXICON, month
from filters.filters import Is_Admin, Is_Superuser, DateCheck, IsContact, Superuser
from keyboards.main_keyboards import *
import datetime
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.fsm.storage.memory import MemoryStorage
router = Router()
storage: MemoryStorage = MemoryStorage()
user_page = {}

#Класс для состояний создания пользователя
class FSMFillForm(StatesGroup):
    fill_name = State()
    fill_surname = State()
    fill_date = State()
    fill_id = State()
    fill_satus_walley = State()
    
#Класс для состояний изменения параметров пользователя
class FSMEditForm(StatesGroup):
    start_edit = State()
    edit_name = State()
    edit_surname = State()
    edit_date = State()
    edit_statuswalley = State()
    edit_cash = State()
    process_edit = State()
 
#Класс для состояний изменения параметров оповещения
class FSMEditNotif(StatesGroup):
    edit_phone = State()
    edit_bank = State()
#Класс для состояний поиска именинников   
class FSMSearchUser(StatesGroup):
    input_surname = State()
   
#Пременю superuser
@router.message(Superuser(), Text(text='/start'))
@router.callback_query(Superuser(), Text(text='main_menu'))
async def premenu_su(msg:Message|CallbackQuery, state : FSMContext):
    await state.clear()   
    if type(msg) == Message:
        await msg.answer(
            text="Выбери свой статус:",
            reply_markup=premenu_keyboard()
            )
        await msg.delete()
    else:
        await msg.message.answer(
            text="Выбери свой статус:",
            reply_markup=premenu_keyboard()
            )
        await msg.message.delete() 
            
#Вызов стартового меню для superuser\superadmin
@router.callback_query(Text(text=["admin_status", "su_status"]))    
async def process_start_su(callback: CallbackQuery):   
    if callback.data =='admin_status':
        await change_user(id_=callback.from_user.id, param="status", new_value="SuperAdmin")
        await callback.message.answer(
            text="Выбери одну из команд:",
            reply_markup=create_start_keyboard("Admin")
            )
    elif callback.data =='su_status':
        await change_user(id_=callback.from_user.id, param="status", new_value="SuperUser")
        await callback.message.answer(
            text="Выбери одну из команд:",
            reply_markup=create_start_keyboard("SuperUser")
            )
    await callback.message.delete()

#Вызов стартового меню для админа
@router.message(Is_Admin(), Text(text='/start'))
@router.callback_query(Is_Admin(), Text(text='main_menu'))
async def process_start_admin(msg:Message|CallbackQuery, state : FSMContext):
    await state.clear()
    if type(msg) == Message:
        await msg.answer(
            text="Выбери одну из команд:",
            reply_markup=create_start_keyboard("Admin")
            )
        await msg.delete()
    else:
        await msg.message.answer(
            text="Выбери одну из команд:",
            reply_markup=create_start_keyboard("Admin")
            )
        await msg.message.delete()


#Поиск именинника по фамилии
@router.callback_query(Is_Admin(), lambda callback: callback.data == "search_user",StateFilter(default_state))
async def search_user(callback:CallbackQuery, state: FSMContext):
    answer = "Введи фамилию для поиска:"
    await callback.message.edit_text(text=answer,reply_markup=footer_keyboard())
    await state.set_state(FSMSearchUser.input_surname)

#Получение данных об имениннике  
@router.message(Is_Admin(), StateFilter(FSMSearchUser.input_surname), F.text.isalpha())
async def get_user_info(message:Message, state: FSMContext):
    await message.answer("Результат поиска:", reply_markup=footer_keyboard())
    await state.clear()
    prepare_list = await get_user_in_surname(message.text)
    now = datetime.datetime.now()
    if len(prepare_list)==0:
        answer_text = "Именинника с такой фамилией нет\.\.\."  
    else: 
        answer_text = "Результат поиска:\n" 
        for u in prepare_list:
            date = u[2].split("-")
            date[0], date[1], date[2] = date[2], month[date[1]], date[0]
            date = " ".join(date)
            age = (now - datetime.datetime.strptime(u[2], "%Y-%m-%d")).days // 365
            age_prefix = "лет" if list(str(age))[1] in ('0','5','6','7','8','9') else 'года'
            status_walley = f"Статус сбора денег: {'Собираем' if u[4] == 'True' else 'Не собираем'}"
            cash = f"Сумма сбора: {u[5]} рублей"
            answer_text+=f"📌 __*{u[0]} {u[1]}*__\n{date}\nВозраст: {age} {age_prefix}\n{status_walley}\n{cash}\n\*\*\*\*\*\*\*\*\*\n"
    await message.answer(text=answer_text,reply_markup=footer_keyboard())
    await message.delete()
    await state.clear()


        
#Смена банка\номера
@router.callback_query(Is_Admin(), lambda callback: callback.data == "edit_phone" or callback.data == "edit_bank", StateFilter(default_state)) 
async def edit_notif_param(callback: CallbackQuery, state:FSMContext):
    if callback.data == "edit_phone":
        phone = get_notif_param('phone')
        answer = f"Введи новый номер \(без пробелов и тире\):\nСтарый: {phone}"
        await callback.message.edit_text(text=answer, reply_markup=footer_keyboard())
        await state.set_state(FSMEditNotif.edit_phone)
    else:
        bank = get_notif_param('bank')
        answer = f"Введи новый банк:\nСтарый: {bank}"
        await callback.message.edit_text(text=answer, reply_markup=footer_keyboard())
        await state.set_state(FSMEditNotif.edit_bank)

#Получение и перезапись телефона  
@router.message(Is_Admin(), StateFilter(FSMEditNotif.edit_phone), F.text.isdigit())
async def edit_notif_phone(message:Message, state: FSMContext):
    await change_notif(param="phone_number",new_value=str(message.text))
    await message.answer("✅Новое значение записано\!✅\nВыбери одну из команд:", reply_markup=create_start_keyboard("Admin"))
    await state.clear()
    
#Получение и перезапись банка
@router.message(Is_Admin(), StateFilter(FSMEditNotif.edit_bank), F.text.isalpha())
async def edit_notif_bank(message:Message, state: FSMContext):
    await change_notif(param="bank",new_value=str(message.text))
    await message.answer("✅Новое значение записано\!✅\nВыбери одну из команд:", reply_markup=create_start_keyboard("Admin"))
    await state.clear()

#Получение справки 
@router.message(lambda x: Is_Superuser() or Is_Admin(),Text(text='/help'))
async def help_process(message:Message, state : FSMContext):
    await state.clear()
    await message.delete()
    await message.answer(text=LEXICON['help'])
    
#Выход из меню взаимодействия  
@router.callback_query(lambda x: Is_Superuser() or Is_Admin(), Text(text='exit'))
async def exit_process(callback:CallbackQuery, state : FSMContext):
    await state.clear()
    await callback.message.answer(text="Для начала работы со мной введи /start")
    await callback.message.delete()
    
#Создание базы данных
@router.callback_query(Is_Superuser(), Text(text='create_bd'))
async def process_creating_bd(callback:CallbackQuery):
    await creating_db()
    await callback.answer(
        text="⚠️ База данных создана")
    
#Удаление базы данных
@router.callback_query(Is_Superuser(), Text(text='del_bd'))
async def process_deleting_bd(callback:CallbackQuery):
    await del_db()
    await callback.answer(
        text="☠️ База данных очищена")

#Получение списка др в этом\сл. месяце
@router.callback_query(Is_Admin(), lambda callback: 'bd_this_month' in callback.data or 'bd_next_month' in callback.data) 
async def get_bd_in_month(callback:CallbackQuery):
    now = datetime.datetime.now()
    month = {'bd_this_month':['now', 'этом'],'bd_next_month':['next','следующем']}
    answer_text = f"__*⚠️В {month[callback.data][1]} месяце празднуют свои ДР:⚠️*__\n"
    bds = [i for i in get_month_bd(month[callback.data][0])]
    bds.sort(key=lambda x: x[2].split("-")[2])
    for bd in bds:
        date = str(bd[2]).split("-")[2]
        age = (now - datetime.datetime.strptime(bd[2], "%Y-%m-%d")).days // 365
        age_prefix = "лет" if list(str(age))[1] in ('0','5','6','7','8','9') else 'года'
        answer_text+=f"🎉‼️ {bd[0]} {bd[1]} ♦️ {date} число ♦️ Исполнится: {age} {age_prefix}\n"
    await callback.message.edit_text(text=answer_text, reply_markup=footer_keyboard())

#Просмотр списока админов и команд
@router.callback_query(Is_Superuser(), Text(text='admins_list'))
async def get_admins_list(callback: CallbackQuery):
    answer_text = "__*Список Админов:*__\n"
    for a in get_user_in_status("Admin"):
        answer_text+=f"▪️ {a[0]} {a[1]}\n"
    await callback.message.edit_text(text=answer_text, reply_markup=create_userlist_keyboard("SuperUser", now = 1, all = 1))

#Просмотр списока всех именинников и команд   
@router.callback_query(Is_Admin(), lambda callback: callback.data in ['users_list', 'next', 'prew', 'stop_prew', 'stop_next', '#'])
async def get_users_list(callback: CallbackQuery):
    now = datetime.datetime.now()
    answer_text = "Список всех именинников:\n"

    if callback.data == "users_list":
        user_page[callback.from_user.id] = 1
    elif callback.data == "next":
        user_page[callback.from_user.id] += 1
    elif callback.data == "prew":
        user_page[callback.from_user.id] -= 1
        
    page = user_page[callback.from_user.id]
    prepare_list = get_user_in_status()
    
    if callback.data in ["#", "stop_next", "stop_prew"]:
        await callback.answer()
    else:
        for u in prepare_list[page]:
            date = u[2].split("-")
            date[0], date[1], date[2] = date[2], month[date[1]], date[0]
            date = " ".join(date)
            age = (now - datetime.datetime.strptime(u[2], "%Y-%m-%d")).days // 365
            age_prefix = "лет" if list(str(age))[1] in ('0','5','6','7','8','9') else 'года'
            status_walley = f"Статус сбора денег: {'Собираем' if u[4] == 'True' else 'Не собираем'}"
            cash = f"Сумма сбора: {u[5]} рублей"
            answer_text+=f"📌 __*{u[0]} {u[1]}*__\n{date}\nВозраст: {age} {age_prefix}\n{status_walley}\n{cash}\n\*\*\*\*\*\*\*\*\*\n"
            
        await callback.message.edit_text(text=answer_text,reply_markup=create_userlist_keyboard("Admin", now=page, all=len(prepare_list)))
 
#Меню удаления админа
@router.callback_query(Is_Superuser(), lambda callback: "del_admin" in callback.data)
async def su_del_menu(callback:CallbackQuery):
    if callback.data.split("del_admin")[1] == "":
        await callback.message.edit_text(
            text="Выбери админа для удаления:",
            reply_markup=edit_status_user_keyboard("SuperUser","del"))
    else:
        await change_user(id_=callback.data.split("del_admin")[1], param="status", new_value="User")
        await callback.message.edit_text(
            text="Выбери админа для удаления:",
            reply_markup=edit_status_user_keyboard("SuperUser","del"))
        
#Меню удаления именинника
@router.callback_query(Is_Admin(), lambda callback: callback.data in ['del_user', 'next_del', 'prew_del', 'stop_prew_del', 'stop_next_del','#_del']
                       or 'del_user' in callback.data)
async def admin_del_menu(callback:CallbackQuery):

    if callback.data == "del_user":
        user_page[callback.from_user.id] = 1
    elif callback.data == "next_del":
        user_page[callback.from_user.id] += 1
    elif callback.data == "prew_del":
        user_page[callback.from_user.id] -= 1
        
    page = user_page[callback.from_user.id]
    
    if callback.data in ["#_del", "stop_next_del", "stop_prew_del"]:
        await callback.answer()
    elif callback.data in ['prew_del','next_del', 'del_user']:
        await callback.message.edit_text(
            text="Выбери именинника для удаления:",
            reply_markup=edit_status_user_keyboard("Admin", "del", now=page)
            )
    else:
        await del_user(id_=callback.data.split("del_user")[1])
        await callback.message.edit_text(
            text="Выбери именинника для удаления:",
            reply_markup=edit_status_user_keyboard("Admin", "del", now=page))

#Меню добавления админа
@router.callback_query(Is_Superuser(), lambda callback: "add_admin" in callback.data)
async def su_del_menu(callback:CallbackQuery):
    if callback.data.split("add_admin")[1] == "":
        await callback.message.edit_text(
            text="Выбери пользователя для добавления в админы:",
            reply_markup=edit_status_user_keyboard("SuperUser","add"))
    else:
        await change_user(id_=callback.data.split("add_admin")[1], param="status", new_value="Admin")
        await callback.message.edit_text(
            text="Выбери пользователя для добавления в админы:",
            reply_markup=edit_status_user_keyboard("SuperUser", "add"))

#Добавление имени нового пользователя
@router.callback_query(Is_Admin(), lambda callback: "add_user" in callback.data, StateFilter(default_state))
async def user_add_name(callback:CallbackQuery,state: FSMContext):
    await callback.message.answer(text="Введи имя пользователя:",reply_markup=footer_keyboard())
    await callback.message.delete()
    await state.set_state(FSMFillForm.fill_name)

#Меню редактирования именинника
@router.callback_query(Is_Admin(), lambda callback: callback.data in ['edit_user', 'next_edit', 'prew_edit', 'stop_prew_edit', 'stop_next_edit','#_edit'])
async def user_edit_list(callback:CallbackQuery):
    
    if callback.data == "edit_user":
        user_page[callback.from_user.id] = 1
    elif callback.data == "next_edit":
        user_page[callback.from_user.id] += 1
    elif callback.data == "prew_edit":
        user_page[callback.from_user.id] -= 1
        
    page = user_page[callback.from_user.id]

    if callback.data in ["#_edit", "stop_next_edit", "stop_prew_edit"]:
        await callback.answer()
    else:    
        await callback.message.edit_text(text="Выбери пользователя для редактирования:",
                                        reply_markup=edit_status_user_keyboard("Admin", "edit", now=page))

#Выбор параметра редактирования именинника
@router.callback_query(Is_Admin(), StateFilter(default_state))
async def user_edit_menu(callback:CallbackQuery,state: FSMContext):
    await state.update_data(id_ = callback.data)
    await callback.message.edit_text(text="Выбери один из пунктов:",
                                     reply_markup=edit_user_keyboard())
    await state.set_state(FSMEditForm.process_edit)

#Выбор параметра редактирования именинника
@router.callback_query(Is_Admin(), StateFilter(FSMEditForm.process_edit))
async def user_edit_param_select(callback:CallbackQuery,state: FSMContext):
    await callback.message.answer(text="Введи новое значение:",
    reply_markup=footer_keyboard())
    await callback.message.delete()
    await callback.answer()
    await state.update_data(param = callback.data.split("_")[1])
    if callback.data.split("_")[1] == "name":
        await state.set_state(FSMEditForm.edit_name)
    elif callback.data.split("_")[1] == "surname":
        await state.set_state(FSMEditForm.edit_surname)
    elif callback.data.split("_")[1] == "date":
        await state.set_state(FSMEditForm.edit_date)
    elif callback.data.split("_")[1] == "statuswalley":
        await state.set_state(FSMEditForm.edit_statuswalley)
    elif callback.data.split("_")[1] == "cash":
        await state.set_state(FSMEditForm.edit_cash)

#Получение и перезапись нового значения имени именинника     
@router.message(Is_Admin(), StateFilter(FSMEditForm.edit_name), F.text.isalpha())
async def user_edit_name(message:Message, state: FSMContext):
    await state.update_data(value = message.text.capitalize())
    new_param_info = await state.get_data()
    await change_user(id_=new_param_info['id_'], param=new_param_info['param'],
                new_value=str(new_param_info['value']))
    await message.answer("✅Новое значение записано\!✅\nВыбери один из пунктов:", reply_markup=edit_user_keyboard())
    await state.clear()

#Получение и перезапись нового значения фамилии именинника     
@router.message(Is_Admin(), StateFilter(FSMEditForm.edit_surname), F.text.isalpha())
async def user_edit_surname(message:Message, state: FSMContext):
    await state.update_data(value = message.text.capitalize())
    new_param_info = await state.get_data()
    await change_user(id_=new_param_info['id_'], param=new_param_info['param'],
                new_value=str(new_param_info['value']))
    await message.answer("✅Новое значение записано\!✅\nВыбери одну из команд:", reply_markup=create_start_keyboard("Admin"))
    await state.clear()

#Добавление даты рождения нового пользователя  
@router.message(StateFilter(FSMFillForm.fill_surname), F.text.isalpha())
async def user_add_date(message: Message, state: FSMContext):
    await state.update_data(surname = message.text.capitalize())
    await message.answer(text="Введи дату рождения в формате ГГГГ\.ММ\.ДД:",reply_markup=footer_keyboard())
    await state.set_state(FSMFillForm.fill_date)
    
#Добавление фамилии нового пользователя   
@router.message(StateFilter(FSMFillForm.fill_name), F.text.isalpha())
async def user_add_surname(message: Message, state: FSMContext):
    await state.update_data(name = message.text.capitalize())
    await message.answer(text="Введи фимилию пользователя:",reply_markup=footer_keyboard())
    await state.set_state(FSMFillForm.fill_surname)

#Добавление id нового пользователя 
@router.message(StateFilter(FSMFillForm.fill_date), DateCheck())
async def user_add_id(message: Message, state: FSMContext):
    await state.update_data(date = message.text.replace('.', '-'))
    await message.answer(text="Пришли мне контакт пользователя:",reply_markup=footer_keyboard())
    await state.set_state(FSMFillForm.fill_id)

#Получение и перезапись нового значения даты именинника 
@router.message(StateFilter(FSMEditForm.edit_date), DateCheck())
async def user_edit_date(message: Message, state: FSMContext):
    await state.update_data(value = message.text.replace('.', '-'))
    new_param_info = await state.get_data()
    await change_user(id_=new_param_info['id_'], param=new_param_info['param'],
                new_value=str(new_param_info['value']))
    await message.answer("✅Новое значение записано\!✅\nВыбери один из пунктов:", reply_markup=edit_user_keyboard())
    await state.clear()
    
#Получение и перезапись нового значения статуса именинника 
@router.message(StateFilter(FSMEditForm.edit_statuswalley), lambda Message: Message.text in ('да', 'нет'))
async def user_edit_status(message: Message, state: FSMContext):
    if message.text.lower() == 'да':
        await state.update_data(value='True')
    else:
        await state.update_data(value='False') 
    new_param_info = await state.get_data()
    await change_user(id_=new_param_info['id_'], param=new_param_info['param'],
                new_value=str(new_param_info['value']))
    await message.answer("✅Новое значение записано\!✅\nВыбери один из пунктов:", reply_markup=edit_user_keyboard())
    await state.clear()
        
#Добавление правила сбора денег с нового пользователя 
@router.message(StateFilter(FSMFillForm.fill_id), IsContact())
async def user_add_satus_walley(message: Message, state: FSMContext):
    await state.update_data(id_=message.contact.user_id)
    await message.answer(text="Необходимо ли собирать деньги с пользователя \(да\/нет\)?",reply_markup=footer_keyboard())
    await state.set_state(FSMFillForm.fill_satus_walley)

#Добавление нового пользователя в БД
@router.message(StateFilter(FSMFillForm.fill_satus_walley), lambda Message: Message.text in ('да', 'нет'))
async def process_add_new_user(message: Message, state: FSMContext):
    if message.text.lower() == 'да':
        await state.update_data(status_walley='True')
    else:
        await state.update_data(status_walley='False')     
    await message.answer(text = "✅Пользователь добавлен\!✅")
    new_user_info = await state.get_data()
    await add_user(name=new_user_info['name'], surname=new_user_info['surname'],
                   date=new_user_info['date'], id_=new_user_info['id_'],
                   status_walley=new_user_info["status_walley"],
                   cash=250)
    await message.answer(
        text="Выбери одну из команд:",
        reply_markup=create_start_keyboard("Admin")
    )
    await message.delete()
    await state.clear()

#Получение и перезапись нового значения суммы сбора именинника 
@router.message(StateFilter(FSMEditForm.edit_cash), F.text.isdigit())
async def user_edit_cash(message: Message, state: FSMContext):
    await state.update_data(value = message.text)
    new_param_info = await state.get_data()
    await change_user(id_=new_param_info['id_'], param=new_param_info['param'],
                new_value=str(new_param_info['value']))
    await message.answer("✅Новое значение записано\!✅\nВыбери один из пунктов:", reply_markup=edit_user_keyboard())
    await state.clear()

#Ответ в случае неверных введенных данных  
@router.message(StateFilter(FSMFillForm.fill_name, FSMEditForm.edit_name, FSMEditForm.edit_surname, 
                            FSMFillForm.fill_surname, FSMFillForm.fill_date, FSMFillForm.fill_id,
                            FSMFillForm.fill_satus_walley, FSMEditForm.edit_date, FSMEditForm.edit_statuswalley,
                            FSMEditForm.edit_cash, FSMEditNotif.edit_bank, FSMEditNotif.edit_phone,FSMSearchUser.input_surname))
async def incorrect_input_data(message: Message):
    await message.answer(text="Ты ввел что\-то не то:")
