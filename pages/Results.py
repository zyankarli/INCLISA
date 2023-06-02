#Import libraries
import streamlit as st
import pandas as pd
from shillelagh.backends.apsw.db import connect
from google.oauth2 import service_account
import plotly.express as px
from datetime import datetime
from PIL import Image 

st.set_page_config(
    layout="wide",
    page_title='Justice in climate mitigation scenarios',
    initial_sidebar_state="auto",
    #online
    page_icon=Image.open("pages/IIASA_PNG logo-short_blue.png")
    #local
    #page_icon = Image.open(r'C:\Users\scheifinger\Documents\GitHub\INCLISA\pages\IIASA_PNG logo-short_blue.png')
)

#hide menu and footer
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

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
    #drop all data points that are not from today
    today = datetime.now().date()
    df['date'] = df['timestamp'].apply(datetime.fromtimestamp).apply(datetime.date)
    to_plot = df[df['date'] == today]

    #Get data for figure 1 = scenarios
    #select relevant columns
    to_plot_scen = to_plot[['scen_meat', 'scen_tran', 'scen_buil', 'scen_gdp']]
    #rename scenarios
    to_plot_scen = to_plot_scen.rename(columns={'scen_meat':"Nutrition",
                                      'scen_tran':"Mobility",
                                      'scen_buil':'Housing',
                                      'scen_gdp':"Economic Activity"})
    #change wide to long
    to_plot_scen = pd.melt(to_plot_scen, var_name="Sector", value_name="Scenario")
    #drop "-"
    to_plot_scen = to_plot_scen[to_plot_scen.Scenario != "-"]
    #group by sector and get percentage of each scenario
    to_plot_scen = pd.DataFrame(to_plot_scen.groupby('Sector')['Scenario'].value_counts(normalize=True).round(decimals=2)).reset_index()
    #Rename new column
    to_plot_scen = to_plot_scen.rename(columns={'proportion': "Percentage"})
    #calculate percentage out of proportion
    to_plot_scen["Percentage"] = to_plot_scen["Percentage"] * 100
    #add labels column
    to_plot_scen["Label"] = to_plot_scen["Percentage"].astype(int).astype(str) + "%"
    #Change scenario names // within try function in case certain scenarios are never picked
    try:
         to_plot_scen.loc[to_plot_scen["Scenario"].str.contains('\u25B2'), "Scenario"] = "Growing consumption (\u25B2)"
    except:
         pass
    try:
        to_plot_scen.loc[to_plot_scen["Scenario"].str.contains('\u25A0'), "Scenario"] = "Convergence (\u25A0)"
    except:
         pass
    try:
        to_plot_scen.loc[to_plot_scen["Scenario"].str.contains('\u25C6'), "Scenario"] = "Catching up (\u25C6)"
    except:
        pass

    #get data for figure 2 = motivations
    to_plot_moti = to_plot[['scen_meat', 'scen_tran', 'scen_buil', 'scen_gdp'
                            ,"scen_meat_reason", "scen_tran_reason", "scen_buil_reason", "scen_gdp_reason"]]
    #Rename columns
    to_plot_moti = to_plot_moti.rename(columns={'scen_meat_reason':"reason_meat",
                                      'scen_tran_reason':"reason_tran",
                                      'scen_buil_reason':'reason_buil',
                                      'scen_gdp_reason':"reason_gdp"})
    #change wide to long
    to_plot_moti.reset_index(inplace=True)
    to_plot_moti = pd.wide_to_long(to_plot_moti,
                                   stubnames=['scen', 'reason'],
                                   i = ['index'],
                                   j = "Sector",
                                   sep="_",
                                   suffix='.+'
                                   )
    #drop "-"
    to_plot_moti = to_plot_moti[(to_plot_moti.scen != "-") & (to_plot_moti.reason != "-")]
    #get values
    to_plot_moti = pd.DataFrame(to_plot_moti.groupby('scen')['reason'].value_counts(normalize=True).round(decimals=2)).reset_index()
     #Rename new column
    to_plot_moti = to_plot_moti.rename(columns={
         'scen' : "Scenario",
         "reason" : "Reason",
         'proportion': "Percentage"
         })
    #calculate percentage out of proportion
    to_plot_moti["Percentage"] = to_plot_moti["Percentage"] * 100
    #add labels column
    to_plot_moti["Label"] = to_plot_moti["Percentage"].astype(int).astype(str) + "%"

    return to_plot_scen, to_plot_moti


to_plot_scen, to_plot_moti = wrangle_data()



#Create PLOTS
fig1 = px.bar(to_plot_scen, x="Percentage", y='Sector', color="Scenario", text = "Label",
            labels={
                     'Percentage': "",
                     'Sector':""
                },
            hover_data = {"Scenario": False, "Percentage": False, "Sector":False, "Label":False},
            hover_name="Scenario",
            orientation='h',
            color_discrete_sequence=px.colors.qualitative.Bold,
            title = "Scenario per sector")

fig2 = px.bar(to_plot_moti, x="Percentage", y="Scenario", color="Reason", text="Label",
              labels={
                     'Percentage': "",
                     'Scenario':""
                },
            hover_data = {"Scenario": False, "Percentage": False, "Reason":False, "Label":False},
            hover_name="Reason",
            orientation='h',
            color_discrete_sequence=px.colors.qualitative.Bold,
            title="Motivation for scenarios")


#Set LAYOUTS
#Size
plot_width=600 
plot_height= plot_width * 0.75 
#Layout
fig1.update_layout(
    legend = dict(
        title_text = "Scenario",
        ),
    width = plot_width,
    height = plot_height
    )

#Layout
fig2.update_layout(
    legend = dict(
        title_text = "Motivation",
        orientation="h",
        yanchor="bottom",
        y=-.32,
        xanchor="right",
        x=1
        ),
    yaxis = dict(
        tickmode = 'array',
        tickvals = ["Scenario \u25B2", "Scenario \u25A0", "Scenario \u25C6"],
        ticktext = ['Growing consumption (\u25B2)', "Convergence (\u25A0)", 'Catching up (\u25C6)']
    ),
    width = plot_width,
    height = plot_height)

fig2.update_yaxes(tickfont_color="black")
#Set graph features
#Disable zoom feature
fig1.layout.xaxis.fixedrange = True
fig1.layout.yaxis.fixedrange = True
fig2.layout.xaxis.fixedrange = True
fig2.layout.yaxis.fixedrange = True
#disable x axis
fig1.update_xaxes(showticklabels=False)
fig2.update_xaxes(showticklabels=False)



st.markdown('# Survey Results')
#Print graph
st.plotly_chart(fig1, theme="streamlit")

st.plotly_chart(fig2, theme="streamlit")

#only reload graph on click
if st.button('Click here to update the graph.'):
    st.experimental_rerun()





#adjust layout
#inclulde buttons ?https://plotly.com/python/custom-buttons/
