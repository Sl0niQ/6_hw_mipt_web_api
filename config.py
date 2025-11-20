# TELEGRAM_BOT_NAME 		= '6_hw_api_mipt'
# TELEGRAM_BOT_USER_NAME 	= 'hw_api_mipt_bot'

POLL_INTERVAL = 30 		# время ожидания новой команды/команд в текущем запросе
PAUSE = 15				# интервал между запросами к боту	
TIME_OUT = 35			# максимальное время ожидания ответа от бота
LIMIT = 100 			# предельное количество сообщений в одном запросе

# Параметры адаптера
POOL_CONNECTIONS = 1 	# количество хостов в пуле
POOL_MAXSIZE = 1 		# количество параллельных соединений на хост  
MAX_RETRIES = 0   		# количество повторных попыток соединения
POOL_BLOCK = False

FILE_PATH = 'iss_data.csv' # путь к источнику данных