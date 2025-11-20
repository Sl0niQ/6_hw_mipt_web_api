# env: webapienv

# Задача:
# 	- создать интерфейс для взаимодействия с данными собранными скраппером. 
# Варианты: 
#	- API для получения данных;
#	- бот для получения данных.
# Выбор: телеграм-бот

import requests
import threading
from time import sleep
import pandas as pd
from pandasql import sqldf
from requests.adapters import HTTPAdapter
from config import POOL_CONNECTIONS, POOL_MAXSIZE, MAX_RETRIES, POOL_BLOCK, POLL_INTERVAL, PAUSE, TIME_OUT, LIMIT, FILE_PATH


class ISSData:
	"""Обработка данных о положении МКС"""
	#---------ok
	def __init__(self, sql_components, file_path=FILE_PATH):
		"""Конструктор"""
		self.file_path = file_path 				# путь к источнику данных
		self.sql_components = sql_components 	# словарь со структурой sql-запроса
		self.sql_query = None 					# динамический sql-запрос

	#---------ok
	def query_builder(self):
		if self.sql_components['agregation']:
			self.sql_query = f"""
				SELECT 					
					{self.sql_components['agregation']}({self.sql_components['field']}) as {self.sql_components['agregation']}_{self.sql_components['field']}
				FROM df;

			"""
		elif self.sql_components['field']:
			self.sql_query = f"""
				SELECT *					
				FROM df
				WHERE {self.sql_components['field']} {self.sql_components['operator']} {self.sql_components['value']}
				LIMIT 5;
			"""
		else:
			self.sql_query = f"""
				SELECT *					
				FROM df
				ORDER BY date DESC
				LIMIT 5;
			"""
		return self.sql_query

	def query_executor(self):
		df = pd.read_csv(self.file_path, sep=';') ###
		df['speed'] = df['speed'].str[:-5].astype(float)
		df['alt'] = df['alt'].str[:-3].astype(float)
		df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')	

		# Обработка через SQL
		result_df = sqldf(self.query_builder())
		return result_df.to_string(index=False)
		

class TelegramBot:
	#---------ok
	def __init__(self, token):
		"""Конструктор"""		
		self.token = token 					# токен для соединения с телеграм-ботом
		self.exit_flag = False 				# флаг завершения работы скрипта		
		self.req_pause = PAUSE 				# интервал опроса API телеграм-бота
		self.last_message_id = -1			# id последней обработанной команды
		self.fields_list = ('alt', 'speed')
		self.operators_list = ('/start', 'latest', 'max', 'min', '>', '<', '=')	

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

	#---------ok
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

	#---------ok
	def sql_components_builder(self, user_message, field, field_name_length):
		"""
			Сбор компонентов для sql-запроса			
		"""
		sql_components = {
			'field': None,
			'operator': None,
			'agregation': None,
			'value': None,
			'error_message': None
		}		
		try:
			if user_message[field_name_length] in (self.operators_list[4:]): # допустимые операторы <, >, =
				sql_components['field'] = field		
				sql_components['value'] = float(user_message[field_name_length+1:])
				sql_components['operator'] = user_message[field_name_length]				
			elif user_message[field_name_length:field_name_length+3] in (self.operators_list[2:4]): # доступные агрегации
				sql_components['field'] = field
				sql_components['agregation'] = user_message[field_name_length:field_name_length+3]
			else:
				sql_components['error_message'] = "Недопустимый оператор / недопустимая агрегация"
			return sql_components
		except ValueError:
			# в фильтре числового поля не число
			sql_components['error_message'] = "Ошибка: значение должно быть числом"
			return sql_components			
		except IndexError:
			# короткая команда, не хватает параметров
			sql_components['error_message'] = "Ошибка: некорректная команда"
			return sql_components			
		except Exception as e:
		    # Любая другая ошибка
		    sql_components['error_message'] = f"Произошла ошибка: {e}"
		    return sql_components
	
	#---------ok
	def messages_processing(self, updates):
		"""
		обработка списка запросов от пользователей телеграм-бота:
		- цикл по всем элементам списка, обработка каждого элемента
		"""	
		for update in updates:			
			if self.last_message_id < update['update_id']:
				self.last_message_id = update['update_id']
		
			user_message = update['message']['text'].replace(" ", "")  	# команда пользователя без пробелов
			if user_message == self.operators_list[0]: 					# команда /start
				data = (
					"Что показать?\n\n"
					"• latest - 5 последних записей\n"
					"• alt max - максимальная высота\n"
					"• speed<40000 - фильтр по скорости\n"
				)
			elif user_message == self.operators_list[1]: 				# команда latest
				sql_components = {
					'field': None,
					'operator': 'Latest',
					'agregation': None,
					'value': None,
					'error_message': None
				}				
				sql_query_result = ISSData(sql_components=sql_components)
				data = sql_query_result.query_executor()

			elif user_message.startswith(self.fields_list): 			# фильтры/агрегации по полям alt, speed
				for field in self.fields_list:							# поиск команды в списке
					field_name_length = len(field)
					if user_message[:field_name_length] == field:						
						sql_components = self.sql_components_builder(user_message, field, field_name_length)
						sql_query_result = ISSData(sql_components=sql_components)
						data = sql_query_result.query_executor() 
						break
			else:
				data = "Неизвестная команда"
			
			self.send_result(update['message']['chat']['id'], data)			
					
	#---------ok
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
				print("Ожидание нового сообщения")								
				updates = self.get_updates(params)				
				if updates:
					print("Обработка...")				
					self.messages_processing(updates)				
		except Exception as e:
			print(f"Ошибка: {e}")
		finally:
			self.session.close()
			print("Сессия закрыта")

token = '********' 
test = TelegramBot(token)
test.run()