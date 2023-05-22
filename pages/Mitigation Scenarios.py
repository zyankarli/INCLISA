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

#set page intial config
st.set_page_config(
     layout="wide")
#Header
st.sidebar.markdown('# Mitigation scenarios')

#Text

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
### WRANGLE DATA
#fix last row name
df.rename(columns = {'2050\r':'2050'}, inplace=True)
#from wide to long
df = pd.melt(df, id_vars=['Scenario', 'Region'],
             var_name="Year", value_name="Value")
df["Year"] = df['Year'].astype(int)

### CREATE PLOTLY PLOT
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

df['Scenario'] = df['Scenario'].replace({"Scenario A":"Scenario \u2BC3", 
                                         "Scenario B": 'Scenario \u25A0',
                                         "Scenario C": "Scenario \u25C6"})

##plot
fig = px.line(df, x='Year', y="Value", color="Region", facet_col='Scenario',
                labels={
                     "Value": "kCal per capita/day",
                },
                #TODO automise random order
                category_orders={"Scenario": ["Scenario \u2BC3", "Scenario \u25A0", "Scenario \u25C6"]},
                title="Climate Scenarios - Meat consumption per region",
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
    orientation="v",
    entrywidth=100,
    entrywidthmode='fraction',
    yanchor="bottom",
    y=0.35,
    xanchor="right",
    x=1.17,
    bgcolor="White",
    bordercolor="Black",
    borderwidth=1
))
#make graph larger
fig.update_layout(width=1250)
#change subplot figure titles
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))


#-------------------------#
#          2ndFIG         #
#-------------------------#

df2 = pd.DataFrame(pd.read_csv("https://raw.githubusercontent.com/zyankarli/INCLISA/main/pages/output.csv",
                                    sep=",", 
                                    lineterminator='\n'))


### WRANGLE DATA
#fix last row name
df2.rename(columns = {'year':'Year',
                      'region': "Region",
                      'value':"Value",
                      'scenario':"Scenario"}, inplace=True)



#from wide to long
#df = pd.melt(df, id_vars=['Scenario', 'Region'],
#             var_name="Year", value_name="Value")
df2["Year"] = df2['Year'].astype(int)
df2["Value"] = df2["Value"].astype(int)

### CREATE PLOTLY PLOT
##get colors
#sort on values of first year
regions_rank = df2[df2['Year'] == df2["Year"].min()].sort_values(by='Value', ascending=False)
#drop duplicates
regions_rank = regions_rank.drop_duplicates(subset='Region')
#add color column ; could be automatise using sns
ReBu = ["#B2182B", "#D6604D", "#F4A582", "#FDDBC7", "#F7F7F7", "#D1E5F0", "#92C5DE", "#4393C3", "#2166AC"]
#add colors to df
regions_rank["Color"] = ReBu
#convert to dict
colors_dict = regions_rank.set_index('Region')['Color'].to_dict()

#df['Scenario'] = df['Scenario'].replace({"Scenario A":"Scenario \u2BC3", 
#                                         "Scenario B": 'Scenario \u25A0',
#                                         "Scenario C": "Scenario \u25C6"})

##plot
fig2 = px.line(df2, x='Year', y="Value", color="Region", facet_col='Scenario',
                labels={
                     "Value": "Passenger kilometer per year",
                },
                #TODO automise random order
                #category_orders={"Scenario": ["Scenario \u2BC3", "Scenario \u25A0", "Scenario \u25C6"]},
                title="Climate Scenarios - Transportion per region",
                range_x=[2020, 2050],
                range_y=[0, 12000],
                color_discrete_map=colors_dict
                )

# Add Lancet Healthy Diet 
fig2.add_hline(y=8000,
              annotation_text="Pkm per year Japan",
              annotation_position="bottom left",
              line_dash="dot")

#add legend
fig2.update_layout(legend=dict(
    orientation="h",
    #entrywidth=10,
    #entrywidthmode='fraction',
    yanchor="bottom",
    y=-0.5,
    xanchor="right",
    x=1,
    bgcolor="White",
    bordercolor="Black",
    borderwidth=1
))
#make graph larger
fig2.update_layout(width=1250)
#change subplot figure titles
fig2.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))



#TODO: make graphs larger
#TODO: cache functions


st.markdown('# Mitigation Scenarios')


#prepare google sheet connection
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

### PREPARE FORM OBJECTS & LISTS
#load country data function
@st.cache_data
def load_countries():
    #load data from github
    df = pd.read_csv("https://raw.githubusercontent.com/OxfordEconomics/CountryLists/master/countryList-UN.csv", 
                                lineterminator='\n',skiprows=0, encoding="latin")
    #limit df to first column in case csv file changes
    df = df.iloc[:,0]
    #TODO: ask elina what's the best approach on that
    return df
country_list = ["-"] + list(load_countries())

accepted_answers = ["Scenario \u2BC3", "Scenario \u25A0", "Scenario \u25C6"]
accepted_answers2 =["I think it is important for everyone to be above a certain threshold.",
                        "I think it is important to have a limit for consumption.",
                        "I think it is important that consumption converges by 2050.",
                        "I think it is important that lower consumption groups increase their \n consumption more rapidly by 2050 compared to 2020.",
                        "Other"]

#initiate form
with st.form("Survey"):
    #Initiate tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Meat Consumption", "Transportation", "Other sectors...", "Personal Questions"])
    #TODO: check for update on placeholder here https://github.com/streamlit/streamlit/issues/949
    #MEAT CONSUMPTION
    with tab1:
        #Introduction
        st.markdown(":red[**The text below is a placeholder. More information will be provided later.**]")
        st.markdown("""---""")
        st.markdown('### Meat Consumption')
        st.markdown("**The livestock sector is an important contributor to greenhouse gas emissions.**")
        st.markdown("Below **we show trends of meat consumption** in different macro regions in three archetypal scenarios.")
        st.markdown("""Scenario \u2BC3 assumes linear growth rates.  
                    Scenario \u25A0 assumes that consumption stabilises in high-consuming regions while other regions increase their consumption.  
                    Lastly, scenario \u25C6 assumes that consumption rates converge globally.""")

        #key needs to be provide in case multiple same widgets are used in same form
        st.plotly_chart(fig, theme="streamlit")

        q1 = st.radio("Which scenario do you personally find to be the fairest, based on the graph above?", ["-"] + accepted_answers,horizontal=True ,key=1)
        q2 = st.text_input("Why do you find this scenario to be the fairest?", placeholder="Please enter your answer here", key=2)
        q3 = st.radio("Which of the following aspects does best describe your main reason for your scenario selection?", ["-"] + accepted_answers2, key=3 )
    #st.markdown("""---""")
        st.markdown("***Please continue this survey by scrolling upwards and selecting the 'Personal Questions' tab.***")
    with tab2:
         st.markdown("### Transportation")
         st.markdown("A introductory text will be added here at a later stage.")
         st.plotly_chart(fig2, theme="streamlit")
    with tab3:
        st.markdown('### Other sectors will be added at a later stage.')
    with tab4:
        st.markdown('### Personal Questions')
        q4 = st.selectbox("Which country are you from? (Please select the country you feel closer to and more knowledgeable about)",
                        country_list)
        q5 = st.selectbox("What type of organisation do you work for?", 
                        ("-", "Government", "Research or academic organisation", "Non-governmental organisation", "Interational organisation", "Private Sector", "Other"), key=5)
        #TODO: add conditional pop-up for st text with other
        q6 = st.selectbox("What is the highest level of education you have completed?",
                        ("-", 'No degree', 'High school diploma (or equivalent)', 'Some college', 'Professional degree', "Bachelor's degree", "Master's degree", "Doctoral degree"), key=6)
        q7 = st. selectbox("What is your age?",
                        ("-", "18-24", '25-34','35-44','45-54','55-64','65-100'), key=7)
        q8 = st.selectbox("What is your gender?",
                        ("-", "Male", "Female", "Other", "Prefer not to say"), key=8)
        q9 = st.selectbox("To which sector is your work most related to?",
                        ("-", "Agriculture", "Industry", "Transport", "Buildings", "General climate mitigation", "Other"),  key=9)
        #TODO: implement Shonalis suggestion to add words to sectors
        q10 = st.selectbox("How knowledgeable are you about Integrated Assessment Models used for climate mitigation scenarios?",
                        ("-", "No prior experience", "Experience in the context of reports such as IPCC", "Occasional user of scenario outputs", "Expert level"), key=10)
        timestamp = time.time()
        #Submit button; send data to google sheet
        submitted = st.form_submit_button("Click here to submit!")
        if submitted:
            cursor = create_connection()
            query = f'INSERT INTO "{sheet_url}" VALUES ("{q1}", "{q2}", "{q3}", "{q4}", "{q5}", "{q6}", "{q7}", "{q8}", "{q9}", "{q10}", "{timestamp}")'
            cursor.execute(query)
            st.write("**:green[Submission successful. Thank you for your feedback!]**")

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
