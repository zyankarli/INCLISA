#Import libraries
import streamlit as st
#to import pictures, use Python Imaging Library
from PIL import Image

#set page configs
st.set_page_config(
     page_title='Justice in climate mitigation scenarios',
     initial_sidebar_state="auto",
     page_icon=Image.open("pages/IIASA_PNG logo-short_blue.png")
)

#hide menu and footer
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)



#add page title and sidebar
st.markdown('# Justice in climate mitigation scenarios')
#st.sidebar.markdown('# Justice in climate mitigation scenarios')

#add columns
col1, col2, col3 = st.columns(3)

with col2:
     #import images
     image1 = Image.open("pages/p1_Climate Justice.png")
     st.image(image1)


#ensure that picture is centered when in full screen mode
st.markdown(
    """
    <style>
        button[title^=Exit]+div [data-testid=stImage]{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True
)

