import streamlit as st
import pandas as pd
import sqlite3
import altair as alt

st.set_page_config(
  page_title="Message Logs",
  page_icon='📖',
  layout='wide',
  initial_sidebar_state='expanded'
)

def load_db_data(msg_data_df):
  query = "SELECT * FROM messages"
  try: 
    with sqlite3.connect('database/app.db', isolation_level=None, check_same_thread=False) as conn:
      # cur = conn.cursor()
      msg_data_df = pd.read_sql_query(query, conn)
  except sqlite3.Error as e:
    print(f'Encountered error retrieving messages from db: {e}')
  finally:
    conn.commit()
    conn.close()

  msg_data_df['phone_number'] = msg_data_df['phone_number'].astype(str)
  msg_data_df['phone_number'] = msg_data_df["phone_number"].str.replace(",", "")
  return msg_data_df

def main():
  msg_data_df = pd.DataFrame()
  msg_data_df = load_db_data(msg_data_df)
  msg_data_df = msg_data_df.sort_values(by='created', ascending=False)
  st.header('Message Distribution Log', divider='rainbow')
  st.dataframe(
    column_config={
      "uuid": None,
    },
    data=msg_data_df, 
    use_container_width=True
  )

if st.session_state["authentication_status"]:
    st.write(f'Welcome back, *{st.session_state["name"]}*')
    main()
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please login on the App page before accessing the application')