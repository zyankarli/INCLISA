#-------------------------#
#        LIBRARIES        #
#-------------------------#
import streamlit as st
#to import pictures, use Python Imaging Library
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from shillelagh.backends.apsw.db import connect
from google.oauth2 import service_account
import time
from PIL import Image
import random
#------------------------------------------------------------------------------#

#-------------------------#
#      CONFIGURATIONS     #
#-------------------------#
#set page configs
st.set_page_config(
     layout="wide",
     page_title='Justice in climate mitigation scenarios',
     initial_sidebar_state="collapsed",
     #page_icon=Image.open("pages/IIASA_PNG logo-short_blue.png")
)
#hide menu and footer
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       header {visibility: hidden;}
       </style>
       """
#st.markdown(hide_default_format, unsafe_allow_html=True)

#hide fullscreen button for plots
hide_img_fs = '''
<style>
button[title="View fullscreen"]{
    visibility: hidden;}
</style>
'''
st.markdown(hide_img_fs, unsafe_allow_html=True)
#------------------------------------------------------------------------------#

#-------------------------#
#        LOAD DATA        #
#-------------------------#
#Data loading and wrangling
#@st.cache_data
def load_csv():
    df = pd.DataFrame(pd.read_csv(r"https://raw.githubusercontent.com/zyankarli/INCLISA/main/pages/output.csv",
                                    sep=","
                                    ))
    return df
df = load_csv()
#------------------------------------------------------------------------------#

#-------------------------#
#       WRANGLE DATA      #
#-------------------------#

#rename columns
df.rename(columns = {'region': "Region",
                      'value':"Value",
                      "year":'Year',
                      'scenario':"scen_id"}, inplace=True)


#annonymise scenario names
df["Scenario"] = df["scen_id"]
#utilitarian = circle
df.loc[df["Scenario"].str.contains("agg"), "Scenario"] = "Scenario \u25B2"
#egalitarian = square
df.loc[df["Scenario"].str.contains("ega"), "Scenario"] = "Scenario \u25A0"
#prioritarian = diamond
df.loc[df["Scenario"].str.contains("pri"), "Scenario"] = "Scenario \u25C6"
#sufficitarian = horizontal bar
df.loc[df["Scenario"].str.contains("suf"), "Scenario"] = "Scenario \u25AC"
#limitarian = vertical bar
df.loc[df["Scenario"].str.contains("lim"), "Scenario"] = "Scenario \u275A"

#Randomisation of i) graph order ii) radio order
#set seed for session state on current time
#without this if statement, the seed would reset every time the page is reloaded, which prevents storing the survey in the google sheet
if 'rs' not in st.session_state:
    st.session_state['rs'] = random.randint(1, 10000)

#randomise order scenarios are displayed
def random_scenario_order():
    random.seed(st.session_state['rs'])
    scenario_list = ["Scenario \u25B2", "Scenario \u25A0", "Scenario \u25C6", "Scenario \u25AC", "Scenario \u275A"]
    scenario_list_nutr = random.sample(scenario_list, len(scenario_list))
    scenario_list_tran = random.sample(scenario_list, len(scenario_list))
    scenario_list_buil = random.sample(scenario_list, len(scenario_list))
    scenario_list_gdp = random.sample(scenario_list, len(scenario_list))
    return scenario_list_nutr, scenario_list_tran, scenario_list_buil, scenario_list_gdp

scenario_list_nutr, scenario_list_tran, scenario_list_buil, scenario_list_gdp = random_scenario_order()

#change values to int
df["Year"] = df['Year'].astype(int)
df["Value"] = df["Value"].astype(int)

#standardise country names
country_conversion = {"Countries of Latin America and the Caribbean" : "Latin America",
    "Countries of South Asia; primarily India":"India+",
    "Countries of Sub-Saharan Africa":"Africa",
    "Countries of centrally-planned Asia; primarily China":"China+",
    "Countries of the Middle East; Iran, Iraq, Israel, Saudi Arabia, Qatar, etc.": "Middle East",
    "Eastern and Western Europe (i.e., the EU28)":"Europe",
    "North America; primarily the United States of America and Canada": "North America",
    "Pacific OECD":"Pacific OECD",
    "Reforming Economies of Eastern Europe and the Former Soviet Union; primarily Russia": "Reformed Economies"
}
df=df.replace({"Region": country_conversion })
#------------------------------------------------------------------------------#

#-------------------------#
#       PLOT SETTINGS     #
#-------------------------#

#map colors to regions
colors_dict = pd.DataFrame({"Region": pd.unique(df["Region"])})
colors_dict["Color"] = pd.Series(px.colors.qualitative.T10[:(len(colors_dict)+1)])
colors_dict = colors_dict.set_index("Region")["Color"].to_dict()

##Layout
#Legend horizontal
legend_dic_hor = dict(
    orientation="h",
    #entrywidth=10,
    #entrywidthmode='fraction',
    yanchor="bottom",
    y=-0.3,
    xanchor="right",
    x=0.9,
    bgcolor="White",
    bordercolor="Black",
    borderwidth=1
    )
legend_dic_ver = dict(
    #orientation="h",
    #entrywidth=10,
    title_text = "Legend",
    entrywidthmode='fraction',
    yanchor="bottom",
    y=0.3,
    xanchor="right",
    x=1.6,
    bgcolor="White",
    bordercolor="Black",
    borderwidth=1,
    font = dict(
        size = 18
    ))
#set legend layout
legend_dic = legend_dic_hor
#Size
plot_width=800 
plot_height= plot_width * 0.75 
#Deactivate zoom/ True = deactivated
x_axis_zoom = True
y_axis_zoom = True
#Hover data
hover_dic = {
    "Region": False, 
    "Scenario": False,
    "Year": False,
    "Value": False
}
global_hover_name = "Region"
#xaxis ticks
global_xticks = dict(tickangle=-45, automargin=True,
                     tickvals = [2030, 2040, 2050])
#annotations
global_annotation = dict(
    xref="paper", yref="paper",
    x=-.05, y=-0.1, text="2020", showarrow=False)
#------------------------------------------------------------------------------#

#-------------------------#
#           PLOTS         #
#-------------------------#
#for phone applications: https://towardsdatascience.com/mobile-first-visualization-b64a6745e9fd

#----GDP----#
#HIGH THRESHOLD
gdp_high = px.line(df[df["scen_id"].str.contains("gdp") & df["scen_id"].str.contains("high")], x='Year', y="Value", color="Region", facet_col='Scenario',
                labels={
                     "Value": "GDP per capita per year",
                     "Year" : ""
                },
                category_orders={"Scenario": scenario_list_gdp,
                                 "Region": sorted(pd.unique(df["Region"]))},
                title="Economic activity trajectories",
                range_x=[2020, 2050],
                range_y=[0, 70000],
                color_discrete_map=colors_dict,
                hover_data=hover_dic,
                hover_name=global_hover_name
                )

gdp_high.add_hline(y=28000,
              annotation_text="",
              annotation_position="bottom left",
              line_dash="dot")

#LOW THRESHOLD
gdp_low = px.line(df[df["scen_id"].str.contains("gdp") & df["scen_id"].str.contains("low")], x='Year', y="Value", color="Region", facet_col='Scenario',
                labels={
                     "Value": "GDP per capita per year",
                     "Year" : ""
                },
                category_orders={"Scenario": scenario_list_gdp,
                                 "Region": sorted(pd.unique(df["Region"]))},
                title="Economic activity scenarios",
                range_x=[2020, 2050],
                range_y=[0, 70000],
                color_discrete_map=colors_dict,
                hover_data=hover_dic,
                hover_name=global_hover_name
                )

gdp_low.add_hline(y=20000,
              annotation_text="",
              annotation_position="bottom left",
              line_dash="dot")

#----MOBILITY----#
#HIGH TRESHOLD
mob_high = px.line(df[df["scen_id"].str.contains("transport") & df["scen_id"].str.contains("high")], x='Year', y="Value", color="Region", facet_col='Scenario',
                labels={
                     "Value": "passenger km per capita per year",
                     "Year" : ""
                },
                category_orders={"Scenario": scenario_list_tran,
                                 "Region": sorted(pd.unique(df["Region"]))},
                title="Mobility scenarios",
                range_x=[2020, 2050],
                range_y=[0, 12000],
                color_discrete_map=colors_dict,
                hover_data=hover_dic,
                hover_name=global_hover_name
                )

mob_high.add_hline(y=8000,
              annotation_text="",
              annotation_position="bottom left",
              line_dash="dot")

#LOW TRESHOLD
mob_low = px.line(df[df["scen_id"].str.contains("transport") & df["scen_id"].str.contains("low")], x='Year', y="Value", color="Region", facet_col='Scenario',
                labels={
                     "Value": "passenger km per capita per year",
                     "Year" : ""
                },
                category_orders={"Scenario": scenario_list_tran,
                                 "Region": sorted(pd.unique(df["Region"]))},
                title="Mobility scenarios",
                range_x=[2020, 2050],
                range_y=[0, 12000],
                color_discrete_map=colors_dict,
                hover_data=hover_dic,
                hover_name=global_hover_name
                )

mob_low.add_hline(y=3500,
              annotation_text="",
              annotation_position="bottom left",
              line_dash="dot")

#----HOUSING----#
#HIGH THRESHOLD
hou_high = px.line(df[df["scen_id"].str.contains("building") & df["scen_id"].str.contains("high")], x='Year', y="Value", color="Region", facet_col='Scenario',
                labels={
                     "Value": "floorspace (m²) per capita per year",
                     "Year" : ""
                },
                category_orders={"Scenario": scenario_list_buil,
                                 "Region": sorted(pd.unique(df["Region"]))},
                title="Housing scenarios",
                range_x=[2020, 2050],
                range_y=[0, 115],
                color_discrete_map=colors_dict,
                hover_data=hover_dic,
                hover_name=global_hover_name
                )

hou_high.add_hline(y=45,
              annotation_text="",
              annotation_position="bottom left",
              line_dash="dot")

#LOW THRESHOLD
hou_low = px.line(df[df["scen_id"].str.contains("building") & df["scen_id"].str.contains("low")], x='Year', y="Value", color="Region", facet_col='Scenario',
                labels={
                     "Value": "floorspace (m²) per capita per year",
                     "Year" : ""
                },
                category_orders={"Scenario": scenario_list_buil,
                                 "Region": sorted(pd.unique(df["Region"]))},
                title="Housing scenarios",
                range_x=[2020, 2050],
                range_y=[0, 115],
                color_discrete_map=colors_dict,
                hover_data=hover_dic,
                hover_name=global_hover_name
                )

hou_low.add_hline(y=10,
              annotation_text="",
              annotation_position="bottom left",
              line_dash="dot")

#----NUTRITION----#
nut = px.line(df[df["scen_id"].str.contains("nutrition")], x='Year', y="Value", color="Region", facet_col='Scenario',
                labels={
                     "Value": "kCal per capita/day",
                     "Year" : ""
                },
                #automise random order
                category_orders={"Scenario": scenario_list_nutr,
                                 "Region": sorted(pd.unique(df["Region"]))},
                title="Meat consumption scenarios",
                range_x=[2018, 2050],
                range_y=[0, 700],
                color_discrete_map=colors_dict,
                hover_data=hover_dic,
                hover_name=global_hover_name
                )

# Add Lancet Healthy Diet
nut.add_hline(y=90,
               annotation_text="",
               annotation_position="bottom left",
               line_dash="dot")


#LAYOUT UPDATES
#get list of all plots defined above
plots = [gdp_high, gdp_low, mob_high, mob_low, hou_high, hou_low, nut]
#set font sizes
font_size_title = 24
font_size_axis = 18
font_size_legend = 14
font_size_subheadings = 18
#add legends
layout_settings = {   
    'legend': legend_dic,
    'autosize': True,
    'title': {'font': {'size': font_size_title}},
    'xaxis': {'title': {'font': {'size': font_size_axis}}},
    'yaxis': {'title': {'font': {'size': font_size_axis}}},
    'height': plot_height
}
# Function to apply layout settings to a plot
def apply_layout_settings(plot):
    updated_plot = plot.update_layout(**layout_settings)
    updated_plot.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    updated_plot.update_annotations(font_size=font_size_subheadings)
    updated_plot.update_xaxes(global_xticks)
    updated_plot.layout.xaxis.fixedrange = x_axis_zoom
    updated_plot.layout.yaxis.fixedrange = y_axis_zoom
    updated_plot.add_annotation(global_annotation)
    return updated_plot

#apply layout settings to all plots
updated_plots = [apply_layout_settings(plot) for plot in plots]

#set plotly configuarations
config = {'displayModeBar': False}


#------------------------------------------------------------------------------#

#-------------------------#
# GOOGLE SHEET CONNECTION #
#-------------------------#

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
#------------------------------------------------------------------------------#

#-------------------------#
#    SURVEY PREPARATION   #
#-------------------------#
#load country data function
#to load country for dropdown menu
@st.cache_data
def load_countries():
    #load data from github
    df = pd.read_csv("https://raw.githubusercontent.com/OxfordEconomics/CountryLists/master/countryList-UN.csv", 
                                lineterminator='\n',skiprows=0, encoding="latin")
    #limit df to first column in case csv file changes
    df = df.iloc[:,0]
    return df
country_list = ["-"] + list(load_countries())

list_of_regions = [
     "-",
    "Countries of Latin America and the Caribbean",
    "Countries of South Asia",
    "Countries of Sub-Saharan Africa",
    "Countries of Central Asia",
    "Countries of the Middle East",
    "The EU28",
    "North America",
    "Pacific OECD",
    "Countries of Eastern Europe and the Former Soviet Union"]

#prepare repeating questions
accepted_answers = ["Scenario \u2BC3", "Scenario \u25A0", "Scenario \u25C6"]
accepted_answers2 =["I think it is important for everyone to be above a certain threshold.",
                    "I think it is important to have a limit for consumption.",
                    "I think it is important that everyone can increase consumption",
                    "I think it is important that consumption converges.",
                    "I think it is important that lower consumption groups increase their consumption.",
                    "I think it is important that the resources should go to who would get most use out of them.",
                    "Other"]
#------------------------------------------------------------------------------#

#-------------------------#
#          FORM           #
#-------------------------#

#set font size for normal text
font_size = "20px"

with st.form("Survey"):

    #MEAT CONSUMPTION
    coll, colm, colr = st.columns([0.4, 0.6, 0.4])
    with colm:
        st.markdown('# Justice in climate mitigation scenarios')

    #INTRODUCTION
        st.markdown(f"""<p style="font-size:{font_size};">
                    Climate justice is about much more than CO2 emissions. At its core, it is a question of how we use and distribute energy in a fair manner.
                    Here, we focus on fair global distributions of energy for basic energy services: food, mobility, housing and economic activities.
                    Unfortunately, it is not always clear what a "fair" distribution would look like. Let's explore this question together!      
                    </p>""", unsafe_allow_html=True)

        #ECONOMIC ACTIVITY
        #High Threshold
        st.markdown("### Economic Activity")
        st.markdown(f"""<p style="font-size:{font_size};">Despite being contested, the gross domestic product (GDP) is universally used as an indicator for economic performance.</p>""", unsafe_allow_html=True)
        st.markdown(f"""<p style="font-size:{font_size};"> Below, we present future GDP trajectories across different world regions.  
                    GDP per capita is used to assess the economic activity of a country in relation to its population.  
                    In climate scenarios, GDP per capita is an important indicator for estimating energy demand and supply.  
                    The dashed line displays the <b> average GPD per capita across the world </b> according to the udpated projections of SSP1. <br>
                    MORE NARRATIVE <br> 
                    This average GDP per capita is projected to be around 28.000 USD per person per year.</p>""", unsafe_allow_html=True)  
        st.markdown(f"""<p style="font-size:{font_size};"><i>Please assume that all scenarios below reach the same climate mitigation goal of 1.5°C.<i> <br>
                Please also note that feasibility and trade-off concerns (e.g. high levels of negative emissions) associated with growth scenarios are outside the scope of this study.</p>""", unsafe_allow_html=True)
        #Graph
        st.plotly_chart(gdp_high, theme="streamlit", config=config, use_container_width=True)
        #Questions
        q1 = st.radio("Which scenario do you personally find to be the fairest, based on the graph above?", ["-"] + scenario_list_gdp,horizontal=True ,
                        key=1)
        q2 = st.text_input("Why do you find this scenario to be the fairest?", placeholder="Please enter your answer here", 
                            key=2)
        q3 = st.selectbox("Which of the following aspects does best describe your main reason for your scenario selection?", ["-"] + accepted_answers2,
                        key=3)
        #Low Threshold
        st.markdown("<br> <br>",unsafe_allow_html=True)
        st.markdown(f"""<p style="font-size:{font_size};"> Let's now assume a different future! 
                    The dashed line displays the <b> average GPD per capita across the world </b> according to a apparent decoupling of the human development index (HDI) and GDP. <br>
                    MORE NARRATIVE <br> 
                    This average GDP per capita is projected to be around 20.000 USD per person per year.</p>""", unsafe_allow_html=True)          
        st.plotly_chart(gdp_low, theme="streamlit", config=config, use_container_width=True) #Graph
        #Questions
        q4 = st.radio("Which scenario do you personally find to be the fairest, based on the graph above?", ["-"] + scenario_list_gdp,horizontal=True ,
                        key=4)
        q5 = st.text_input("Why do you find this scenario to be the fairest?", placeholder="Please enter your answer here", 
                            key=5)
        q6 = st.selectbox("Which of the following aspects does best describe your main reason for your scenario selection?", ["-"] + accepted_answers2,
                        key=6)
        st.markdown("""---""")

        #MOBILITY
        #High Threshold
        st.markdown("### Mobility")
        st.markdown(f"""<p style="font-size:{font_size};">Mobility is important for a good standard of living as it allows the connection of people and markets, thereby enabling access to services and economic opportunities.  
                    However, the current mobility system has significant negative effects on human health and the environment. 
                    The mobility sector is a major contributor to global greenhouse gas emissions, while air and noise pollution further affect local populations. 
                    Moreover, mobility infrastructure is artificially dividing natural habitats and thereby damaging ecosystems.</p>""", unsafe_allow_html=True)
        st.markdown(f"""<p style="font-size:{font_size};">Below, we present future trajectories for mobility across different world regions.  
                    Mobility is assessed using <b>passenger kilometers per year</b>,  which includes all modes of transport except air travel.  
                    This indicator provides insights into the overall level of mobility within a population or region and is used to estimate energy consumption and environmental impacts in climate scenarios.  
                    To provide a benchmark, the dashed line refers to the <b>Japanese mobility system</b>, which is often considered an efficient and effective role model. 
                    The average Japanese individual travels approximately  22km per day (8.000km per year), which is approximately the distance from the Cologne Bonn Airport to the World Conference Center (27km).</p>""", unsafe_allow_html=True)  
        st.markdown(f"""<p style="font-size:{font_size};"><i>Please assume that all scenarios below reach the same climate mitigation goal of 1.5°C.<i> <br>
                Please also note that feasibility and trade-off concerns (e.g. high levels of negative emissions) associated with growth scenarios are outside the scope of this study.</p>""", unsafe_allow_html=True)
                    
        #Graph
        st.plotly_chart(mob_high, theme="streamlit", config=config, use_container_width=True)
        #Questions
        q7 = st.radio("Which scenario do you personally find to be the fairest, based on the graph above?", ["-"] + scenario_list_tran,horizontal=True,
            key=7)
        q8 = st.text_input("Why do you find this scenario to be the fairest?", placeholder="Please enter your answer here",
            key=8)
        q9 = st.selectbox("Which of the following aspects does best describe your main reason for your scenario selection?", ["-"] + accepted_answers2,
            key=9)
        #Low Threshold
        st.markdown("<br> <br>",unsafe_allow_html=True)
        st.markdown(f"""<p style="font-size:{font_size};"> Let's now assume a different future! 
            The dashed line displays the <b> definition dashed line </b> according to <br>
            MORE NARRATIVE <br> 
            This average pkm per capita per year is estimated to be around 3.500.</p>""", unsafe_allow_html=True)          
        st.plotly_chart(mob_low, theme="streamlit", config=config, use_container_width=True)  # Graph
        #Questions
        q10 = st.radio("Which scenario do you personally find to be the fairest, based on the graph above?", ["-"] + scenario_list_gdp,horizontal=True ,
            key=10)
        q11 = st.text_input("Why do you find this scenario to be the fairest?", placeholder="Please enter your answer here", 
                key=11)
        q12 = st.selectbox("Which of the following aspects does best describe your main reason for your scenario selection?", ["-"] + accepted_answers2,
            key=12)     

        st.markdown("""---""")

        #HOUSING
        #High Treshold
        st.markdown("### Housing")
        st.markdown(f"""<p style="font-size:{font_size};">Housing is a central factor for a persons living conditions, but it also has a significant environmental impact.  
        Aside from the land used for construction and the resources consumed during construction, housing requires a large amounts of energy for heating, cooling, and cooking.</p>""", unsafe_allow_html=True)
        st.markdown(f"""<p style="font-size:{font_size};">Below, we present future trajectories for housing across different world regions.  
        <b>Floor space per capita</b> is used to assess the level of living or working space available to individuals.  
        In climate scenarios, this indicator helps calculate heating and cooling needs, which are essential for determining energy demands. 
        The dashed line symbolizes a floor space of 45m² (or 480ft²) per person, which is the <b>estimated average of floor space</b> per person across European countries in 2014. 
                    This is approximately the area covered by 5 average cars.</p>""", unsafe_allow_html=True)  
        st.markdown(f"""<p style="font-size:{font_size};"><i>Please assume that all scenarios below reach the same climate mitigation goal of 1.5°C.<i> <br>
                Please also note that feasibility and trade-off concerns (e.g. high levels of negative emissions) associated with growth scenarios are outside the scope of this study.</p>""", unsafe_allow_html=True)
        #Graph
        st.plotly_chart(hou_high, theme="streamlit", config=config, use_container_width=True)
        #Questions
        q13 = st.radio("Which scenario do you personally find to be the fairest, based on the graph above?", ["-"] + scenario_list_buil,horizontal=True ,
                key=13)
        q14 = st.text_input("Why do you find this scenario to be the fairest?", placeholder="Please enter your answer here",
                key=14)
        q15 = st.selectbox("Which of the following aspects does best describe your main reason for your scenario selection?", ["-"] + accepted_answers2,
                key=15)
        #Low Threshold
        st.markdown("<br> <br>",unsafe_allow_html=True)
        st.markdown(f"""<p style="font-size:{font_size};"> Let's now assume a different future! 
                The dashed line displays the <b> definition dashed line </b> according to <br>
                MORE NARRATIVE <br> 
                This average pkm per capita per year is estimated to be around 3.500.</p>""", unsafe_allow_html=True)          
        st.plotly_chart(hou_low, theme="streamlit", config=config, use_container_width=True)   
        #Questions
        q16 = st.radio("Which scenario do you personally find to be the fairest, based on the graph above?", ["-"] + scenario_list_gdp,horizontal=True ,
                key=16)
        q17 = st.text_input("Why do you find this scenario to be the fairest?", placeholder="Please enter your answer here", 
                    key=17)
        q18 = st.selectbox("Which of the following aspects does best describe your main reason for your scenario selection?", ["-"] + accepted_answers2,
                key=18)
        st.markdown("""---""")

        #NUTRITION
        st.markdown('### Nutrition')
        
        st.markdown(f"""<p style="font-size:{font_size};">A balanced diet is crucial for human health and involves consuming a variety of fruits, vegetables, nuts, and animal products.  
                        Meat production has many environmental impacts and requires a lot of resources compared to plant-based foods. Raising animals for meat requires large amounts of land, water, and feed. 
                        The production of feed for livestock, like soy and corn, often involves deforestation and the use of fertilizers, which contribute to greenhouse gas emissions. 
                        Moreover, certain animals produce methane, a potent greenhouse gas, during their digestive process.</p>""", unsafe_allow_html=True)
        
        st.markdown(f"""<p style="font-size:{font_size};">Below, we present future trajectories for <b> meat consumption </b> across different world regions.  
                Meat consumption is assessed using kilo calories of meat consumption per capita per day.  
                The EAT-Lancet Commission recommends that a <b>healthy diet</b> includes approximately 90cKal (or 85g) of meat per day, which is represented as dashed line. This quantity is equivalent to a piece of meat about the size of the palm of your hand.</p>""", unsafe_allow_html=True)
        
        st.markdown(f"""<p style="font-size:{font_size};"><i>Please assume that all scenarios below reach the same climate mitigation goal of 1.5°C.<i> <br>
                Please also note that feasibility and trade-off concerns (e.g. high levels of negative emissions) associated with growth scenarios are outside the scope of this study.</p>""", unsafe_allow_html=True)
        #Graph
        st.plotly_chart(nut, theme="streamlit", config=config, use_container_width=True)
        #Questions
        q19 = st.radio("Which scenario do you personally find to be the fairest, based on the graph above?", ["-"] + scenario_list_nutr, horizontal=True ,
                    key=19)
        q20 = st.text_input("Why do you find this scenario to be the fairest?", placeholder="Please enter your answer here",
                    key=20)
        q21 = st.selectbox("Which of the following aspects does best describe your main reason for your scenario selection?", ["-"] + accepted_answers2,
                    key=21 )
        st.markdown("""---""")

        #PERSONAL QUESTIONS
        st.markdown('### Personal Questions')
        q22 = st.selectbox("How knowledgeable are you about Integrated Assessment Models used for climate mitigation scenarios?",
                ("-", "No prior experience", "Experience in the context of reports such as IPCC", "Occasional user of scenario outputs", "Expert level"),
                key=22)
        q23=st.selectbox("How often per week do you eat meat?",
                    ("-", "Never", "Once per week or less", "At least 3 times per week", "Everyday"), 
                    key=23)
        q24=st.selectbox("How often per year do you travel by plane?",#
                    ("-", "Never", "Once per year", "3 times per year", "At least 5 times per year"), 
                    key=24)
        q25=st.selectbox("What is the size of your apartment/ house?",
                    ("-", "Less than 10m² per person", "Between 10m² and 30m² per person","Between 30m² and 50m² per person","More than 50m² per person" ), 
                    key=25)
        q26 = st.selectbox("Which region are you from? (Please select the region you feel closer to and more knowledgeable about)",
                list_of_regions, 
                key=26)
        q27 = st.selectbox("What type of organisation do you work for?", 
                ("-", "Government", "Research or academic organisation", "Non-governmental organisation", "Interational organisation", "Private Sector", "Other"), 
                key=27)
        #TODO: add conditional pop-up for st text with other
        q28 = st.selectbox("What is the highest level of education you have completed?",
                ("-", 'No degree', 'High school diploma (or equivalent)', 'Some college', 'Professional degree', "Bachelor's degree", "Master's degree", "Doctoral degree"),
                key=28)
        q29 = st. selectbox("What is your age?",
                ("-", "18-24", '25-34','35-44','45-54','55-64','65-100'), 
                key=29)
        q30 = st.selectbox("What is your gender?",
                ("-", "Male", "Female", "Other", "Prefer not to say"), 
                key=30)
        q31 = st.selectbox("To which sector is your work most related to?",
                ("-", "Agriculture/Food/Land Management", "Industry/Manufacturing", "Transport/Shipping/Public Transportation", "Buildings/Housing/Construction", "Climate mitigation/ adapdation", "Other"), 
                key=31)
        timestamp = time.time()
    #Submit button; send data to google sheet
        submitted = st.form_submit_button("Click here to submit!")
        if submitted:
            cursor = create_connection()
            query = f'INSERT INTO "{sheet_url}" VALUE ("{q1}", "{q2}", "{q3}", "{q4}", "{q5}", "{q6}", "{q7}", "{q8}", "{q9}", "{q10}","{q11}","{q12}","{q13}","{q14}","{q15}","{q16}","{q17}","{q18}","{q19}","{q20}","{q21}","{q22}","{q23}","{q24}","{q25}","{q26}","{q27}","{q28}","{q29}","{q30}","{q31}", "{timestamp}")'
            cursor.execute(query)
            st.write("**:green[Submission successful. Thank you for your input!]**")
            st.toast("**:green[Submission successful!]**", icon=None)

