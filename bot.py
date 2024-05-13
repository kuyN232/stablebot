import telebot
import logging
from telebot.types import BotCommand, BotCommandScope
from validators import check_number_of_users, is_gpt_token_limit, is_stt_block_limit, is_tts_symbol_limit
from yandex_gpt import ask_gpt
from config import COUNT_LAST_MSG, ADMIN_ID, LOGS
from database import create_database, add_message, select_n_last_messages
from speechkit import text_to_speech, speech_to_text
from creds import get_bot_token 

bot = telebot.TeleBot(get_bot_token()) 


start_message = ("Привет! Я бот-нейросетью. Ты можешь задавать вопросы, просить помощи, общаться со мной голосом или "
                 "просто сообщениями. Если нужна помощь, то напиши /help")

help_message = ("Тебе нужна помощь? Вот мои команды:\n"
                "/start - перезапуск бота;\n"
                "/help - информация о командах и помощь;\n")


@bot.message_handler(commands=["debug"])
def send_logs(message):
    user_id = message.chat.id
    if user_id == ADMIN_ID:
        try:
            with open(LOGS, "rb") as f:
                bot.send_document(message.chat.id, f)
                logging.info("логи отправлены")
        except telebot.apihelper.ApiTelegramException:
            bot.send_message(message.chat.id, "Логов пока нет.")
    else:
        bot.send_message(message.chat.id, "У Вас недостаточно прав для использования этой команды.")
        logging.info(f"{user_id} пытался получить доступ к логам, не являясь админом")


def register_comands(message):
    commands = [ 
        BotCommand("start", "запуск бота"),
        BotCommand("help", "основная информация о боте")]
    bot.set_my_commands(commands)
    BotCommandScope('private', chat_id=message.chat.id)

@bot.message_handler(commands=["start"])
def send_welcome(message):
    logging.info("Отправка приветственного сообщения")
    bot.reply_to(message, start_message)
    register_comands(message)



@bot.message_handler(commands=["help"])
def about_bot(message):
    bot.send_message(message.chat.id, help_message, parse_mode="markdown")



@bot.message_handler(content_types=["text"])
def handle_text(message):
    try:
        user_id = message.from_user.id

        status_check_users, error_message = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message) 
            return

        full_user_message = [message.text, 'user', 0, 0, 0]
        add_message(user_id=user_id, full_message=full_user_message)

        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)
        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
        if error_message:
            bot.send_message(user_id, error_message)
            return

        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        if not status_gpt:
            bot.send_message(user_id, answer_gpt)
            return
        total_gpt_tokens += tokens_in_answer

        full_gpt_message = [answer_gpt, 'assistant', total_gpt_tokens, 0, 0]
        add_message(user_id=user_id, full_message=full_gpt_message)

        bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)
    except Exception as e:
        logging.error(e)
        bot.send_message(message.from_user.id, "Не получилось ответить. Попробуй написать другое сообщение")


@bot.message_handler(content_types=['voice'])
def handle_voice(message: telebot.types.Message):
    try:
        user_id = message.from_user.id

        status_check_users, error_message = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message)
            return

        stt_blocks, error_message = is_stt_block_limit(user_id, message.voice.duration)
        if error_message:
            bot.send_message(user_id, error_message)
            return

        file_id = message.voice.file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)
        status_stt, stt_text = speech_to_text(file)
        if not status_stt:
            bot.send_message(user_id, stt_text)
            return


        add_message(user_id=user_id, full_message=[stt_text, 'user', 0, 0, stt_blocks])


        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)
        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
        if error_message:
            bot.send_message(user_id, error_message)
            return

        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        if not status_gpt:
            bot.send_message(user_id, answer_gpt)
            return
        total_gpt_tokens += tokens_in_answer

        tts_symbols, error_message = is_tts_symbol_limit(user_id, answer_gpt)

        add_message(user_id=user_id, full_message=[answer_gpt, 'assistant', total_gpt_tokens, tts_symbols, 0])

        if error_message:
            bot.send_message(user_id, error_message)
            return

        status_tts, voice_response = text_to_speech(answer_gpt)
        if status_tts:
            bot.send_voice(user_id, voice_response, reply_to_message_id=message.id)
        else:
            bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)

    except Exception as e:
        logging.error(e)
        user_id = message.from_user.id
        bot.send_message(user_id, "Не получилось ответить. Попробуй записать другое сообщение")


@bot.message_handler(func=lambda: True)
def handler(message):
    bot.send_message(message.from_user.id, "Отправь мне голосовое или текстовое сообщение, и я тебе отвечу")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H",
        filename=LOGS,
        filemode="w",
        encoding='utf-8',
        force=True)
    create_database()  
    bot.infinity_polling() 
    logging.info("Бот запущен")
