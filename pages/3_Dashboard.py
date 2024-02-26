# import streamlit as st
# import sqlite3
# import pandas as pd
# import altair as alt
# # import plotly.express as px

# st.set_page_config(
#   page_title="Dashboard",
#   page_icon='📈',
#   layout='wide',
#   initial_sidebar_state='expanded'
# )

# def load_db_data(msg_data_df):
#   query = "SELECT * FROM messages"
#   try: 
#     with sqlite3.connect('database/app.db', isolation_level=None, check_same_thread=False) as conn:
#       # cur = conn.cursor()
#       msg_data_df = pd.read_sql_query(query, conn)
#   except sqlite3.Error as e:
#     print('Encountered error retrieving messages from db: ', e)
#   finally:
#     conn.commit()
#     conn.close()

#   msg_data_df['phone_number'] = msg_data_df['phone_number'].astype(str)
#   msg_data_df['phone_number'] = msg_data_df["phone_number"].str.replace(",", "")
#   return msg_data_df


# # alt.themes.enable('dark')

# def main():
#   msg_data_df = pd.DataFrame()
#   user_data_df = pd.DataFrame()
#   msg_data_df = load_db_data(msg_data_df)
#   msg_data_df['created'] = pd.to_datetime(msg_data_df['created'])
#   msg_data_df['created'] = msg_data_df['created'].dt.date
#   msg_data_df = msg_data_df.sort_values(by='created', ascending=False)
#   st.dataframe(
#     column_config={
#       "uuid": None,
#     },
#     data=msg_data_df, 
#     use_container_width=True
#   )
#   # user_data_df = msg_data_df.groupby('user').size().reset_index(name='message_sid')
#   # user_data_df = user_data_df.rename(columns={'user': 'User', 'message_sid': 'Message Count'})
#   user_data_df = msg_data_df[['user', 'created', 'message_sid']]
#   st.dataframe(
#     column_config={
#       "uuid": None,
#     },
#     data=user_data_df, 
#     use_container_width=True
#   )
#   st.header('Dashboard', divider='rainbow')
#   st.line_chart(user_data_df, x='created', y='message_sid', color='user')
#   # st.bar_chart(user_data_df, x='User', y='Message Count')
#   st.bar_chart(msg_data_df, x='created', y='message_sid')
#   st.bar_chart(msg_data_df, x='user', y='message_sid')


# if st.session_state["authentication_status"]:
#     st.write(f'Welcome back, *{st.session_state["name"]}*')
#     main()
# elif st.session_state["authentication_status"] is False:
#     st.error('Username/password is incorrect')
# elif st.session_state["authentication_status"] is None:
#     st.warning('Please login on the App page before accessing the application')