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
from config import TELEGRAM_TOKEN

########################## Test code ->
session = requests.session() 	# 17:19 разовое подключение к серверу и дальнейшее удержание соединения
adapter = HTTPAdapter()			# 18:30 драйвер для https-соединения

session.mount("https://", adapter) # 19:17 добавление адаптера в сессию

retry_num = 0
with session as session:
	url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates" # 22:00
	while retry_num < 1:
		# 29:03
		# print(url)
		response = session.request("post", url)
		# print(response)
		updates = response.json()['result']
		print(updates)
		sleep(10)
		retry_num += 1
		# 50:34
############################ Test code <-

class TelegramBot:
	def __init__(self, token, poll_interval=45):
		"""Конструктор"""		
		self.token = token 					# токен для соединения с телеграм-ботом
		self.last_message_id = None 		# id последнего сообщения в чате
		self.exit_flag = False 				# флаг завершения работы скрипта		
		self.poll_interval = poll_interval 	# интервал опроса API телеграм-бота

	def wait_for_exit(self): #-->ok
		"""Обработка команды остановки приложения"""
		while not self.exit_flag:
			if input().strip().lower() == 'exit':
				self.exit_flag = True

	def pause(self): #-->ok
		"""Пауза между запросами к API"""
		for _ in range(self.poll_interval):
			if self.exit_flag:
				break
			sleep(1)

	def run(self):
		"""Главный цикл сбора данных"""
		try:            
            # Запуск фонового потока
			exit_thread = threading.Thread(target=self.wait_for_exit, daemon=True)
			exit_thread.start()
"""
Остановился здесь. Этап: определить id последнего сообщения в случае первого запуска,
Прочитать новое сообщение
			# Чтение последнего сообщения
			while not self.exit_flag:
				print("next step")
				self.pause()
"""				
		except Exception as e:
			print(f"Ошибка: {e}")
		finally:
			pass
			#self.cleanup()

test = TelegramBot(token=TELEGRAM_TOKEN, poll_interval=2)
test.run()

