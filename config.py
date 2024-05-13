MAX_USERS = 3 
MAX_GPT_TOKENS = 120 
COUNT_LAST_MSG = 4 


MAX_USER_STT_BLOCKS = 10
MAX_USER_TTS_SYMBOLS = 5_000 
MAX_USER_GPT_TOKENS = 2_000

GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
GPT_MODEL = "yandexgpt-lite"
SYSTEM_PROMPT = [{"role": "system", "text": "Ты веселый собеседник. Общайся с пользователем на \"ты\"."
                                            "Не объясняй пользователю, что ты умеешь и можешь. Чётко и понятно "
                                            "отвечай на вопросы пользователя. Не используй диалоги, если этого не "
                                            "требуется."
                                            "Изображай человека"}]

ADMIN_ID: int = 1234 


URL_TTS = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
URL_STT = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?"
LANGUAGE = "ru-RU"
SPEECHKIT_MODEL = "general" 
VOICE = "filipp"


HOME_DIR = '/home/student/stablebot'  
LOGS = f'{HOME_DIR}/logs.log' 
DB_FILE = f'{HOME_DIR}/messages.db' 

IAM_TOKEN_PATH = f'{HOME_DIR}/creds/iam_token.txt' 
FOLDER_ID_PATH = f'{HOME_DIR}/creds/folder_id.txt' 
BOT_TOKEN_PATH = f'{HOME_DIR}/creds/bot_token.txt' 


