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
from config import POOL_CONNECTIONS, POOL_MAXSIZE, MAX_RETRIES, POOL_BLOCK, POLL_INTERVAL, PAUSE, TIME_OUT, LIMIT

############################ Test code ->
"""

"""
############################ Test code <-

class TelegramBot:
	#---------в разработке
	def __init__(self, token):
		"""Конструктор"""		
		self.token = token 					# токен для соединения с телеграм-ботом
		self.exit_flag = False 				# флаг завершения работы скрипта		
		self.req_pause = PAUSE 				# интервал опроса API телеграм-бота
		self.last_message_id = -1			# id последней обработанной команды

		self.session = requests.session() 
		adapter = HTTPAdapter(
			pool_connections = POOL_CONNECTIONS,
			pool_maxsize = POOL_MAXSIZE,
			max_retries = MAX_RETRIES,
			pool_block = POOL_BLOCK
		)
		self.session.mount("https://", adapter)

	#---------ok
	def wait_for_exit(self):
		""" Обработка команды остановки приложения """
		while not self.exit_flag:
			if input().strip().lower() == 'exit':
				self.exit_flag = True
				print("Завершение обработки текущих запросов...")
				break

	#---------ok ?нужно?
	def pause(self): 
		""" Пауза между запросами к API """
		for _ in range(self.req_pause):
			if self.exit_flag:
				break
			sleep(1)

	#---------в разработке
	def send_result(self, chat_id, data):
		try:
			self.session.request(
				"POST", 
				f"https://api.telegram.org/bot{self.token}/sendMessage", 
				json={'chat_id': chat_id, 'text': data}, 
				timeout=TIME_OUT
			)			
		except requests.exceptions.RequestException as e:
			print(f"Не удалось отправить сообщение: {e}")

	#---------ok
	def get_updates(self, params):
		"""	Чтение новых сообщений """
		if self.last_message_id > -1:
			params['offset'] = self.last_message_id + 1 # для чтения только необработанных команд
		response = self.session.request(
			"GET", 
			f"https://api.telegram.org/bot{self.token}/getUpdates", 
			params=params, 
			timeout=TIME_OUT
		)				
		return response.json()['result']

	#---------в разработке
	def messages_processing(self, updates):
		"""
		обработка пакета:
		- цикл по элементам пакета
		- обработка отдельных элементов
		"""	
		for update in updates:
			print(f"update_id: {update['update_id']} text: {update['message']['text']}") ###
			if self.last_message_id < update['update_id']:
				self.last_message_id = update['update_id']
			print(self.last_message_id)
			print(update['message']['chat']['id'])
			print(update['message']['chat']['first_name'])
			print(update['message']['chat']['username'])
			data = f"Привет, {update['message']['chat']['first_name']}! Знаешь ли ты, что твой ник в телеге {update['message']['chat']['username']}?"
			self.send_result(update['message']['chat']['id'], data)
			#sendMessage(update['message']['chat']['id'], f"Привет, {update['message']['chat']['first_name']}! Ты знаешь, что твой ник в телеге {update['message']['chat']['username']}")
					
	#---------в разработке
	def run(self):
		"""Главный цикл сбора данных"""
		try:            
            # Запуск фонового потока
			exit_thread = threading.Thread(target=self.wait_for_exit, daemon=True)
			exit_thread.start()
						
			url_post = f"https://api.telegram.org/bot{self.token}/sendMessage"					
			# параметры для запроса к боту
			params = {
				'timeout': POLL_INTERVAL, 	# время ожидания новой команды (лонг пуллинг)
				'limit': LIMIT 				# ограничение количества сообщений в одном ответе
			}

			# Получение сообщений
			while not self.exit_flag:
				print("start")				
				#print(self.last_message_id)				
				updates = self.get_updates(params)
				#print(f"updates={updates}")
				if updates:
					print("новое сообщение")
					self.messages_processing(updates)





				#self.pause()
				print("end")
		except Exception as e:
			print(f"Ошибка: {e}")
		finally:
			self.session.close()
			print("Сессия закрыта")

token = '' 
test = TelegramBot(token)
test.run()