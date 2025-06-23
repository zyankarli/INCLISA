#-------------------------#
#        LIBRARIES        #
#-------------------------#
import streamlit as st
from PIL import Image

#------------------------------------------------------------------------------#

#-------------------------#
#      CONFIGURATIONS     #
#-------------------------#
#set page configs
st.set_page_config(
     layout="wide",
     page_title='Justice in climate mitigation scenarios',
     initial_sidebar_state="expanded",
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

#hide fullscreen button for plots
hide_img_fs = '''
<style>
button[title="View fullscreen"]{
    visibility: hidden;}
</style>
'''
st.markdown(hide_img_fs, unsafe_allow_html=True)

def update_selectbox_style():
    st.markdown(
        """
        <style>
            .stSelectbox [data-baseweb="select"] div[aria-selected="true"] {
                white-space: normal; overflow-wrap: anywhere;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
#update_selectbox_style()

# Define your pages using st.Page
pages = [
    st.Page("pages/Content.py", title="Home", icon="🏠"),
    st.Page("pages/Results.py", title="Results", icon="📊"),
    # Add other pages as needed
]

# Create the navigation object
nav = st.navigation(pages, position="sidebar", expanded=True)

# Run the selected page
nav.run()
