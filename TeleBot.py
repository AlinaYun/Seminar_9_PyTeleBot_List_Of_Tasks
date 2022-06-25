import telebot
from telebot import types # чтоб создать кнопки
import csv


with open('token.txt', 'r') as f:
    Token = f.read()

bot = telebot.TeleBot(Token)

with open('list_of_current_tasks.csv', 'r', encoding='utf-8') as file:
    list_of_tasks = []
    reader = csv.reader(file)
    for line in reader:
        list_of_tasks.append(line)

def read_from_file(file, msg):
    index = 1
    with open(file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for line in reader:
            bot.send_message(msg.chat.id, f'{str(index)}. {line[0]}')
            index += 1

def write_to_file(file):
    with open(file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        for elem in list_of_tasks:
            writer.writerow(elem)

def append_to_file(file, msg):
    with open (file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(msg)

@bot.message_handler(commands=['start'])
def menu(message):
    mess = f'Привет, {message.from_user.first_name}! Какое действие ты хочешь выполнить?'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)   #row_width сколько кнопок в ряду, resize - чтоб корректно отображалось на компе и телефоне
    btn1 = types.KeyboardButton('Добавить задачу')
    btn2 = types.KeyboardButton('Удалить задачу')
    btn3 = types.KeyboardButton('Задача выполнена')
    btn4 = types.KeyboardButton('Список текущих задач')
    btn5 = types.KeyboardButton('Список завершенных задач')
    btn6 = types.KeyboardButton('Выйти')
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    bot.send_message(message.chat.id, mess, reply_markup=markup)

@bot.message_handler(content_types=['text'])
def msg_from_user(message):
    get_message_bot = message.text.strip().lower()
    global list_of_tasks
    if get_message_bot == 'добавить задачу':
        sent = bot.send_message(message.chat.id, f'*Напиши задачу*', parse_mode='Markdown')
        bot.register_next_step_handler(sent, message_to_save)
    elif get_message_bot == 'удалить задачу':
        sent = bot.send_message(message.chat.id, f'*Какую задачу удалить (напиши ее номер)?*', parse_mode='Markdown')
        read_from_file('list_of_current_tasks.csv', message)
        bot.register_next_step_handler(sent, message_to_delete)
    elif get_message_bot == 'задача выполнена':
        sent = bot.send_message(message.chat.id, f'*Какая задача выполнена (напиши ее номер)?*', parse_mode='Markdown')
        read_from_file('list_of_current_tasks.csv', message)
        bot.register_next_step_handler(sent, mark_accomplished)
    elif get_message_bot == 'список текущих задач':
        read_from_file('list_of_current_tasks.csv', message)
    elif get_message_bot == 'список завершенных задач':
        read_from_file('list_of_accomplished_tasks.csv', message)
    elif get_message_bot == 'выйти':
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, text='До свидания! Заходи еще!', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f'я не знаю такой команды')

def mark_accomplished(message):
    accomplished_task = message.text
    if accomplished_task.isdigit() and int(accomplished_task) <= len(list_of_tasks):
        deleted_task = list_of_tasks.pop(int(accomplished_task) - 1)
        write_to_file('list_of_current_tasks.csv')
        append_to_file('list_of_accomplished_tasks.csv', deleted_task)
        bot.send_message(message.chat.id, f'Задача *{deleted_task[0]}* выполнена', parse_mode='Markdown')
    elif accomplished_task.isdigit() and int(accomplished_task) > len(list_of_tasks):
        bot.send_message(message.chat.id, f'Задачи с таким номером не существует')
    else:
        bot.send_message(message.chat.id, f'Я тебя не понимаю')

def message_to_delete(message):
    task_to_delete = message.text
    if task_to_delete.isdigit() and int(task_to_delete) <= len(list_of_tasks):
        deleted_task = list_of_tasks.pop(int(task_to_delete)-1)
        bot.send_message(message.chat.id, f'Задача *{deleted_task[0]}* удалена', parse_mode='Markdown')
        write_to_file('list_of_current_tasks.csv')
    elif task_to_delete.isdigit() and int(task_to_delete) > len(list_of_tasks):
        bot.send_message(message.chat.id, f'Задачи с таким номером не существует')
    else:
        bot.send_message(message.chat.id, f'Я тебя не понимаю')

def message_to_save(message):
    message_to_save = [message.text]
    append_to_file('list_of_current_tasks.csv', message_to_save)
    bot.send_message(message.chat.id, f'Задача *{message_to_save[0]}* создана', parse_mode='Markdown')
    list_of_tasks.append(message_to_save)



bot.polling(none_stop=True)
