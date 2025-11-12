# env: webapienv

# Задача:
# 	- создать интерфейс для взаимодействия с данными собранными скраппером. 
# Варианты: 
#	- API для получения данных;
#	- бот для получения данных.

import requests
import threading
from time import sleep
from requests.adapters import HTTPAdapter
from config import TELEGRAM_TOKEN, POOL_CONNECTIONS, POOL_MAXSIZE, MAX_RETRIES, POOL_BLOCK

############################ Test code ->
"""

"""
############################ Test code <-

class TelegramBot:
	def __init__(self, token, poll_interval=45):
		"""Конструктор"""		
		self.token = token 					# токен для соединения с телеграм-ботом
		self.exit_flag = False 				# флаг завершения работы скрипта		
		self.poll_interval = poll_interval 	# интервал опроса API телеграм-бота
		self.last_message_id = 0 			# id последней обработанной команды

	def wait_for_exit(self): #-->ok
		"""Обработка команды остановки приложения"""
		while not self.exit_flag:
			if input().strip().lower() == 'exit':
				self.exit_flag = True
				print("Завершение обработки текущих запросов...")
				break

	def pause(self): #-->ok
		"""Пауза между запросами к API"""
		for _ in range(self.poll_interval):
			if self.exit_flag:
				break
			sleep(1)
	"""
	def find_last_message_id(self, session, url):
		#latest_message = max(updates, key=lambda x: x['message']['message_id'])
		return None
	"""

	def single_message_processing():
		"""
		обработка одной команды:
		- извлечение команды и id;
		- сохранение id в self.last_message_id если значение больше;
		- анализ команды и выполнение соответствующего действия
		"""
		pass

	def messages_processing():
		"""
		обработка пакета:
		- цикл по елементам пакета
		- обработка отдельных элементов
		"""
		pass

	def run(self):
		"""Главный цикл сбора данных"""
		try:            
            # Запуск фонового потока
			exit_thread = threading.Thread(target=self.wait_for_exit, daemon=True)
			exit_thread.start()

			session = requests.session() 
			adapter = HTTPAdapter(
				pool_connections = POOL_CONNECTIONS,
				pool_maxsize = POOL_MAXSIZE,
				max_retries = MAX_RETRIES,
				pool_block = POOL_BLOCK
			)
			session.mount("https://", adapter)
			url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
			# параметры для запроса к боту
			params = {
				'timeout': 30, # время ожидания новой команды (лонг пуллинг)
				'limit': 100   # ограничение количества сообщений в одном ответе
			}
			# Получение сообщений
			while not self.exit_flag:				
				if self.last_message_id:
					params['offset'] = self.last_message_id + 1 # для чтения только необработанных команд
				response = session.request("get", url, params=params, timeout=35)
				print("get")
				updates = response.json()['result']
				#print(updates[1].get("message").get("message_id"))
				print(updates)
				self.pause()
		except Exception as e:
			print(f"Ошибка: {e}")
		finally:
			session.close()
			print("Сессия закрыта")

test = TelegramBot(token=TELEGRAM_TOKEN, poll_interval=20)
test.run()