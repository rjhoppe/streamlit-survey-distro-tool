import streamlit as st
import pandas as pd
import sqlite3
import altair as alt

msg_data_df = pd.DataFrame()
query = "SELECT * FROM messages"

try: 
  with sqlite3.connect('database/app.db', isolation_level=None, check_same_thread=False) as conn:
    cur = conn.cursor()
    msg_data_df = pd.read_sql_query(query, conn)
except sqlite3.Error as e:
  print('Encountered error retrieving messages from db: ', e)
finally:
  conn.commit()
  conn.close()

msg_data_df['phone_number'] = msg_data_df['phone_number'].astype(str)
msg_data_df['phone_number'] = msg_data_df["phone_number"].str.replace(",", "")

st.set_page_config(
  page_title="Message Logs",
  page_icon='📖',
  layout='wide',
  initial_sidebar_state='expanded'
)

alt.themes.enable('dark')
st.header('Message Distribution Log', divider='rainbow')
st.dataframe(
  column_config={
    "uuid": None,
  },
  data=msg_data_df, 
  use_container_width=True
)