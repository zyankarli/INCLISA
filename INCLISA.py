#Import libraries
import streamlit as st
#to import pictures, use Python Imaging Library
from PIL import Image

#add page title and sidebar
st.markdown('# Climate justice')
st.sidebar.markdown('# Climate justice')

#import images
image1 = Image.open("pages/p1_Climate Justice.png")
image2 = Image.open("pages/p2_Justice Dimensions.png")


st.image(image1, width=750)
st.image(image2, width=750)

# 2 ways forward
#TODO: 1) reseize original pictures
#TODO: 2) ensure that full-size pictures are central [requires CSS] 
#TODO: bring it online
