#Import libraries
import streamlit as st
#to import pictures, use Python Imaging Library
from PIL import Image

#set page configs
st.set_page_config(
     page_title='Justice in climate mitigation scenarios',
     initial_sidebar_state="auto"
)

#add page title and sidebar
st.markdown('# Justice in climate mitigation scenarios')
st.sidebar.markdown('# Justice in climate mitigation scenarios')

#add columns
col1, col2, col3 = st.columns(3)

with col2:
     #import images
     image1 = Image.open("pages/p1_Climate Justice.png")
     st.image(image1)


# 2 ways forward
#TODO: 1) reseize original pictures
#TODO: 2) ensure that full-size pictures are central [requires CSS] 
#TODO: bring it online
