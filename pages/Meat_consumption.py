#Import libraries
import streamlit as st
#import pyam
import plotly.express as px
import streamlit_survey as ss
import pandas as pd
from shillelagh.backends.apsw.db import connect

#connect google sheet
'''connection = connect(":memory:",
                     adapter_kwargs = {
                            "gsheetsapi": { 
                            "service_account_info":  st.secrets["gcp_service_account"] 
                                    }
                                        }
                        )'''


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



st.markdown('### Feedback survey')



#streamlit_survey package to inlcude survey features

survey = ss.StreamlitSurvey("Survey Example")



survey.radio("Which scenario do you personally find to be more just, based on the graph above?",
             options=["Scenario A", "Scenario B", "Scenario C"], horizontal=True)

survey.text_input("Please briefly explain why you found one scenario to be more just compared to the other and if possible explain which concept of justice did you apply to derive your answer.")

json = survey.to_json()
survey_df = pd.read_json(json)

st.write(survey_df)
'''Possible workflow: Store data as JSON -> convert to dataframe -> append to google sheet'''

#TODO: find way to save data
#Google sheets: https://medium.com/nyu-ds-review/how-to-create-a-python-web-app-to-securely-collect-and-store-user-information-cb8f36921988
#https://medium.com/@jb.ranchana/write-and-append-dataframes-to-google-sheets-in-python-f62479460cf0
#trubrics: https://trubrics.github.io/trubrics-sdk/streamlit/
##account: inclisa@inclisa.iam.gserviceaccount.com
