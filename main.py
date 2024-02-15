import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import os
import yaml
import asyncio
from dotenv import load_dotenv
import yaml
from yaml.loader import SafeLoader
from textblob import TextBlob
from twilio.rest import Client

num_of_rows = 0
request_num = 0

load_dotenv()
account_sid = os.getenv('TWLO_SID')
auth_token = os.getenv('TWLO_TOKEN')
twlo_number = os.getenv('TWLO_NUMBER')
client = Client(account_sid, auth_token)

st.set_page_config(
    page_title="HotLinks",
    page_icon="🥵",
)

def calc_number_rows(df):
  num_of_rows = len(df)
  if num_of_rows > 200:
    st.write("Distribution list exceeds 100 respondents. Please reduce the list or reach out to admin.")
  else:
    return num_of_rows

def update_btn_text(res):
  res = st.button(label='Send Surveys')
  return res

async def check_file(df, column_validation):
  if df.columns.tolist() != ['client_name','url','message','phone_numbers']:
    st.write('Column headers incorrect. Check spelling and order.')
  else:
    st.write('Column headers formatted correctly.')
    column_validation = True
    return column_validation
  
async def parse_msg_data(df, content_validation):
  message = TextBlob(df[['message']].values[0][0])
  if message != str(df[['message']].values[0][0]):
    st.write('Spelling errors detected in message.')
    st.write(f'Recommended spelling: {message.correct()}')
  else:
    st.write('Message content spellchecked.')
    content_validation = True
    return content_validation

async def parse_valid_numbers(df, phone_num_validation):
  for i, v in enumerate(df['phone_numbers']):
    v = len(str(v))
    if v != 11:
       st.write(f'Invalid phone number at row: {i}')
    else:
      st.write('Phone numbers validated.')
  phone_num_validation = True
  return phone_num_validation

async def parse_dup_numbers(df, dedupe_validation, num_of_rows):
  if set(df['phone_numbers']) != num_of_rows:
    st.write('Duplicate phone numbers detected.')
    return
  else:
    st.write('No duplicates detected')
    dedupe_validation = True
    return dedupe_validation
  
async def distribute_sms(df, df2, num_of_rows, request_num):
  message = df[['message']].values[0][0]
  for row, val in df['phone_numbers'].items(): 
    message = client.messages \
                .create(
                    body=message,
                    from_=twlo_number,
                    to=str(val)
                )
    st.write(message.sid)

async def main():
  column_validation = False
  content_validation = False
  phone_num_validation = False
  dedupe_validation = False

  validate_disabled = True
  review_disabled = True
  distribute_disabled = True

  with st.expander("What is this? 💡"):
    st.write("This is an application designed to enable SPMs to interact" + 
             " directly with the Twilio API using a simple UI to distribute their survey invites." +
             "Follow the three steps below to use the application.")
  st.subheader('1. Upload a .csv file')
  uploaded_file = st.file_uploader(label='upload_csv', type=['csv'], accept_multiple_files=False, 
                  help='Download the example file to see what the .csv parser accepts',
                  label_visibility='hidden')
  st.caption('The .csv file must have the following column headers: client_name, url, message, phone_numbers')
  if uploaded_file is not None:
      with st.spinner("Parsing file..."):
        df = pd.read_csv(uploaded_file)
        num_of_rows = calc_number_rows(df)
        async with asyncio.TaskGroup() as tg:
          column_validation = tg.create_task(check_file(df, column_validation))
          content_validation = tg.create_task(parse_msg_data(df, content_validation))
          phone_num_validation = tg.create_task(parse_valid_numbers(df, phone_num_validation))
          dedupe_validation = tg.create_task(parse_dup_numbers(df, dedupe_validation, num_of_rows))
  else:
    st.write('Please upload a file.')

  if column_validation == False:
    st.write("Validation failed: Check column headers.")
  elif content_validation == False:
    st.write("Validation failed: Check message content.")
  elif phone_num_validation == False:
    st.write("Validation failed: Ensure phone numbers are 11 digits and include a country code at the beginning.")
  elif dedupe_validation == False:
    st.write("Validation failed: Remove duplicate phone numbers.")
  else:
    validate_disabled = False
    st.write('File validation successful!')

  with open('example.csv', 'rb') as file:
    st.download_button(label='Download EX file ⬇️', file_name='example.csv', data=file, mime='text/csv', help='Downloads the example file')
  
  df2 = pd.read_csv('example.csv')
  df2['phone_numbers'] = df2['phone_numbers'].astype(str)
  df2['phone_numbers'] = df2["phone_numbers"].str.replace(",", "")
  st.dataframe(data=df2, width=800)
  st.caption('Please include the country code at the beginning of your phone numbers!')
  st.divider()

  st.subheader('2. Validate your file')
  res = st.button(label='Validate ✅', disabled=validate_disabled)
  st.write(f'Validated: {res}')
  if res == True:
    df['phone_numbers'] = df['phone_numbers'].astype(str)
    df['phone_numbers'] = df["phone_numbers"].str.replace(",", "")
    st.dataframe(data=df, width=800)
    review_disabled = False
  elif uploaded_file is None:
    st.warning('You must upload a file first! ⛔')

  st.divider()
  st.subheader('3. Distribute surveys')
  st.write('Please review your file one last time')
  review = st.checkbox(label='Reviewed 🔎', disabled=review_disabled)
  st.write(f'Reviewed: {review}')
  if review == True:
    distribute_disabled = False
  else:
    st.warning('Please validate your .csv file first ⛔')

  distro = st.button(label='Distribute 🚀', disabled=distribute_disabled)
  if distro == True:
    df2 = df['phone_numbers']
    print(df2)
    await distribute_sms(df, df2, num_of_rows, request_num)
    st.write('Distribution complete!')
    st.balloons()

with open('../config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

name, authentication_status, username = authenticator.login()

if st.session_state["authentication_status"]:
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.header('HotLinks 🔥🥵🚒', divider="rainbow")
    asyncio.run(main())
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
