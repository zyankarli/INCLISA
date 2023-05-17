#Import libraries
import streamlit as st
#to import pictures, use Python Imaging Library
from PIL import Image

#set page configs
st.set_page_config(
     page_title='Justice in climate mitigation scenarios',
     initial_sidebar_state="expanded",
)

#add page title and sidebar
st.markdown('# Justice in climate mitigation scenarios')
st.sidebar.markdown('# Justice in climate mitigation scenarios')

#import images
image1 = Image.open("pages/p1_Climate Justice.png")
st.image(image1, width=750)


# 2 ways forward
#TODO: 1) reseize original pictures
#TODO: 2) ensure that full-size pictures are central [requires CSS] 
#TODO: bring it online
