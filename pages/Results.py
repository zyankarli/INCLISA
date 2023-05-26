#Import libraries
import streamlit as st
import pandas as pd
from shillelagh.backends.apsw.db import connect
from google.oauth2 import service_account
import plotly.express as px

#set page intial config
st.set_page_config(
     layout="wide")


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

cursor = create_connection()

# Perform SQL query on the Google Sheet.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=5)
def run_query(query):
    rows = cursor.execute(query)
    rows = rows.fetchall()
    return rows

#Get data
##define data wrangling function
def wrangle_data():
    df = pd.DataFrame(run_query(f'SELECT * FROM "{sheet_url}"'))
#rename columns
    df.columns= ['scen_meat', 'scen_meat_feedback', 'scen_meat_reason', 
            'scen_tran', 'scen_tran_feedback', 'scen_tran_reason', 
            'scen_buil', 'scen_buil_feedback', 'scen_buil_reason', 
            'scen_gdp', 'scen_gdp_feedback', 'scen_gdp_reason', 
             'meat_consumption', 'air_travel', 'housing_space','country', 'organisation', 'education', 'age','gender', 'sector','iam','timestamp']

    #wrangle data
    to_plot = df[['scen_meat', 'scen_tran', 'scen_buil', 'scen_gdp']]
    #rename scenarios
    to_plot = to_plot.rename(columns={'scen_meat':"Food",
                                      'scen_tran':"Mobility",
                                      'scen_buil':'Housing',
                                      'scen_gdp':"Economic Activity"})

    #change wide to long
    to_plot = pd.melt(to_plot, var_name="Scenario", value_name="Value")
    #drop "-"
    to_plot = to_plot[to_plot.Value != "-"]
    return to_plot

to_plot = wrangle_data()

#TODO: only reload graph on click
if st.button('Click here to update the graph.'):
    wrangle_data()      

fig = px.bar(to_plot, x ='Value', color="Scenario",barmode='group',
              labels={
                     "Value": "",
                     'count': "Count"
                },
                #TODO automise random order
                title="Results: Climate mitigation scenarios per sector")

#Size
plot_width=600 
plot_height= plot_width * 0.75 


fig.update_layout(
    legend = dict(
        title_text = "Sector",
        ),
        width = plot_width,
        height = plot_height
    )

#Deactivate zoom/ True = deactivated
#Disable zoom feature
fig.layout.xaxis.fixedrange = False
fig.layout.yaxis.fixedrange = False


st.plotly_chart(fig, theme="streamlit", use_container_width=True)




#adjust layout
#inclulde buttons ?https://plotly.com/python/custom-buttons/
