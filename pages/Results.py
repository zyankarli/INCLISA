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
    #page_icon=Image.open("pages/IIASA_PNG logo-short_blue.png")
    #local
    #page_icon = Image.open(r'C:\Users\scheifinger\Documents\GitHub\INCLISA\pages\IIASA_PNG logo-short_blue.png')
)

#hide menu and footer
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       header {visibility: hidden;}
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
def wrangle_data(): #TODO: for each session state, only keep the row with highest timestamp
    df = pd.DataFrame(run_query(f'SELECT * FROM "{sheet_url}"'))
#rename columns
    df.columns= [
         'session_state',
         'gdp_high_scenario', 'gdp_high_feedback', 'gdp_high_motivation', 
         'gdp_low_scenario', 'gdp_low_feedback', 'gdp_low_motivation', 
         'mob_high_scenario', 'mob_high_feedback', 'mob_high_motivation',
         'mob_low_scenario', 'mob_low_feedback', 'mob_low_motivation',
         'hou_high_scenario', 'hou_high_feedback', 'hou_high_motivation',
         'hou_low_scenario', 'hou_low_feedback', 'hou_low_motivation',
         'nut_high_scenario', 'nut_high_feedback', 'nut_high_motivation',
         'nut_low_scenario', 'nut_low_feedback', 'nut_low_motivation',
         'IAM_expertise', 'meat_consumption', 'air_travel', 'housing_space',
         'region', 'organisation', 'education', 'age',
         'gender', 'sector', 'gdp_threshold', 'mob_threshold', 'hou_threshold', 'nut_threshold','timestamp']
    #drop all data points that are not from today    
    today = datetime.now().date()
    df['date'] = df['timestamp'].apply(datetime.fromtimestamp).apply(datetime.date)
    to_plot = df[df['date'] == today]

    #if there are multiple data points with same session_state, only keep the one with highest timestamp
    to_plot = to_plot.sort_values(by=['timestamp'], ascending=False).drop_duplicates(subset=['session_state'])

    #DATA FOR FIGURE 1 = scenarios for each sector
    #select relevant columns
    #get all columns with the string "scenario" in it and the column timestamp
    to_plot_scen = to_plot.filter(regex='scenario|timestamp|session_state') 

    #put columns with same suffix into one column, e.g. gdp_high_scenario and gdp_low_scenario into gdp_scenario
    to_plot_scen = pd.wide_to_long(to_plot_scen,
                                      stubnames=['gdp', 'mob', 'hou', 'nut'],
                                      i = ['timestamp', 'session_state'],
                                      j = "Sector",
                                      sep="_",
                                      suffix='.+'
                                      )
    
    st.write(to_plot_scen)
    #to_plot_scen = to_plot[['gdp_high_scenario', 'mob_high_scenario', 'hou_high_scenario', 'nut_scenario']]
    #rename scenarios
    to_plot_scen = to_plot_scen.rename(columns={'nut':"Nutrition",
                                      'mob':"Mobility",
                                      'hou':'Housing',
                                      'gdp':"Economic Activity"})
    
    #select only relevant columns    
    to_plot_scen = to_plot_scen[['Economic Activity', 'Mobility', 'Housing', 'Nutrition']]
  
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
    try:
         to_plot_scen.loc[to_plot_scen["Scenario"].str.contains('\u25AC'), "Scenario"] = "Lower limit (\u25AC)"
    except:
        pass
    try:
        to_plot_scen.loc[to_plot_scen["Scenario"].str.contains('\u275A'), "Scenario"] = "Upper limit (\u275A)"
    except:
        pass

    #DATA FOR FIGURE 2 = scenarios for high/ low in facet
    to_plot_thre = to_plot.filter(regex='scenario') 
    #reset index
    to_plot_thre.reset_index(inplace=True)
    #rename columns)
    #put columns with same suffix into one column, e.g. gdp_high_scenario and gdp_low_scenario into gdp_scenario
    to_plot_thre = pd.wide_to_long(to_plot_thre,
                                      stubnames=['gdp', 'mob', 'hou', 'nut'],
                                      i = ['index'],
                                      j = "Threshold",
                                      sep="_",
                                      suffix='.+'
                                      )
    # Reset the index
    to_plot_thre = to_plot_thre.reset_index()

    to_plot_thre = pd.melt(to_plot_thre,
                           id_vars=['index', "Threshold"], 
                           value_vars=['gdp', 'mob', 'hou', 'nut'], 
                           var_name='Sector', value_name='Scenario')

    #to_plot_thre.reset_index(inplace=True)
    #to_plot_thre['Scenario'] = to_plot_thre['Scenario'].apply(lambda x: 'High' if 'high' in x else 'Low')
    
 

    #to_plot_scen = to_plot[['gdp_high_scenario', 'mob_high_scenario', 'hou_high_scenario', 'nut_scenario']]
    #rename scenarios
    # to_plot_thre = to_plot_scen.rename(columns={'nut':"Nutrition",
    #                                   'mob':"Mobility",
    #                                   'hou':'Housing',
    #                                   'gdp':"Economic Activity"})
    
    #select only relevant columns    
    # to_plot_thre = to_plot_thre[['Economic Activity', 'Mobility', 'Housing', 'Nutrition']]
  
    #change wide to long
    # to_plot_thre = pd.melt(to_plot_scen, var_name="Sector", value_name="Scenario")
    #drop "-"
    to_plot_thre = to_plot_thre[to_plot_thre.Scenario != "-"]
    #group by sector and get percentage of each scenario
    to_plot_thre = pd.DataFrame(to_plot_thre.groupby(['Sector', 'Threshold'])['Scenario'].value_counts(normalize=True).round(decimals=2)).reset_index()
    #Rename new column
    to_plot_thre = to_plot_thre.rename(columns={'proportion': "Percentage"})
    #calculate percentage out of proportion
    to_plot_thre["Percentage"] = to_plot_thre["Percentage"] * 100
    #add labels column
    to_plot_thre["Label"] = to_plot_thre["Percentage"].astype(int).astype(str) + "%"
    #rename sector and threshold columns
    to_plot_thre["Sector"] = to_plot_thre["Sector"].replace({"gdp": "Economic Activity", "mob": "Mobility", "hou": "Housing", "nut": "Nutrition"})
    to_plot_thre["Threshold"] = to_plot_thre["Threshold"].replace({"low_scenario": "Low", "high_scenario": "High"})

    #Change scenario names // within try function in case certain scenarios are never picked
    try:
         to_plot_thre.loc[to_plot_thre["Scenario"].str.contains('\u25B2'), "Scenario"] = "Growing consumption (\u25B2)"
    except:
         pass
    try:
        to_plot_thre.loc[to_plot_thre["Scenario"].str.contains('\u25A0'), "Scenario"] = "Convergence (\u25A0)"
    except:
         pass
    try:
        to_plot_thre.loc[to_plot_thre["Scenario"].str.contains('\u25C6'), "Scenario"] = "Catching up (\u25C6)"
    except:
        pass
    try:
         to_plot_thre.loc[to_plot_thre["Scenario"].str.contains('\u25AC'), "Scenario"] = "Lower limit (\u25AC)"
    except:
        pass
    try:
        to_plot_thre.loc[to_plot_thre["Scenario"].str.contains('\u275A'), "Scenario"] = "Upper limit (\u275A)"
    except:
        pass



    #DATA FOR FIGURE 3 = motivations for scenarios
    to_plot_moti = to_plot.filter(regex='scenario|motivation')
    #set index
    to_plot_moti.reset_index(inplace=True)
    
    #for each column with 'scenario' in it
    # I want to change the column name by putting scenario in front of it and
    # get rid of the "scenario at the end of it"
    for col in to_plot_moti.columns:
        if "scenario" in col:
            new_col_name = col.replace("_scenario", "")
            to_plot_moti = to_plot_moti.rename(columns={col: "scenario_"+new_col_name})
        elif "motivation" in col:
            new_col_name = col.replace("_motivation", "")
            to_plot_moti = to_plot_moti.rename(columns={col: "motivation_"+new_col_name})
    
    to_plot_moti = pd.wide_to_long(to_plot_moti,
                                   stubnames=['scenario', 'motivation'],
                                   i = ['index'],
                                   j = "Sector",
                                   sep="_",
                                   suffix='.+'
                                   )
 
    #drop "-"
    to_plot_moti = to_plot_moti[(to_plot_moti.scenario != "-") & (to_plot_moti.motivation != "-")]
    #get values
    to_plot_moti = pd.DataFrame(to_plot_moti.groupby('scenario')['motivation'].value_counts(normalize=True).round(decimals=2)).reset_index() 
    #rename columns
    to_plot_moti = to_plot_moti.rename(columns={
         'scenario' : "Scenario",
         "motivation" : "Reason",
         'proportion': "Percentage"
         })
    # #calculate percentage out of proportion
    to_plot_moti["Percentage"] = to_plot_moti["Percentage"] * 100
    # #add labels column
    to_plot_moti["Label"] = to_plot_moti["Percentage"].astype(int).astype(str) + "%"   


    #substitute Scenario with ['Growing consumption (\u25B2)', "Convergence (\u25A0)", 'Catching up (\u25C6)',  "Lower limit (\u25AC)", "Upper limit (\u275A)"]
    to_plot_moti.loc[to_plot_moti["Scenario"].str.contains('\u25B2'), "Scenario"] = "Growing consumption (\u25B2)"
    to_plot_moti.loc[to_plot_moti["Scenario"].str.contains('\u25A0'), "Scenario"] = "Convergence (\u25A0)"
    to_plot_moti.loc[to_plot_moti["Scenario"].str.contains('\u25C6'), "Scenario"] = "Catching up (\u25C6)"
    to_plot_moti.loc[to_plot_moti["Scenario"].str.contains('\u25AC'), "Scenario"] = "Lower limit (\u25AC)"
    to_plot_moti.loc[to_plot_moti["Scenario"].str.contains('\u275A'), "Scenario"] = "Upper limit (\u275A)"


    #set order of scenarios, same to as just above
    to_plot_moti["Scenario"] = pd.Categorical(to_plot_moti["Scenario"], ["Growing consumption (\u25B2)", "Convergence (\u25A0)", "Catching up (\u25C6)", "Lower limit (\u25AC)", "Upper limit (\u275A)"][::-1])

    return to_plot_scen, to_plot_thre, to_plot_moti


to_plot_scen, to_plot_thre, to_plot_moti = wrangle_data()



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
            title = "What scenarios are preferred in which sector?")

fig2 = px.bar(to_plot_thre, x="Percentage", y='Threshold', color="Scenario", text = "Label",
            #barmode='group',
            labels={
                     'Percentage': "",
                     'Sector':""
                },
            hover_data = {"Scenario": False, "Percentage": False, "Sector":False, "Label":False},
            hover_name="Scenario",
            orientation='h',
            color_discrete_sequence=px.colors.qualitative.Bold,
            title = "Is the threshold relevant?", 
            facet_col="Sector")

fig3 = px.bar(to_plot_moti, x="Percentage", y="Scenario", color="Reason", text="Label",
              labels={
                     'Percentage': "",
                     'Scenario':""
                },
            hover_data = {"Scenario": False, "Percentage": False, "Reason":False, "Label":False},
            hover_name="Reason",
            orientation='h',
            color_discrete_sequence=px.colors.qualitative.Bold,
            title="What is the motivation to pick a certain scenario?",
            #set order for legend
            category_orders= {"Reason" : ["I think it is important for everyone to be above a certain threshold.",
                    "I think it is important to have a limit for consumption.",
                    "I think it is important that everyone can increase consumption",
                    "I think it is important that consumption converges.",
                    "I think it is important that lower consumption groups increase their consumption.",
                    "I think it is important that the resources should go to who would get most use out of them.",
                    "Other"]})

#Set LAYOUTS
#Size
plot_width=600 
plot_height= plot_width * 0.75
#set font sizes
font_size_title = 24
font_size_axis = 18
font_size_legend = 14

#Layouts
fig1.update_layout(
    autosize=True,
    title={'font': {'size': font_size_title}},
    yaxis_tickfont_size=font_size_axis, 
    legend = dict(
        title_text = "Scenario",
        font = dict(size = 18)
        ),
    height = plot_height
    )
fig2.update_layout(
    autosize=True,
    title={'font': {'size': font_size_title}},
    yaxis_tickfont_size=font_size_axis, 
    legend = dict(
        title_text = "Scenario",
        font = dict(size = 18)
        ),
    height = plot_height
    )

fig3.update_layout(
    legend = dict(
        title_text = "Motivation",
        orientation="h",
        # yanchor="bottom",
        # y=-1,
        # xanchor="right",
        # x=1,
        font = dict(size = 18)
        ),
    yaxis_tickfont_size=font_size_axis, 
    yaxis = dict(
        tickmode = 'array',
        #tickvals = ["Scenario \u25B2", "Scenario \u25A0", "Scenario \u25C6", "Scenario \u25AC", "Scenario \u275A"],
        ticktext = ['Growing consumption (\u25B2)', "Convergence (\u25A0)", 'Catching up (\u25C6)',  "Lower limit (\u25AC)", "Upper limit (\u275A)"]
    ),
    width = plot_width,
    height = plot_height)

#Set graph features
#Disable zoom feature
fig1.layout.xaxis.fixedrange = True
fig1.layout.yaxis.fixedrange = True
fig2.layout.xaxis.fixedrange = True
fig2.layout.yaxis.fixedrange = True
fig3.layout.xaxis.fixedrange = True
fig3.layout.yaxis.fixedrange = True
#disable x axis
fig1.update_xaxes(showticklabels=False)
fig2.update_xaxes(showticklabels=False)
fig3.update_xaxes(showticklabels=False)
fig3.update_yaxes(tickfont_color="black")
#size of sub titles
config = {'displayModeBar': False}



#add update layout
fig1.update_layout(
                   autosize=True,
                   title={'font': {'size': font_size_title}},
                   xaxis={'title': {'font': {'size': font_size_axis}}},
                   yaxis={'title': {'font': {'size': font_size_axis}}},  
                #    width=plot_width,
                    height=plot_height
                   )
fig2.update_layout(
                     autosize=True,
                     title={'font': {'size': font_size_title}},
                     xaxis={'title': {'font': {'size': font_size_axis}}},
                     yaxis={'title': {'font': {'size': font_size_axis}}},  
                     height=plot_height
                     ) 
fig2.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))    
fig3.update_layout(
                   autosize=True,
                   title={'font': {'size': font_size_title}},
                   xaxis={'title': {'font': {'size': font_size_axis}}},
                   yaxis={'title': {'font': {'size': font_size_axis}}},
                   height=plot_height)

#Print graph
coll, colm, colr = st.columns([0.2, 0.8, 0.2])
with colm: 
    st.markdown('# Results')
    st.plotly_chart(fig1, theme="streamlit", config=config, use_container_width=True)
    st.plotly_chart(fig2, theme="streamlit", config=config, use_container_width=True)
    st.plotly_chart(fig3, theme="streamlit", config=config, use_container_width=True)

#only reload graph on click
if st.button('Click here to update the graphs.'):
    st.experimental_rerun()




#adjust layout
#inclulde buttons ?https://plotly.com/python/custom-buttons/
