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
    print(list_of_tasks)

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
        sent = bot.send_message(message.chat.id, 'Напиши задачу')
        bot.register_next_step_handler(sent, message_to_save)
    elif get_message_bot == 'удалить задачу':
        sent = bot.send_message(message.chat.id, 'Какую задачу удалить (напиши ее номер)?')
        index = 1
        with open('list_of_current_tasks.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for line in reader:
                bot.send_message(message.chat.id, f'{str(index)}. {line[0]}')
                index += 1
        bot.register_next_step_handler(sent, message_to_delete)
    elif get_message_bot == 'задача выполнена':
        sent = bot.send_message(message.chat.id, 'Какая задача выполнена (напиши ее номер)?')
        index = 1
        with open('list_of_current_tasks.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for line in reader:
                bot.send_message(message.chat.id, f'{str(index)}. {line[0]}')
                index += 1
        bot.register_next_step_handler(sent, mark_accomplished)
    elif get_message_bot == 'список текущих задач':
        index = 1
        with open('list_of_current_tasks.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            for line in reader:
                bot.send_message(message.chat.id, f'{str(index)}. {line[0]}')
                index += 1
    elif get_message_bot == 'список завершенных задач':
        index = 1
        with open('list_of_accomplished_tasks.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            for line in reader:
                bot.send_message(message.chat.id, f'{str(index)}. {line[0]}')
                index += 1
    elif get_message_bot == 'выйти':
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, text='До свидания! Заходи еще!', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f'я не знаю такой команды')

def mark_accomplished(message):
    accomplished_task = message.text
    if accomplished_task.isdigit() and int(accomplished_task) <= len(list_of_tasks):
        deleted_task = list_of_tasks.pop(int(accomplished_task) - 1)
        with open ('list_of_current_tasks.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            for elem in list_of_tasks:
                writer.writerow(elem)
        with open('list_of_accomplished_tasks.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(deleted_task)
        bot.send_message(message.chat.id, f'Задача *{deleted_task[0]}* выполнена', parse_mode='Markdown')
    elif accomplished_task.isdigit() and int(accomplished_task) > len(list_of_tasks):
        bot.send_message(message.chat.id, f'Задачи с таким номером не существует')
    else:
        bot.send_message(message.chat.id, f'Я тебя не понимаю')

def message_to_delete(message):
    task_to_delete = message.text
    if task_to_delete.isdigit() and int(task_to_delete) <= len(list_of_tasks):
        deleted_task = list_of_tasks.pop(int(task_to_delete)-1)
        bot.send_message(message.chat.id, f'Задача *{deleted_task}* удалена', parse_mode='Markdown')
        with open('list_of_current_tasks.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            for elem in list_of_tasks:
                writer.writerow(elem)
    elif task_to_delete.isdigit() and int(task_to_delete) > len(list_of_tasks):
        bot.send_message(message.chat.id, f'Задачи с таким номером не существует')
    else:
        bot.send_message(message.chat.id, f'Я тебя не понимаю')

def message_to_save(message):
    message_to_save = [message.text]
    with open ('list_of_current_tasks.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(message_to_save)
        bot.send_message(message.chat.id, f'Задача *{message_to_save[0]}* создана', parse_mode='Markdown')
    list_of_tasks.append(message_to_save)



bot.polling(none_stop=True)
