#-------------------------#
#        LIBRARIES        #
#-------------------------#
import streamlit as st
#to import pictures, use Python Imaging Library
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
#from shillelagh.backends.apsw.db import connect
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
df.loc[df["Scenario"].str.contains("agg"), "Scenario"] = "\u25B2"
#egalitarian = square
df.loc[df["Scenario"].str.contains("ega"), "Scenario"] = "\u25A0"
#prioritarian = diamond
df.loc[df["Scenario"].str.contains("pri"), "Scenario"] = "\u25C6"
#sufficitarian = horizontal bar
df.loc[df["Scenario"].str.contains("suf"), "Scenario"] = "\u25AC"
#limitarian = vertical bar
df.loc[df["Scenario"].str.contains("lim"), "Scenario"] = "\u275A"

#Randomisation of i) graph order ii) radio order
#set seed for session state on current time
#without this if statement, the seed would reset every time the page is reloaded, which prevents storing the survey in the google sheet
if 'rs' not in st.session_state:
    st.session_state['rs'] = random.randint(1, 10000)

#randomise order scenarios are displayed
def random_scenario_order():
    random.seed(st.session_state['rs'])
    scenario_list = ["\u25B2", "\u25A0", "\u25C6", "\u25AC", "\u275A"]
    #randomise order for each plot in plots
    scenario_list_gdp_high = random.sample(scenario_list, len(scenario_list))
    scenario_list_gdp_low = random.sample(scenario_list, len(scenario_list))
    scenario_list_mob_high = random.sample(scenario_list, len(scenario_list))
    scenario_list_mob_low = random.sample(scenario_list, len(scenario_list))
    scenario_list_hou_high = random.sample(scenario_list, len(scenario_list))
    scenario_list_hou_low = random.sample(scenario_list, len(scenario_list))
    scenario_list_nut_high = random.sample(scenario_list, len(scenario_list))
    scenario_list_nut_low = random.sample(scenario_list, len(scenario_list))
    return scenario_list_gdp_high, scenario_list_gdp_low, scenario_list_mob_high, scenario_list_mob_low,\
          scenario_list_hou_high, scenario_list_hou_low, scenario_list_nut_high, scenario_list_nut_low

scenario_list_gdp_high, scenario_list_gdp_low, scenario_list_mob_high, scenario_list_mob_low,\
      scenario_list_hou_high, scenario_list_hou_low, scenario_list_nut_high, scenario_list_nut_low = random_scenario_order()


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
global_xticks = dict(tickangle=-90, automargin=True,
                     tickvals = [2050])
# set the x-tick labels to include a space before and after the year
#global_xtick_labels = ['2020', '2050']
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
                category_orders={"Scenario": scenario_list_gdp_high,
                                 "Region": sorted(pd.unique(df["Region"]))},
                title="Economic activity scenarios",
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
                category_orders={"Scenario": scenario_list_gdp_low,
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
                category_orders={"Scenario": scenario_list_mob_high,
                                 "Region": sorted(pd.unique(df["Region"]))},
                title="Mobility scenarios",
                range_x=[2020, 2050],
                range_y=[0, 27000],
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
                category_orders={"Scenario": scenario_list_mob_low,
                                 "Region": sorted(pd.unique(df["Region"]))},
                title="Mobility scenarios",
                range_x=[2020, 2050],
                range_y=[0, 27000],
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
                category_orders={"Scenario": scenario_list_hou_high,
                                 "Region": sorted(pd.unique(df["Region"]))},
                title="Housing scenarios",
                range_x=[2020, 2050],
                range_y=[0, 115],
                color_discrete_map=colors_dict,
                hover_data=hover_dic,
                hover_name=global_hover_name
                )

hou_high.add_hline(y=25,
              annotation_text="",
              annotation_position="bottom left",
              line_dash="dot")

#LOW THRESHOLD
hou_low = px.line(df[df["scen_id"].str.contains("building") & df["scen_id"].str.contains("low")], x='Year', y="Value", color="Region", facet_col='Scenario',
                labels={
                     "Value": "floorspace (m²) per capita per year",
                     "Year" : ""
                },
                category_orders={"Scenario": scenario_list_hou_low,
                                 "Region": sorted(pd.unique(df["Region"]))},
                title="Housing scenarios",
                range_x=[2020, 2050],
                range_y=[0, 115],
                color_discrete_map=colors_dict,
                hover_data=hover_dic,
                hover_name=global_hover_name
                )

hou_low.add_hline(y=15,
              annotation_text="",
              annotation_position="bottom left",
              line_dash="dot")

#----NUTRITION----#
#HIGH THRESHOLD
nut_high = px.line(df[df["scen_id"].str.contains("nutrition") & df["scen_id"].str.contains("high")], x='Year', y="Value", color="Region", facet_col='Scenario',
                labels={
                     "Value": "kCal per capita/day",
                     "Year" : ""
                },
                #automise random order
                category_orders={"Scenario": scenario_list_nut_high,
                                 "Region": sorted(pd.unique(df["Region"]))},
                title="Meat consumption scenarios",
                range_x=[2018, 2050],
                range_y=[0, 700],
                color_discrete_map=colors_dict,
                hover_data=hover_dic,
                hover_name=global_hover_name
                )

# Add Lancet Healthy Diet
nut_high.add_hline(y=210,
               annotation_text="",
               annotation_position="bottom left",
               line_dash="dot")


#LOW THRESHOLD
nut_low = px.line(df[df["scen_id"].str.contains("nutrition") & df["scen_id"].str.contains("low")], x='Year', y="Value", color="Region", facet_col='Scenario',
                labels={
                     "Value": "kCal per capita/day",
                     "Year" : ""
                },
                #automise random order
                category_orders={"Scenario": scenario_list_nut_low,
                                 "Region": sorted(pd.unique(df["Region"]))},
                title="Meat consumption scenarios",
                range_x=[2018, 2050],
                range_y=[0, 700],
                color_discrete_map=colors_dict,
                hover_data=hover_dic,
                hover_name=global_hover_name
                )

# Add Lancet Healthy Diet
nut_low.add_hline(y=90,
               annotation_text="",
               annotation_position="bottom left",
               line_dash="dot")


#LAYOUT UPDATES
#get list of all plots defined above
plots = [gdp_high, gdp_low, mob_high, mob_low, hou_high, hou_low, nut_high, nut_low]
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
    'height': plot_height,
    'showlegend': False
}
# Function to apply layout settings to a plot
def apply_layout_settings(plot):
    updated_plot = plot.update_layout(**layout_settings)
    updated_plot.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    updated_plot.update_annotations(font_size=font_size_subheadings)
    updated_plot.update_xaxes(global_xticks)
    #updated_plot.update_xaxes(ticktext=global_xtick_labels)
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

# def create_connection():
#         credentials = service_account.Credentials.from_service_account_info(
#         st.secrets["gcp_service_account"], 
#         scopes=["https://www.googleapis.com/auth/spreadsheets",],)
#         connection = connect(":memory:", adapter_kwargs={
#             "gsheetsapi" : { 
#             "service_account_info" : {
#                 "type" : st.secrets["gcp_service_account"]["type"],
#                 "project_id" : st.secrets["gcp_service_account"]["project_id"],
#                 "private_key_id" : st.secrets["gcp_service_account"]["private_key_id"],
#                 "private_key" : st.secrets["gcp_service_account"]["private_key"],
#                 "client_email" : st.secrets["gcp_service_account"]["client_email"],
#                 "client_id" : st.secrets["gcp_service_account"]["client_id"],
#                 "auth_uri" : st.secrets["gcp_service_account"]["auth_uri"],
#                 "token_uri" : st.secrets["gcp_service_account"]["token_uri"],
#                 "auth_provider_x509_cert_url" : st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
#                 "client_x509_cert_url" : st.secrets["gcp_service_account"]["client_x509_cert_url"],
#                 }
#             },
#         })
#         return connection.cursor()
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

#function to disable automatic submission of form
# def on_text_input_enter():
#     pass #don't do anything, just don't submit the form


#set font size for normal text
font_size = "20px"

with st.form("Survey"):

    #MEAT CONSUMPTION
    coll, colm, colr = st.columns([0.4, 0.6, 0.4])
    with colm:
        st.markdown('# Justice in climate mitigation scenarios')

    #INTRODUCTION
        st.markdown(f"""<p style="font-size:{font_size};">
                    Climate justice isn’t just about reducing CO2 emission. At its core, it is about using limited resources, like materials and energy, to make sure people have access to basic services such as food, mobility, housing and economic activities. 
                    Unfortunately, it is not always clear what a "fair" distribution of resources and therefore access to services would look like. Let's explore this question together!
                    <br>
                    For all figures in this web application, only the values for the year 2020 are based on real data, other annual values are fictional. The baselines provided are examples and to some extent arbitrary.
                    <br>
                    Disclaimer: By using our web application, you agree to our data privacy rules.
                    </p>""", unsafe_allow_html=True)

        #ECONOMIC ACTIVITY
        #High Threshold
        st.markdown("### Economic Activity")
        #st.markdown(f"""<p style="font-size:{font_size};">Despite being contested, the gross domestic product (GDP) is universally used as an indicator for economic performance.</p>""", unsafe_allow_html=True)
        st.markdown(f"""<p style="font-size:{font_size};">
                    Despite being contested, the gross domestic product (GDP) is universally used as an indicator for how well an economy is doing.
                    Below, we present future GDP developments across different world regions. <b> GDP per capita </b> is used to assess the economic activity of a country in relation to its population.
                    In climate scenarios, GDP per capita is an important indicator for estimating future energy demand and supply. 
                    The figure below shows the GDP per capita for different world regions. 
                    Please note that only the values for the year 2020 are based on actual data, all other values are fictional. 
                    The dashed line displays the <b> average GDP per capita across the world </b>.
                    This average GDP per capita is projected to be around 28.000 USD per person (in 2017 USD) and assumes a global future that features high levels of sustainability, wealth and equality. 
                    The value is taken from the Shared-Socioeconomic Pathways (SSPs), a set of socio-economic scenarios often used in climate mitigation modelling. 
                    More specifically, this global average is based on the most optimistic SSP, SSP1 which assumes future world development is “taking the Green Road”. 
                    This GDP per capita of 28.000 USD would mean more than doubling the current global average GDP per capita (13.000 USD). 
                    </p>""", unsafe_allow_html=True)  
        st.markdown(f"""<p style="font-size:{font_size};"><i>Please assume that all scenarios below reach the same climate mitigation goal of 1.5°C.<i> <br>
                Please also note that feasibility and trade-off concerns (e.g. high levels of negative emissions) associated with growth scenarios are outside the scope of this study.</p>""", unsafe_allow_html=True)
        #Graph
        st.plotly_chart(gdp_high, theme="streamlit", config=config, use_container_width=True)
        #Questions
        q1 = st.radio("Which scenario do you personally find to be the fairest, based on the graph above?", ["-"] + scenario_list_gdp_high,horizontal=True ,
                        key=1)
        q2 = st.text_input("Why do you find this scenario to be the fairest?", placeholder="Please enter your answer here", 
                            key=2)
        q3 = st.selectbox("Which of the following aspects does best describe your main reason for your scenario selection?", ["-"] + accepted_answers2,
                        key=3)
        #Low Threshold
        st.markdown("<br> <br>",unsafe_allow_html=True)
        st.markdown(f"""<p style="font-size:{font_size};"> 
                    Now, let’s envision an alternative future with different economic development! 
                    In this case, the dashed line now marks 20.000 USD per capita. This can be assumed to be a universal income required for a <b> decent life </b>. 
                    It symbolises a life where all basic needs are satisfied, without consuming luxury goods. 
                    Analyses show, that this level of GDP marks approximately the point at which an increase of GDP is not related anymore with an increase of the Human Development Index (HDI).
                    </p>""", unsafe_allow_html=True)          
        st.plotly_chart(gdp_low, theme="streamlit", config=config, use_container_width=True) #Graph
        #Questions
        q4 = st.radio("Which scenario do you personally find to be the fairest, based on the graph above?", ["-"] + scenario_list_gdp_low,horizontal=True ,
                        key=4)
        q5 = st.text_input("Why do you find this scenario to be the fairest?", placeholder="Please enter your answer here", 
                            key=5)
        q6 = st.selectbox("Which of the following aspects does best describe your main reason for your scenario selection?", ["-"] + accepted_answers2,
                        key=6)
        st.markdown("<br> <br>",unsafe_allow_html=True)
        gdp_threshold = st.selectbox("Which of the two thresholds regarding economic activity do you prefer?", ["-"] + ["Higher threshold", "Lower threshold"])
        st.markdown("""---""")

        #MOBILITY
        #High Threshold
        st.markdown("### Mobility")
        st.markdown(f"""<p style="font-size:{font_size};">Mobility is important for a good standard of living as it allows the connection of people and markets, thereby enabling access to services and economic opportunities.  
                    However, the current mobility system has significant negative effects on human health and the environment. 
                    The mobility sector is a major contributor to global greenhouse gas emissions, while air and noise pollution further affect local populations. 
                    Moreover, mobility infrastructure is artificially dividing natural habitats and thereby damaging ecosystems.</p>""", unsafe_allow_html=True)
        st.markdown(f"""<p style="font-size:{font_size};">
                    Here, we are presenting future developments for mobility across different world regions. 
                    Mobility is represented through the indicator <b> passenger kilometres per year </b>, which includes all modes of motorized transport except air travel. 
                    This indicator provides insights into the overall level of mobility within a population or region and is used to estimate energy consumption and environmental impacts in climate scenarios. 
                    As a benchmark, the dashed line refers to the <b> Japanese mobility system </b>, which is often considered a role model: Japan’s population enjoys a good mobility system that operates very energy efficient. 
                    The average Japanese individual travels approximately 22km with motorized transport per day (8.000km per year). 
                    This is equivalent to daily travelling the distance from the Vienna International Airport to the Hofburg (20km) to reach the work place, and undertaking an additional, shorter trip to the gym or a grocery store. 
                    This level of mobility also allows for occasional longer-distance weekend or holiday trips.
                    </p>""", unsafe_allow_html=True)  
        st.markdown(f"""<p style="font-size:{font_size};"><i>Please assume that all scenarios below reach the same climate mitigation goal of 1.5°C.<i> <br>
                Please also note that feasibility and trade-off concerns (e.g. high levels of negative emissions) associated with growth scenarios are outside the scope of this study.</p>""", unsafe_allow_html=True)
                    
        #Graph
        st.plotly_chart(mob_high, theme="streamlit", config=config, use_container_width=True)
        #Questions
        q7 = st.radio("Which scenario do you personally find to be the fairest, based on the graph above?", ["-"] + scenario_list_mob_high,horizontal=True,
            key=7)
        q8 = st.text_input("Why do you find this scenario to be the fairest?", placeholder="Please enter your answer here",
            key=8)
        q9 = st.selectbox("Which of the following aspects does best describe your main reason for your scenario selection?", ["-"] + accepted_answers2,
            key=9)
        #Low Threshold
        st.markdown("<br> <br>",unsafe_allow_html=True)
        st.markdown(f"""<p style="font-size:{font_size};"> 
                    To satisfy human mobility needs for a <b> decent life </b>, a rough estimate is 3.500 passenger kilometre a year. 
                    This translate to a little less than 10km of motorized transport per day, equivalent to double the length of Vienna’s Ring Road (5.3km). 
                    It is assumed that many distances are covered using active modes of transport, such as walking or cycling. 
                    Groceries and leisure activities would be pursued in the neighbourhood. 
                    </p>""", unsafe_allow_html=True)          
        st.plotly_chart(mob_low, theme="streamlit", config=config, use_container_width=True)  # Graph
        #Questions
        q10 = st.radio("Which scenario do you personally find to be the fairest, based on the graph above?", ["-"] + scenario_list_mob_low,horizontal=True ,
            key=10)
        q11 = st.text_input("Why do you find this scenario to be the fairest?", placeholder="Please enter your answer here", 
                key=11)
        q12 = st.selectbox("Which of the following aspects does best describe your main reason for your scenario selection?", ["-"] + accepted_answers2,
            key=12)     

        st.markdown("<br> <br>",unsafe_allow_html=True)
        mob_threshold = st.selectbox("Which of the two mobility thresholds do you prefer?", ["-"] + ["Higher threshold", "Lower threshold"])
        st.markdown("""---""")

        #HOUSING
        #High Treshold
        st.markdown("### Housing")
        st.markdown(f"""<p style="font-size:{font_size};">Housing is a central factor for a persons living conditions, but it also has a significant environmental impact.  
        Aside from the land used for construction and the resources consumed during construction, housing requires a large amounts of energy for heating, cooling, and cooking.</p>""", unsafe_allow_html=True)
        st.markdown(f"""<p style="font-size:{font_size};">
                    Let’s now look at future developments regarding housing across different world regions.
                    <b> Floor space per capita </b> is used to assess the level of living or working space available to individuals. 
                    In climate scenarios, this indicator helps calculate heating and cooling needs, which are essential for determining energy demands.
                    In the figure below, the dashed line symbolizes a floor space of 25m² (or 270ft²) per person, which is the <b> recommended floor space per person by the Japanese Ministry of Health, Labour and Welfare </b>. 
                    This is a little less than the area covered by 3 average cars. For a family of three, this would mean living in a 75m² (807ft²) single family house with a kitchen and a children’s rooms.
                    </p>""", unsafe_allow_html=True)  
        st.markdown(f"""<p style="font-size:{font_size};"><i>Please assume that all scenarios below reach the same climate mitigation goal of 1.5°C.<i> <br>
                Please also note that feasibility and trade-off concerns (e.g. high levels of negative emissions) associated with growth scenarios are outside the scope of this study.</p>""", unsafe_allow_html=True)
        #Graph
        st.plotly_chart(hou_high, theme="streamlit", config=config, use_container_width=True)
        #Questions
        q13 = st.radio("Which scenario do you personally find to be the fairest, based on the graph above?", ["-"] + scenario_list_hou_high,horizontal=True ,
                key=13)
        q14 = st.text_input("Why do you find this scenario to be the fairest?", placeholder="Please enter your answer here",
                key=14)
        q15 = st.selectbox("Which of the following aspects does best describe your main reason for your scenario selection?", ["-"] + accepted_answers2,
                key=15)
        #Low Threshold
        st.markdown("<br> <br>",unsafe_allow_html=True)
        st.markdown(f"""<p style="font-size:{font_size};">
                    Now let’s consider a dashed line that marks 15m² (160ft²) per person, which can again be considered a lower minimum for a <b> decent life </b>. 
                    The family of three has now 45m² (480ft²) at their disposal. 45m² allow for two medium-sized room and a kitchenette. 
                    </p>""", unsafe_allow_html=True)          
        st.plotly_chart(hou_low, theme="streamlit", config=config, use_container_width=True)   
        #Questions
        q16 = st.radio("Which scenario do you personally find to be the fairest, based on the graph above?", ["-"] + scenario_list_hou_low,horizontal=True ,
                key=16)
        q17 = st.text_input("Why do you find this scenario to be the fairest?", placeholder="Please enter your answer here", 
                    key=17)
        q18 = st.selectbox("Which of the following aspects does best describe your main reason for your scenario selection?", ["-"] + accepted_answers2,
                key=18)
        st.markdown("<br> <br>",unsafe_allow_html=True)
        hou_threshold = st.selectbox("Which of the two housing thresholds do you prefer?", ["-"] + ["Higher threshold", "Lower threshold"])
        st.markdown("""---""")

        #NUTRITION
        st.markdown('### Nutrition')
        
        st.markdown(f"""<p style="font-size:{font_size};">A balanced diet is crucial for human health and involves consuming a variety of fruits, vegetables, nuts, and animal products.  
                        Meat production has many environmental impacts and requires a lot of resources compared to plant-based foods. Raising animals for meat requires large amounts of land, water, and feed. 
                        The production of feed for livestock, like soy and corn, often involves deforestation and the use of fertilizers, which contribute to greenhouse gas emissions. 
                        Moreover, certain animals produce methane, a potent greenhouse gas, during their digestive process.</p>""", unsafe_allow_html=True)
        
        #High Threshold
        st.markdown(f"""<p style="font-size:{font_size};">
                    Below, we present future developments for meat consumption across different world regions. 
                    Meat consumption is measured using <b> kilo calories of meat consumption per capita per day </b>. 
                    The dashed line marks 210 kcal, which is the <b> maximum suggested daily meat intake </b> according to the British National Health System (NHS). 
                    This is an amount of meat similar to one and a half slices of bread.
                    </p>""",unsafe_allow_html=True)
        #Graph
        st.plotly_chart(nut_high, theme="streamlit", config=config, use_container_width=True)
        #Questions
        q19 = st.radio("Which scenario do you personally find to be the fairest, based on the graph above?", ["-"] + scenario_list_nut_high, horizontal=True ,
                    key=19)
        q20 = st.text_input("Why do you find this scenario to be the fairest?", placeholder="Please enter your answer here",
                    key=20)
        q21 = st.selectbox("Which of the following aspects does best describe your main reason for your scenario selection?", ["-"] + accepted_answers2,
                    key=21 )
        #Low Threshold
        st.markdown(f"""<p style="font-size:{font_size};">
                    On the other hand, the EAT-Lancet Commission, recommends a <b> healthy diet </b> that includes approximately 90cKal (or 85g) of meat per day, which is now represented as the dashed line. 
                    This quantity is similar to a piece of meat the size of the palm of your hand.
                    </p>""", unsafe_allow_html=True)
        
        st.markdown(f"""<p style="font-size:{font_size};"><i>Please assume that all scenarios below reach the same climate mitigation goal of 1.5°C.<i> <br>
                Please also note that feasibility and trade-off concerns (e.g. high levels of negative emissions) associated with growth scenarios are outside the scope of this study.</p>""", unsafe_allow_html=True)
        #Graph
        st.plotly_chart(nut_low, theme="streamlit", config=config, use_container_width=True)
        #Questions
        q22 = st.radio("Which scenario do you personally find to be the fairest, based on the graph above?", ["-"] + scenario_list_nut_low, horizontal=True ,
                    key=22)
        q23 = st.text_input("Why do you find this scenario to be the fairest?", placeholder="Please enter your answer here",
                    key=23)
        q24 = st.selectbox("Which of the following aspects does best describe your main reason for your scenario selection?", ["-"] + accepted_answers2,
                    key=24)
        st.markdown("<br> <br>",unsafe_allow_html=True)
        nut_threshold = st.selectbox("Which of the two thresholds regarding nutrition do you prefer?", ["-"] + ["Higher threshold", "Lower threshold"])
        st.markdown("""---""")

        #PERSONAL QUESTIONS
        st.markdown('### Personal Questions')
        q25 = st.selectbox("How knowledgeable are you about Integrated Assessment Models used for climate mitigation scenarios?",
                ("-", "No prior experience", "Experience in the context of reports such as IPCC", "Occasional user of scenario outputs", "Expert level"),
                key=25)
        q26=st.selectbox("How often per week do you eat meat?",
                    ("-", "Never", "Once per week or less", "At least 3 times per week", "Everyday"), 
                    key=26)
        q27=st.selectbox("How often per year do you travel by plane?",#
                    ("-", "Never", "Once per year", "3 times per year", "At least 5 times per year"), 
                    key=27)
        q28=st.selectbox("What is the size of your apartment/ house?",
                    ("-", "Less than 10m² per person", "Between 10m² and 30m² per person","Between 30m² and 50m² per person","More than 50m² per person" ), 
                    key=28)
        q29 = st.selectbox("Which region are you from? (Please select the region you feel closer to and more knowledgeable about)",
                list_of_regions, 
                key=29)
        q30 = st.selectbox("What type of organisation do you work for?", 
                ("-", "Government", "Research or academic organisation", "Non-governmental organisation", "Interational organisation", "Private Sector", "Other"), 
                key=30)
        #TODO: add conditional pop-up for st text with other
        q31 = st.selectbox("What is the highest level of education you have completed?",
                ("-", 'No degree', 'High school diploma (or equivalent)', 'Some college', 'Professional degree', "Bachelor's degree", "Master's degree", "Doctoral degree"),
                key=31)
        q32 = st. selectbox("What is your age?",
                ("-", "18-24", '25-34','35-44','45-54','55-64','65-100'), 
                key=32)
        q33 = st.selectbox("What is your gender?",
                ("-", "Male", "Female", "Other", "Prefer not to say"), 
                key=33)
        q34 = st.selectbox("To which sector is your work most related to?",
                ("-", "Agriculture/Food/Land Management", "Industry/Manufacturing", "Transport/Shipping/Public Transportation", "Buildings/Housing/Construction", "Climate mitigation/ adapdation", "Other"), 
                key=34)
        timestamp = time.time()

    #Submit button; send data to google sheet
        submitted = st.form_submit_button("Click here to submit!")
        if submitted:
            #cursor = create_connection()
            #query = f'INSERT INTO "{sheet_url}" VALUES ("{q1}", "{q2}", "{q3}", "{q4}", "{q5}", "{q6}", "{q7}", "{q8}", "{q9}", "{q10}","{q11}","{q12}","{q13}","{q14}","{q15}","{q16}","{q17}","{q18}","{q19}","{q20}","{q21}","{q22}","{q23}","{q24}","{q25}","{q26}","{q27}","{q28}","{q29}","{q30}","{q31}", "{timestamp}")'
            #cursor.execute(query)
            session_state = st.session_state['rs']
            import gspread
            credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], 
            scopes=["https://www.googleapis.com/auth/spreadsheets",],)

            client = gspread.authorize(credentials) 
            sheet = client.open_by_url(sheet_url)
            worksheet = sheet.get_worksheet(0)
            values = [session_state, q1, q2, q3, q4, q5, q6, q7, q8, q9, \
                      q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, \
                        q20, q21, q22, q23, q24, q25, q26, q27, q28, q29, \
                            q30, q31, q32, q33, q34,\
                                gdp_threshold, mob_threshold,hou_threshold, nut_threshold, timestamp]
            worksheet.append_row(values, 1)


            #generate to send data to google sheet
            #my column names are: gdp_high_scenario	gdp_high_feedback	gdp_high_motivation	gdp_low_scenario	gdp_low_feedback	gdp_low_motivation	mob_high_scenario	mob_high_feedback	mob_high_motivation	mob_low_scenario	mob_low_feedback	mob_low_motivation	hou_high_scenario	hou_high_feedback	hou_high_motivation	hou_low_scenario	hou_low_feedback	hou_low_motivation	nut_scenario	nut_feedback	nut_motivation	IAM_expertise	meat_consumption	air_travel	housing_space	region	organisation	education	age	gender	sector	timestamp
            #my value names are q1 to q31
            # credentials = service_account.Credentials.from_service_account_info(
            #     st.secrets["gcp_service_account"])
            # conn = connect(credentials=credentials)
            # data_to_send = {
            #     "gdp_high_scenario": q1,
            #     "gdp_high_feedback": q2,
            #     "gdp_high_motivation": q3,
            #     "gdp_low_scenario": q4,
            #     "gdp_low_feedback": q5,
            #     "gdp_low_motivation": q6,
            #     "mob_high_scenario": q7,
            #     "mob_high_feedback": q8,
            #     "mob_high_motivation": q9,
            #     "mob_low_scenario": q10,
            #     "mob_low_feedback": q11,
            #     "mob_low_motivation": q12,
            #     "hou_high_scenario": q13,
            #     "hou_high_feedback": q14,
            #     "hou_high_motivation": q15,
            #     "hou_low_scenario": q16,
            #     "hou_low_feedback": q17,
            #     "hou_low_motivation": q18,
            #     "nut_scenario": q19,
            #     "nut_feedback": q20,
            #     "nut_motivation": q21,
            #     "IAM_expertise": q22,
            #     "meat_consumption": q23,
            #     "air_travel": q24,
            #     "housing_space": q25,
            #     "region": q26,
            #     "organisation": q27,
            #     "education": q28,
            #     "age": q29,
            #     "gender": q30,
            #     "sector": q31,
            #     "timestamp": timestamp
            # }
            # conn.insert("Sheet1", data_to_send)
            
            st.write("**:green[Submission successful. Thank you for your input!]**")
            st.toast("**:green[Submission successful!]**", icon=None)

