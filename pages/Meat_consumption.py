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
# @st.cache_data
# def get_data():
#     #connect to iiasa server 
#     conn = pyam.iiasa.Connection('ar6-public')
#     #other variables: 'Emissions|CO2', 'Primary Energy|Coal', 
#     #query for climate scenario data
#     df = conn.query(
#         model='REMIND-MAgPIE 2.1-4.2',
#         scenario = ['EN_NPi2020_500', 'SusDev_SDP-PkBudg1000'],
#         variable="Agricultural Demand|Livestock|Food",
#         RRRRRRRRRRRRRRRregion=['Asia', 'Latin America']
#     )
#     #return data format of df
#     return df.data

#df = get_data()

#selecting subset
regions_ = ["Asian countries except Japan", 
            "Latin American countries", 
            "Countries of the Middle East and Africa", 
            "OECD90 and EU (and EU candidate) countries"]
scenarios_ = ["EN_NPi2020_500", "SusDev_SDP-PkBudg1000"]
#selection = df[(df['scenario'].isin(scenarios_)) & (df["region"].isin(regions_))]

### IMPORT CSV DATA
df = pd.DataFrame(pd.read_csv("https://raw.githubusercontent.com/zyankarli/INCLISA/main/pages/scenario_archetypes.csv",
                                    sep=",", 
                                    lineterminator='\n'))


##Wrangle data
#fix last row name
df.rename(columns = {'2050\r':'2050'}, inplace=True)
#from wide to long
df = pd.melt(df, id_vars=['Scenario', 'Region'],
             var_name="Year", value_name="Value")
df["Year"] = df['Year'].astype(int)

#PLOTLY
##get colors
#sort on values of first year
regions_rank = df[df['Year'] == df["Year"].min()].sort_values(by='Value', ascending=False)
#drop duplicates
regions_rank = regions_rank.drop_duplicates(subset='Region')
#add color column ; could be automatise using sns
ReBu = ["#B2182B", "#D6604D", "#F4A582", "#FDDBC7", "#F7F7F7", "#D1E5F0", "#92C5DE", "#4393C3", "#2166AC"]
#add colors to df
regions_rank["Color"] = ReBu
#convert to dict
colors_dict = regions_rank.set_index('Region')['Color'].to_dict()

##plot
fig = px.line(df, x='Year', y="Value", color="Region", facet_col='Scenario',
                labels={
                     "Value": "kCal per capita/day",
                },
                category_orders={"Scenario": ["Scenario B", "Scenario C", "Scenario A"]},
                title="Climate Scenarios - Livestock Food Demand per region",
                range_x=[2018, 2050],
                range_y=[0, 1000],
                color_discrete_map=colors_dict
                )

# Add Lancet Healthy Diet 
fig.add_hline(y=250,
            annotation_text="Lancet Healthy Diet",
            annotation_position="bottom left",
            line_dash="dot")

#add legend
fig.update_layout(legend=dict(
    orientation="h",
    entrywidth=500,
    yanchor="bottom",
    y=-0.5, #1.02
    xanchor="left",
    x=1,
    bgcolor="White",
    bordercolor="Black",
    borderwidth=1
))
#make graph larger
fig.update_layout(width=1000, height=600)

st.plotly_chart(fig, theme="streamlit")


#add separating line
st.markdown("""---""")


#TODO: make graphs larger
#TODO: cache functions


st.markdown('### Feedback form')


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
    accepted_answers2 =["I think it is important for everyone to be above a certain threshold.",
                         "I think it is important to have a limit for consumption.",
                         "I think it is important that consumption converges by 2050.",
                         "I think it is important that lower consumption groups increase their \n consumption more rapidly by 2050 compared to 2020.",
                         "Other"]
    #key needs to be provide in case multiple same widgets are used in same form
    q1 = st.selectbox("Which scenario do you personally find to be more just, based on the graph above?", ["-"] + accepted_answers, key=1)
    q2 = st.selectbox("What was the main reason for your scenario selection?", ["-"] + accepted_answers2, key=2 )
    feedback = st.text_input("Please add additional points that you were thinking about when you picked your preferred option: ")
    timestamp = time.time()
    submitted = st.form_submit_button("Submit your entry!")
    if submitted:
        cursor = create_connection()
        query = f'INSERT INTO "{sheet_url}" VALUES ("{q1}", "{q2}", "{feedback}", "{timestamp}")'
        cursor.execute(query)
        st.write("Submission successful. Thank you for your feedback!")

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
