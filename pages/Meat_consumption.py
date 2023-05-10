#Import libraries
import streamlit as st
#import pyam
import plotly.express as px
import streamlit_survey as ss
import pandas as pd
from shillelagh.backends.apsw.db import connect
from google.oauth2 import service_account
import time
from PIL import Image

#Header
st.markdown('# Meat consumption patterns')
st.sidebar.markdown('# Meat consumption patterns')

#Text
st.markdown("**The livestock sector is an important contributor to greenhouse gas emissions.**")
st.markdown("Below **we show trends of livestock demand** in different macro regions in two different scenarios that reach the 1.5°C target in 2100. These scenarios have been developed by the REMIND MAgPIE model. The 'Food Demand Livestock' variable measures daily per capita consumption of animal proteins.")
st.markdown("The first scenario assumes a continuation of current trends of livestock consumption, while the second scenario assumes a global convergence to a low-meat diet by 2050.")

#PYAM
#Model to use: REMIND-MAgPIE 2.1-4.2

#create funciton and cache it to save on compuation
'''@st.cache_data
def get_data():
    #connect to iiasa server 
    conn = pyam.iiasa.Connection('ar6-public')
    #other variables: 'Emissions|CO2', 'Primary Energy|Coal', 
    #query for climate scenario data
    df = conn.query(
        model='REMIND-MAgPIE 2.1-4.2',
        scenario = ['EN_NPi2020_500', 'SusDev_SDP-PkBudg1000'],
        variable="Agricultural Demand|Livestock|Food",
        region=['Asia', 'Latin America']
    )
    #return data format of df
    return df.data
'''
#df = get_data()

#selecting subset
regions_ = ["Asian countries except Japan", 
            "Latin American countries", 
            "Countries of the Middle East and Africa", 
            "OECD90 and EU (and EU candidate) countries"]
scenarios_ = ["EN_NPi2020_500", "SusDev_SDP-PkBudg1000"]
#selection = df[(df['scenario'].isin(scenarios_)) & (df["region"].isin(regions_))]

### IMPORT CSV DATA
selection = pd.DataFrame(pd.read_csv("https://raw.githubusercontent.com/zyankarli/INCLISA/main/pages/scenario_data.csv",
                                    sep=",", 
                                    lineterminator='\n'))

#PLOTLY
##first attempt: two seperate figures
#create both figures


#second attempt to combine figures
##get one large data sheet

fig3 = px.line(selection, x='year', y="value\r", color="region", facet_col='scenario',
                labels={
                     "year": "Year",
                     "value": "Livestock Food Demand",
                     "region": "Region"
                    }, 
                title="Climate Scenarios - Livestock Food Demand per region",
                range_x=[2005, 2100],
                range_y=[0, 250]
                )

#fig3.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True)
#fig3.update_yaxes(showline=True, linewidth=2, linecolor='black', mirror=True)
fig3.update_layout(legend=dict(
    orientation="h",
    entrywidth=200,
    yanchor="bottom",
    y=-0.5, #1.02
    xanchor="right",
    x=1,
    bgcolor="LightSteelBlue",
    bordercolor="Black",
    borderwidth=2
))


st.plotly_chart(fig3, theme="streamlit")

#fig3.update_layout(height=600, width=800, title_text="Side By Side Subplots")




#TODO implement chache to reduce loading time; get all countries
#TODO: make graphs share legend
#TODO: make graphs larger


#import images
image1 = Image.open("pages/Scenario_Archetypes.png")
st.image(image1, width=500)

st.markdown('### Feedback survey')








#connect google sheet

sheet_url = st.secrets["private_gsheets_url"]

def create_connection():
        credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], 
        scopes=["https://www.googleapis.com/auth/spreadsheets",],)
        connection = connect(":memory:", adapter_kwargs={
            "gsheetsapi" : { 
            "service_account_info" : {
                "type" : st.secrets["gcp_service_account"]["type"],
                "project_id" : st.secrets["gcp_service_account"]["project_id"],
                "private_key_id" : st.secrets["gcp_service_account"]["private_key_id"],
                "private_key" : st.secrets["gcp_service_account"]["private_key"],
                "client_email" : st.secrets["gcp_service_account"]["client_email"],
                "client_id" : st.secrets["gcp_service_account"]["client_id"],
                "auth_uri" : st.secrets["gcp_service_account"]["auth_uri"],
                "token_uri" : st.secrets["gcp_service_account"]["token_uri"],
                "auth_provider_x509_cert_url" : st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
                "client_x509_cert_url" : st.secrets["gcp_service_account"]["client_x509_cert_url"],
                }
            },
        })
        return connection.cursor()



#create form objects
with st.form("Survey"):
    accepted_answers = ["Scenario A", "Scenario B", "Scenario C"]
    accepted_answers2 =["The level of consumption in 2050 achieved across regions",
                        "Whether the levels of consumption converge or not by 2050",
                        "By how much regions (especially that have a lower consumption starting point) improve compared to 2020 ​",
                        "Other"]
    #key needs to be provide in case multiple same widgets are used in same form
    q1 = st.selectbox("Which scenario do you personally find to be more just, based on the graph above?", ["-"] + accepted_answers, key=1)
    q2 = st.selectbox("What was the main reason for your scenario selection?", ["-"] + accepted_answers2, key=2 )
    feedback = st.text_input("Please add additional points that you were thinking about when evaluating the trajectories:")
    timestamp = time.time()
    submitted = st.form_submit_button("Submit your entry!")
    if submitted:
        cursor = create_connection()
        query = f'INSERT INTO "{sheet_url}" VALUES ("{q1}", "{q2}", "{feedback}", "{timestamp}")'
        cursor.execute(query)

#Links for the solution above
#https://discuss.streamlit.io/t/solved-issue-of-pulling-private-google-sheet-into-a-streamlit-app-using-gspread-instead-of-gsheetsdb/39056/4
#https://discuss.streamlit.io/t/sending-data-to-private-google-sheet-authentication-st-secrets/31420        

#st.forms
#https://discuss.streamlit.io/t/get-user-input-and-store-in-a-database-table/31115


#TODO: find way to save data
#Google sheets: https://medium.com/nyu-ds-review/how-to-create-a-python-web-app-to-securely-collect-and-store-user-information-cb8f36921988
#https://medium.com/@jb.ranchana/write-and-append-dataframes-to-google-sheets-in-python-f62479460cf0
#trubrics: https://trubrics.github.io/trubrics-sdk/streamlit/
##account: inclisa@inclisa.iam.gserviceaccount.com
