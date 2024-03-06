import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import yaml
from yaml.loader import SafeLoader

st.set_page_config(
	page_title="Login",
	page_icon='🔑',
	layout='wide',
	initial_sidebar_state='expanded'
)
	
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
	side_bar_state = 'expanded'
	st.header('[Application Name]', divider="rainbow")
	st.write('You have successfully logged in. Navigate to the other pages on the sidebar to use the application.')
elif st.session_state["authentication_status"] is False:
	st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
	st.warning('Please enter your username and password.')