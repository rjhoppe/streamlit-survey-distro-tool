import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import asyncio
import os
import uuid
import time
import sqlite3
import yaml
from yaml.loader import SafeLoader
from dotenv import load_dotenv
from twilio.rest import Client
from classes import Database

st.set_page_config(
	page_title="Demo",
	page_icon='🧪',
	layout='wide',
	initial_sidebar_state='expanded'
)

load_dotenv()
account_sid = os.getenv('TWLO_SID')
auth_token = os.getenv('TWLO_TOKEN')
twlo_number = os.getenv('TWLO_NUMBER')
client = Client(account_sid, auth_token)

def validate_phone_number(recipient):
	if len(recipient) != 11:
		st.warning('❌ Invalid phone number. Did you remember to include the country code?')
		return False
	else:
		st.write('✅ Phone number validated.')
		return True

def validate_email():
	return

def sms_distro(message, recipient, SQLite):
	try:
		text = client.messages \
								.create(
										body=message,
										from_=twlo_number,
										to=str(recipient)
								)
		st.write(text.sid)
		log = {
			'uuid': str(uuid.uuid4()),
			'message_sid': text.sid,
			'phone_number': recipient,
			'user': 'Demo User',
			'status': 'success',
			'error_msg': 'N/A'
		}
		msg_df = pd.DataFrame(log, index=[0])
		st.write('Distribution complete!')
		st.balloons()
	except Exception as e:
		st.warning(f'❌ Something went wrong: {e}')
		log = {
			'uuid': str(uuid.uuid4()),
			'message_sid': 'N/A',
			'phone_number': recipient,
			'user': 'Demo User',
			'status': 'failed',
			'error_msg': e
		}
		msg_df = pd.DataFrame(log, index=[0])
	finally:
		SQLite.check_db()
		SQLite.loadData(msg_df)
		print('DB conn successful')
		return

def email_distro():
	return

async def main():
	SQLite = Database(db_name='app-db', url='database/app.db')
	st.header('Try it out!', divider="rainbow")
	method = st.radio(
		'Select your distribution method:',
		["SMS", "Email", "Both"]
	)
	if method == 'SMS':
		recipient = st.text_input('Enter a recipient phone number, including country code. **EX: 12816792312**')
	elif method == 'Email':
		recipient = st.text_input('Enter a recipient email')
	elif method == 'Both':
		recipient = st.text_input('Enter a recipient phone number, including country code. **EX: 12816792312**')
		recipient_email = st.text_input('Enter a recipient email')

	message = st.text_area('Enter your message:', max_chars=160)

	if message != '' and recipient != '':
		if method == "SMS":
			phone_num_val = validate_phone_number(recipient)
			if phone_num_val is True:
				st.button(label='Distribute 🚀', on_click=sms_distro, args=(message, recipient, SQLite))
		elif method == "Email":
			st.button(label='Distribute 🚀', on_click=email_distro, args=(message, recipient, SQLite))
		elif method == "Both":
			st.button(label='Distribute 🚀')

asyncio.run(main())