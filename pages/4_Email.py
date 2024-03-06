import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import os
import asyncio
import sqlite3

st.set_page_config(
    page_title="Email",
    page_icon="✉️",
    layout='wide',
    initial_sidebar_state='expanded'
)

def main():
  st.header('Email Distribution', divider='rainbow')
  st.warning('⚠️ Under construction')

try: 
  if st.session_state["authentication_status"]:
      st.write(f'Welcome back, *{st.session_state["name"]}*')
      main()
  elif st.session_state["authentication_status"] is False:
      st.error('Username/password is incorrect')
  elif st.session_state["authentication_status"] is None:
      st.warning('Please login on the App page before accessing the application')

except KeyError:
  st.warning('You must login on the Login page before proceeding.')