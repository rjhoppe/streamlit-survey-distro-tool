import sqlite3

class Database:
	def __init__(self, db_name, url):
		self.name = db_name
		self.url = url

	def check_db(self):
	# Need to change conn element to st.connection for prod and define db conn in secrets
		try:
			with sqlite3.connect(self.url) as conn:
				cur = conn.cursor()
				cur.execute('''
										CREATE TABLE IF NOT EXISTS messages(
										created datetime default current_timestamp,
										uuid text,
										message_sid text,
										phone_number integer,
										user text,
										status text,
										error_msg text
										)''')
				print('DB configured')
		except sqlite3.OperationalError as e:
			print(f'SQLite Error: {e}')
		finally:
			cur.close()
			conn.commit()
			conn.close()

	# Need to serialize database connections to avoid data corruption
	def loadData(self, msg_df):
		try:
			with sqlite3.connect(self.url, isolation_level=None, check_same_thread=False) as conn:
				cur = conn.cursor()
				msg_df.to_sql('messages', conn, if_exists='append', index=False)
				rows = cur.execute("SELECT * FROM messages").fetchall()
				print(rows)
		except sqlite3.Error as e:
			print('Something went wrong', e)
		finally:
			cur.close()
			conn.commit()
			conn.close()