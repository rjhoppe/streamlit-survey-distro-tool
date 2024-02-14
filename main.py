import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import yaml
import asyncio
from yaml.loader import SafeLoader

num_of_rows = 0

def check_file(df):
  if df.columns.tolist() != ['client_name','url','message','phone_numbers']:
    st.write('Column headers incorrect. Check spelling and order.')
    return
  else:
    num_of_rows = df.columns.tolist() - 1
    st.write('Column headers formatted correctly...parsing data')
    return num_of_rows

async def parse_msg_data(df):
  for i, v in enumerate(df['message']): 
    if v == '':
      st.write(f'Empty message column at row: {i}')
    else:
       st.write('Message content validated')
  return

async def parse_valid_numbers(df):
  for i, v in enumerate(df['phone_numbers']):
    if len(v) != 11:
       st.write(f'Invalid phone number at row: {i}')
    else:
      st.write('Phone numbers validated')
  return

async def parse_dup_numbers(df):
  if set(df['phone_numbers']) != num_of_rows:
    st.write('Duplicate phone numbers detected.')
    return
  else:
    st.write('No duplicates detected')
    return
  
def update_btn_text(res):
  res = st.button(label='Send Surveys')
  return res
  
async def main():
  st.subheader('1. Upload a .csv file')
  uploaded_file = st.file_uploader(label='upload_csv', type=['csv'], accept_multiple_files=False, 
                  help='Download the example file to see what the .csv parser accepts',
                  label_visibility='hidden')
  st.caption('The .csv file must have the following column headers: client_name, url, message, phone_numbers')
  if uploaded_file is not None:
      with st.spinner("Parsing file..."):
        df = pd.read_csv(uploaded_file)
        check_file(df)
        async with asyncio.TaskGroup() as tg:
          tg.create_task(parse_msg_data(df))
          tg.create_task(parse_valid_numbers(df))
          tg.create_task(parse_dup_numbers(df))
        st.write('File validation complete')
  else:
    st.write('Please upload a file.')

  st.download_button(label='Download EX file ⬇️', data='notes.txt', help='Downloads the example file')
  df2 = pd.read_csv('example.csv')
  df2['phone_numbers'] = df2['phone_numbers'].astype(str)
  df2["phone_numbers"] = df2["phone_numbers"].str.replace(",", "")
  st.dataframe(data=df2, width=800)
  st.divider()

  st.subheader('2. Validate your file')
  res = st.button(label='Validate ✅')
  st.write(f'Validated: {res}')
  if res == True:
    st.dataframe(data=df, width=800)
  elif uploaded_file is None:
    st.warning('You must upload a file first! ⛔')

  st.divider()
  st.subheader('3. Distribute surveys')
  st.write('Please review your file one last time')
  review = st.button(label='Review 🔎')
  st.write(f'Reviewed: {review}')
  if review == True and res == True:
    # st.dataframe(data=df, width=800)
    st.button(label='Distribute 🚀')
  else:
    st.warning('Please validate your .csv file first ⛔')

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
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.header('HotLinks 🔥🥵🚒', divider="rainbow")
    asyncio.run(main())
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
