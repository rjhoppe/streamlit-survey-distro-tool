import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import os
import asyncio
import sqlite3
# import sqlalchemy
import uuid
import time
import yaml
from yaml.loader import SafeLoader
from dotenv import load_dotenv
# from spellchecker import SpellChecker
# from autocorrect import Speller
# from textblob import TextBlob
from twilio.rest import Client

num_of_rows = 0
request_num = 0
side_bar_state = 'collapsed'

st.set_page_config(
    page_title="HotLinks",
    page_icon="🥵",
    initial_sidebar_state=side_bar_state
)

load_dotenv()
account_sid = os.getenv('TWLO_SID')
auth_token = os.getenv('TWLO_TOKEN')
twlo_number = os.getenv('TWLO_NUMBER')
client = Client(account_sid, auth_token)

class Database:
  def __init__(self, db_name, url, conn, cur):
    self.name = db_name
    self.url = url
    self.conn = conn
    self.cur = cur

def check_db():
# Need to change conn element to st.connection for prod and define db conn in secrets
  try:
    with sqlite3.connect('database/app.db') as conn:
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
def loadData(msg_df):
  try:
    with sqlite3.connect('database/app.db', isolation_level=None, check_same_thread=False) as conn:
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

  # Make async
  # def connect(self):
  #   try:
  #     with sqlite3.connect('database/app.db', isolation_level=None) as conn:
  #       cur = conn.cursor()
  #       cur.execute("SELECT * FROM messages").fetchall()
  #       print('Connection successful')
  #   except sqlite3.Error as e:
  #     if str(e) == 'no such table: test':
  #       print('Table does not exist')
  #       with sqlite3.connect('database/app.db') as conn:
  #         cur.close()
  #         cur = conn.cursor()
  #         cur.execute('''
  #                     CREATE TABLE messages(
  #                     created datetime default current_timestamp,
  #                     uuid text,
  #                     message_sid text,
  #                     phone_number integer,
  #                     user text,
  #                     status text,
  #                     error_msg text
  #                     )''')
  #       print('Table created')
  #   finally:
  #     cur.close()
  #     conn.commit()
  #     conn.close()

  # # Remove files older than 30 days from database - not tested
  # # Make async
  # def rm_data():
  #   query = "DELETE FROM messages WHERE created <= strftime('%s', datetime('now', '-30 day'));"
  #   try:
  #     with sqlite3.connect('database/app.db', isolation_level=None) as conn:
  #       cur = conn.cursor()
  #       cur.execute(query)
  #   except Exception as e:
  #     print('Encountered error deleting records', e)
  #   finally:
  #     cur.close()
  #     conn.commit()
  #     conn.close()
  
  # def insert_data(msg_df):
  #   try:
  #     with sqlite3.connect('database/app.db', isolation_level=None, check_same_thread=False) as conn:
  #       cur = conn.cursor()
  #       msg_df.to_sql('messages', conn, if_exists='append', index=False)
  #       rows = cur.execute("SELECT * FROM messages").fetchall()
  #       print(rows)
  #   except sqlite3.Error as e:
  #     print('Something went wrong', e)
  #   finally:
  #     conn.commit()
  #     conn.close()

# Need to serialize database connections to avoid data corruption
# def check_db():
#   # Need to change conn element to st.connection for prod and define db conn in secrets
#     try:
#       with sqlite3.connect('database/app.db') as conn:
#         cur = conn.cursor()
#         cur.execute('''
#                     CREATE TABLE IF NOT EXISTS messages(
#                     created datetime default current_timestamp,
#                     uuid text,
#                     message_sid text,
#                     phone_number integer,
#                     user text,
#                     status text,
#                     error_msg text
#                     )''')
#         print('DB configured')
#     except sqlite3.OperationalError as e:
#       print(f'SQLite Error: {e}')
#     finally:
#       cur.close()
#       conn.commit()
#       conn.close()

# # Need to serialize database connections to avoid data corruption
# def loadData(msg_df):
#   try:
#     with sqlite3.connect('database/app.db', isolation_level=None, check_same_thread=False) as conn:
#       cur = conn.cursor()
#       msg_df.to_sql('messages', conn, if_exists='append', index=False)
#       rows = cur.execute("SELECT * FROM messages").fetchall()
#       print(rows)
#   except sqlite3.Error as e:
#     print('Something went wrong', e)
#   finally:
#     cur.close()
#     conn.commit()
#     conn.close()

def calc_number_rows(df):
  num_of_rows = len(df)
  if num_of_rows > 200:
    st.warning("❌ Distribution list exceeds 100 respondents. Please reduce the list or reach out to admin.")
  else:
    return num_of_rows

@st.cache_data
def load_example_csv():
  df2 = pd.read_csv('example.csv')
  df2['phone_numbers'] = df2['phone_numbers'].astype(str)
  df2['phone_numbers'] = df2["phone_numbers"].str.replace(",", "")
  return df2

async def check_file(df, column_validation):
  try:
    async with asyncio.timeout(5):
      # Test timeout
      # time.sleep(10)
      if df.columns.tolist() != ['client_name','url','message','phone_numbers']:
        st.warning('❌ Column headers incorrect. Check spelling and order.')
      elif len(df['client_name']) > 1:
        st.warning('❌ Client column only requires one value. See example file.')
      elif len(df['url']) > 1:
        st.warning('❌ URL column only requires one value. See example file.')
      elif len(df['message']) > 1:
        st.warning('❌ Message column only requires one value. See example file.')
      else:
        st.write('✅ Column headers formatted correctly.')
        column_validation = True
        await asyncio.sleep(1)
        return column_validation
  except asyncio.TimeoutError:
    st.warning('❌ Application timeout, try again later.')
  except Exception as e:
    st.warning(f'❌ Something went wrong: {e}')

async def parse_msg_data(df, content_validation):
  try:
    async with asyncio.timeout(5):
      message = df[['message']].values[0][0]
      if len(message) > 320:
        st.warning('❌ Content exceeds SMS limit of 320 characters. Please revise.')
        st.write(f'Current character count: {len(message)}')
      else:
        st.write('✅ Message content under 320 characters.')
        content_validation = True
        await asyncio.sleep(1)
        return content_validation
  except asyncio.TimeoutError:
    st.warning('❌ Application timeout, try again later.')
  except Exception as e:
    st.warning(f'❌ Something went wrong: {e}')
    
async def parse_valid_numbers(df, phone_num_validation):
  try:
    async with asyncio.timeout(5):
      for i, v in enumerate(df['phone_numbers']):
        v = len(str(v))
        if v != 11:
          st.warning(f'❌ Invalid phone number at row: {i}')
        else:
          st.write('✅ Phone numbers validated.')
          phone_num_validation = True
      await asyncio.sleep(1)
      return phone_num_validation
  except asyncio.TimeoutError:
    st.warning('❌ Application timeout, try again later.')
  except Exception as e:
    st.warning(f'❌ Something went wrong: {e}')

async def parse_dup_numbers(df, dedupe_validation, num_of_rows):
  try:
    async with asyncio.timeout(5):
      if len(set(df['phone_numbers'])) > 1 and set(df['phone_numbers']) != num_of_rows:
        st.warning('❌ Duplicate phone numbers detected.')
        return
      else:
        st.write('✅ No duplicate contacts detected.')
        dedupe_validation = True
        await asyncio.sleep(1)
        return dedupe_validation
  except asyncio.TimeoutError:
    st.warning('❌ Application timeout, try again later.')
  except Exception as e:
    st.warning(f'❌ Something went wrong: {e}')
  
async def distribute_sms(df, *args):
  message = df[['message']].values[0][0]
  link = df[['url']].values[0][0]
  log = {}
  for row, val in df['phone_numbers'].items(): 
    try:
      message = client.messages \
                  .create(
                      body=message + ' ' + link,
                      from_=twlo_number,
                      to=str(val)
                  )
      st.write(message.sid)
      log = {
        'uuid': str(uuid.uuid4()),
        'message_sid': message.sid,
        'phone_number': val,
        'user': name,
        'status': 'success',
        'error_msg': 'N/A'
      }
      msg_df = pd.DataFrame(log, index=[0])
    except Exception as e:
      st.warning(f'❌ Something went wrong: {e}')
      log = {
        'uuid': str(uuid.uuid4()),
        'message_sid': 'N/A',
        'phone_number': val,
        'user': name,
        'status': 'failed',
        'error_msg': e
      }
      msg_df = pd.DataFrame(log, index=[0])
  st.write('Distribution complete!')
  st.balloons()
  return msg_df

async def main():

  # SQLite = Database(db_name='st-app-db', url='', conn='', cur='')

  column_validation = False
  content_validation = False
  phone_num_validation = False
  dedupe_validation = False
  distro_success = False

  validate_disabled = True
  review_disabled = True
  distribute_disabled = True

  with st.expander("💡 What is this?"):
    st.write("This is an application designed to enable SPMs to interact" + 
             " directly with the Twilio API using a simple UI to distribute survey links. " +
             "Follow the three steps below to use the application.")
  st.subheader('1. Upload a .csv file')
  uploaded_file = st.file_uploader(label='upload_csv', type=['csv'], accept_multiple_files=False, 
                  help='Download the example file to see what the .csv parser accepts',
                  label_visibility='hidden')
  st.caption('The .csv file must have the following column headers: client_name, url, message, phone_numbers')
  st.caption('💡 Please remove the dummy data values included in the example file and replace them with your own.')
  if uploaded_file is not None:
    try:
      with st.spinner("Parsing file..."):
        df = pd.read_csv(uploaded_file)
        num_of_rows = calc_number_rows(df)
        async with asyncio.TaskGroup() as tg:
          column_validation = tg.create_task(check_file(df, column_validation))
          content_validation = tg.create_task(parse_msg_data(df, content_validation))
          phone_num_validation = tg.create_task(parse_valid_numbers(df, phone_num_validation))
          dedupe_validation = tg.create_task(parse_dup_numbers(df, dedupe_validation, num_of_rows))
          time.sleep(2)
        column_validation = column_validation.result()
        content_validation = content_validation.result()
        phone_num_validation = phone_num_validation.result()
        dedupe_validation = dedupe_validation.result()
    except Exception as e:
      st.warning(f'❌ Encountered error when validating file: {e}')
      return
        
  else:
    st.write('Please upload a file.')

  if column_validation is True and content_validation is True and phone_num_validation is True and dedupe_validation is True:
    validate_disabled = False
    st.write('File upload successful!')

  with open('example.csv', 'rb') as file:
    st.download_button(label='Download EX file ⬇️', file_name='example.csv', data=file, mime='text/csv', help='Downloads the example file')
  
  df2 = load_example_csv()

  st.dataframe(data=df2, width=800)
  st.caption('Please include the country code at the beginning of your phone numbers!')
  st.caption('💡 Pro Tip: Include your own phone number in the distribution list to ensure your distribution was sent.')
  st.divider()

  st.subheader('2. Validate your file')
  res = st.button(label='Validate ✅', disabled=validate_disabled)
  st.write(f'Validated: {res}')
  if res is True:
    with st.spinner('Processing file...'):
      time.sleep(2)
      df['phone_numbers'] = df['phone_numbers'].astype(str)
      df['phone_numbers'] = df["phone_numbers"].str.replace(",", "")
      st.dataframe(data=df, width=800)
      review_disabled = False
  elif uploaded_file is None:
    st.warning('You must upload a file first! ⛔')

  st.divider()
  st.subheader('3. Distribute surveys')
  st.write('Please review your file one last time.')
  st.write('⚠️ WARNING: All phone numbers included in the phone_numbers column will be sent an SMS message.')
  review = st.checkbox(label='Reviewed 🔎', disabled=review_disabled)
  st.write(f'Reviewed: {review}')
  if review is True:
    distribute_disabled = False
  else:
    st.warning('Please validate your .csv file first ⛔')

  distro = st.button(label='Distribute 🚀', disabled=distribute_disabled)
  if distro is True:
    try:
      msg_df = await asyncio.wait_for(distribute_sms(df), timeout=10.0)
      distro_success = True
    except asyncio.TimeoutError:
      st.warning('Request timed out, exiting process. Do not retry.')
    except Exception as e:
      st.warning(f'❌ Something went wrong: {e}')

  if distro_success is True:
    try:
      distribute_disabled = True
      check_db()
      loadData(msg_df)
      print('DB conn successful')
    except Exception as e:
      print(f'Something went wrong when connecting with db: {e}')

  # Figure out how to disable Distribute button after initial send
  # distribute_disabled = True

# For local dev
# Need a config.yaml file, see stauth GitHub for info on contents
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
    
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

name, authentication_status, username = authenticator.login()

if st.session_state["authentication_status"]:
    st.write(f'Welcome back, *{st.session_state["name"]}*')
    st.header('HotLinks 🔥🥵🚒', divider="rainbow")
    side_bar_state = 'expanded'
    asyncio.run(main())
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
