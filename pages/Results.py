#Import libraries
import streamlit as st
import pandas as pd
from shillelagh.backends.apsw.db import connect
from google.oauth2 import service_account
import plotly.express as px

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
#TODO: only reload graph on click
df = pd.DataFrame(run_query(f'SELECT * FROM "{sheet_url}"'))
#rename columns
df.columns= ['scen_meat', 'scen_meat_feedback', 'scen_meat_reason', 'country', 'organisation', 'education', 'age','gender', 'sector','iam','timestamp']
#Create plot
fig = px.bar(df[df['scen_meat'] != '-'], x='scen_meat',
             labels={
                     "scen_meat": "Scenario",
                     'count': "Count"
                },
                #TODO automise random order
                title="Preferred climate mitigation scenario")


#adjust layout
fig.update_layout(height = 600 ,width=700)


st.plotly_chart(fig, theme="streamlit")