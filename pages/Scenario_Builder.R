#-------------------------#
#       Libraries         #
#-------------------------#
#import libraries
library(reticulate)
library(readxl)
library(dplyr)
library(tidyverse)
library(ggplot2)

#load baseline data
#read_excel("C:\\Users\\scheifinger\\OneDrive - IIASA\\Interactive Tools\\Scenario Archetypes\\Scenario Archetypes.xlsx", 
#           sheet = "Baseline",
#           skip=1)

require(reticulate)
#IIASA
use_condaenv(condaenv = "C:\\Users\\scheifinger\\AppData\\Local\\anaconda3\\envs\\Streamlit", conda = "auto", required = NULL)
#home
#use_condaenv("C:\\Users\\schei\\anaconda3\\envs\\streamlit", conda="auto", required = NULL)
pyam <- import("pyam")


#-------------------------#
#       Functions         #
#-------------------------#

#define functions
##function that calculates CAGR
CAGR_calculator <- function(starting_value, end_value, n ) {
  rate = (end_value / starting_value) ^(1/n)
  rate = rate - 1
  return(rate)
}

##function that calculate linear growth
LG_calculator <- function(starting_value, end_value,n){
  rate =  (end_value / starting_value)^(1/n) - 1
  return(rate)
}

##function that creates df for certain region based on years and growth rate
forecaster <- function(starting_year, starting_value, years, 
                       growth_rate, region, growth_type){
  #create new data frame
  new_df <- data.frame(
    region = character(),
    value = numeric(),
    year = numeric()
  )
  #iterate over years
  for (i in seq(years)){
    n = i
    value = starting_value * ((1+growth_rate)**n)
    #convert data into vector
    new_row <- c(region = region, value = value, year = years[i])
    #append to dataframe while avoid loosing column title
    new_df[nrow(new_df) + 1,] <- new_row
  }
  #return new_df
  return(new_df)
}

#test function
ys = c(2022, 2026, 2030, 2034, 2038, 2042, 2046, 2050)
forecaster(2018, 24.12279228, ys, -0.0231558,"Test", growth_type = "aagr")

#pack running forecast in one function
run_forecast <- function(historic_values, #follow format region, value, year
                         starting_year, #most recent year with data (2020)
                         list_of_growth_rates, #list of growth rates for each region
                         list_of_years, #list of years to run projection for
                         list_of_regions,#list of regions to be included - must be in historic_values
                         scenario_name)#name that scenario should get in csv file
{
  #generate empty list
  df_list <- list()
  ##add starting values
  df_list[[1]] <- historic_values %>% filter(year==starting_year)
  ##add starting index
  index = 1
  for (r in list_of_regions){
    index = index + 1 #iterate index
    #run forecaster function
    new_df = forecaster(starting_year =  starting_year,
                        starting_value = filter(historic_values, region == r, year==starting_year)$value,
                        years = list_of_years,
                        growth_rate = filter(growth_rates,region == r)$gr,
                        region = r)
    #add to df_list
    df_list[[index]] <- new_df
  }
  #combine df_list
  scen_data = do.call(rbind, df_list)
  #name scenario
  scen_data <- scen_data %>%
    #convert value column to numeric
    mutate(value = as.numeric(value)) %>%
    #add column to identify scenario
    mutate(scenario = scenario_name)%>%
    #add identifier at beginning of df
    relocate(scenario, .before = 1)
  return(scen_data)
}

#-------------------------#
#    Global Variables     #
#-------------------------#

#create dataframe that will be used to export scenarios in csv formate
export_df <- data.frame()

#create list with relevant regions
regions_filter = c(
  "North America; primarily the United States of America and Canada",
  "Eastern and Western Europe (i.e., the EU28)",
  "Countries of Latin America and the Caribbean",
  "Countries of South Asia; primarily India",
  "Countries of centrally-planned Asia; primarily China",
  "Pacific OECD",
  "Reforming Economies of Eastern Europe and the Former Soviet Union; primarily Russia",
  "Countries of the Middle East; Iran, Iraq, Israel, Saudi Arabia, Qatar, etc.",
  "Countries of Sub-Saharan Africa"
)


#-------------------------#
#        Read Me          #
#-------------------------#
# This script models five scenarios.
# 1) Aggregate utilitarian: everyone grows the same
# 2) Prioritarian: lowest 5 ones grow while other stay constant; the lower the higher growth
    #distances between lowest 5 curves must decline 
# 3) Egalitarian: convergence
# 4) sufficientarian: lower ones grow to threshold by 2040 and stay there, highest stay constant
# 5) Limitarian: highest ones reduce, lowers stay constant
# When core logic of justice principle doesn't specify for some regions, regions stay constant

#-------------------------#
#       Transport         #
#-------------------------#
#load data
df = pyam$read_iiasa(
  'ar6-public',
  model='REMIND-MAgPIE 2.1-4.2',
  #scenario='2.1-4.2_SusDev_SDP-PkBudg1000',
  variable=c('Energy Service|Transportation|Passenger'),
  meta=c('category')
)
#get right format
df = df$data

#get starting values
hist_data <- c("2005", "2010", "2015", "2020")
#look at historic values
hist_vals <- df %>%
  #filter on year, scenario and region
  filter((year %in% hist_data) & (scenario == 'SusDev_SDP-PkBudg1000') & (region %in% regions_filter)) %>%
  select(region, value, year)

hist_vals %>%
  ggplot(aes(x=year, y=value, color=region))+
  geom_line()

#specify years for scenarios
years <- c(2025, 2030, 2035, 2040, 2045, 2050)
#get regions for scenarios
regions_list <- unique(hist_vals$region)

####----GENERAL SCENARIO----####
years <- c(2025, 2030, 2035, 2040, 2045, 2050)
starting_values <- c(100, 200, 300, 400, 500, 600, 700, 800, 900)
regions_list <- c("A", "B", "C", "D", "E", "F", "G", "H", "I")
## AGGREGATE UTILITARIAN
#set end values
end_values <- starting_values + 200
#get growth rates
growth_rates <- LG_calculator(starting_value = starting_values,
                              end_value = end_values,
                              n = length(years))
#forecast
df_list <- list()
index = 0
for (r in regions_list){
  index = index + 1 #iterate index
  new_df = forecaster(starting_year =  2020,
            starting_value = starting_values[index],
            years = years,
            growth_rate = growth_rates[index],
            region = r)
  #add to data list
  df_list[[index]] <- new_df
}
scen_data = do.call(rbind, df_list)

#Visualize it
scen_data %>%
    ggplot(aes(x=as.numeric(year), y=as.numeric(value), group=region, color=region))+
    geom_line() +
    ggtitle("Basic Aggregate Scenario")+
    ylim(0, 1200)


## PRIORITARIAN
end_values <- starting_values * c(3.8, 2, 1.5, 1.2, 1.05, 1, 1, 1, 1)
#get growth rates
growth_rates <- CAGR_calculator(starting_value = starting_values,
                              end_value = end_values,
                              n = length(years))
#forecast
df_list <- list()
index = 0
for (r in regions_list){
  index = index + 1 #iterate index
  new_df = forecaster(starting_year =  2020,
            starting_value = starting_values[index],
            years = years,
            growth_rate = growth_rates[index],
            region = r)
  #add to data list
  df_list[[index]] <- new_df
}
scen_data = do.call(rbind, df_list)

#Visualize it
scen_data %>%
    ggplot(aes(x=as.numeric(year), y=as.numeric(value), group=region, color=region))+
    geom_line() +
    ggtitle("Basic Prioriatrian Scenario")+
    ylim(0, 1200)

##EGALITARIAN
end_values <-  c(450, 450, 450, 450, 450, 450, 450, 450, 450)
#get growth rates
growth_rates <- CAGR_calculator(starting_value = starting_values,
                              end_value = end_values,
                              n = length(years))
#forecast
df_list <- list()
index = 0
for (r in regions_list){
  index = index + 1 #iterate index
  new_df = forecaster(starting_year =  2020,
            starting_value = starting_values[index],
            years = years,
            growth_rate = growth_rates[index],
            region = r)
  #add to data list
  df_list[[index]] <- new_df
}
scen_data = do.call(rbind, df_list)

#Visualize it
scen_data %>%
    ggplot(aes(x=as.numeric(year), y=as.numeric(value), group=region, color=region))+
    geom_line() +
    ggtitle("Basic Prioriatrian Scenario")+
    ylim(0, 1200)

##SUFFICITARIAN
threshold <- 350
end_values <- c(threshold, threshold, threshold, 400, 500, 600, 700, 800, 900)
#get growth rates
growth_rates <- CAGR_calculator(starting_value = starting_values,
                              end_value = end_values,
                              n = length(years)-2)
#forecast
df_list <- list()
index = 0
for (r in regions_list){
  index = index + 1 #iterate index
  new_df = forecaster(starting_year =  2020,
            starting_value = starting_values[index],
            years = years,
            growth_rate = growth_rates[index],
            region = r)
    #change 2045 and 2050 values to threshold for affected years
  if (new_df$value[6] != new_df$value[5]){ #affected years grow until end
    new_df <- new_df %>%
      mutate(value = if_else(year %in% c(2045, 2050), as.numeric(threshold), as.numeric(value)))
    
  }
  #add to data list
  df_list[[index]] <- new_df
}
scen_data = do.call(rbind, df_list)

#Visualize it
scen_data %>%
    ggplot(aes(x=as.numeric(year), y=as.numeric(value), group=region, color=region))+
    geom_line() +
    ggtitle("Basic Prioriatrian Scenario")+
    ylim(0, 1200)

##Limitarian
threshold <- 550
end_values <- c(100, 200, 300, 400, 500, threshold, threshold, threshold, threshold)
#get growth rates
growth_rates <- CAGR_calculator(starting_value = starting_values,
                              end_value = end_values,
                              n = length(years)-2)
#forecast
df_list <- list()
index = 0
for (r in regions_list){
  index = index + 1 #iterate index
  new_df = forecaster(starting_year =  2020,
            starting_value = starting_values[index],
            years = years,
            growth_rate = growth_rates[index],
            region = r)
    #change 2045 and 2050 values to threshold for affected years
  if (new_df$value[6] != new_df$value[5]){ #affected years grow until end
    new_df <- new_df %>%
      mutate(value = if_else(year %in% c(2045, 2050), as.numeric(threshold), as.numeric(value)))
    
  }
  #add to data list
  df_list[[index]] <- new_df
}
scen_data = do.call(rbind, df_list)

#Visualize it
scen_data %>%
    ggplot(aes(x=as.numeric(year), y=as.numeric(value), group=region, color=region))+
    geom_line() +
    ggtitle("Basic Prioriatrian Scenario")+
    ylim(0, 1200)


####----SCENARIO 1 TRANSPORT aggu----####
#AGGREGATE UTILITARIAN
##set growth rates individually via end value
##set end values in 2050; 0 means no change to present day
#find values via
# hist_vals %>% filter(year == 2020) %>% arrange(desc(value)) %>% mutate(value = value + 1000)
end_val = c(
  10295.520 , #Eastern and Western Europe (i.e., the EU28)
  9572.598 , #North America; primarily the United States of America and Canada
  6456.067 , #Countries of centrally-planned Asia; primarily China
  6042.791 , #Countries of the Middle East; Iran, Iraq, Israel, Saudi Arabia, Qatar, etc.
  5329.384 , #Countries of South Asia; primarily India
  5184.672 , #Countries of Latin America and the Caribbean
  3106.586 , #Reforming Economies of Eastern Europe and the Former Soviet Union; primarily Russia
  2554.980 , #Countries of Sub-Saharan Africa
  2396.735 ) #Pacific OECD

#add growth rates
growth_rates <- hist_vals %>%
  filter(year == 2020) %>%
  arrange(desc(value)) %>%
  mutate(end_val = end_val) %>%
  mutate(gr = if_else(end_val == 0,
                      0, 
                      LG_calculator(starting_value = value,
                                      end_value = end_val,
                                      n = length(years))))

#FORECAST
#create empty df
df_list <- list()
##add starting values
df_list[[1]] <- hist_vals %>% filter(year==2020)
##add starting index
index = 1
for (r in regions_list){
  index = index + 1 #iterate index
  new_df = forecaster(starting_year =  2020,
            starting_value = filter(hist_vals, region == r, year==2020)$value,
            years = years,
            growth_rate = filter(growth_rates,region == r)$gr,
            region = r)
  #add to data list
  df_list[[index]] <- new_df
}

scen_data = do.call(rbind, df_list)
#name scenario
scen_data <- scen_data %>%
  #convert value column to numeric
  mutate(value = as.numeric(value)) %>%
  #add column to identify scenario
  mutate(scenario = "transport_agg")%>%
  #add identifier at beginning of df
  relocate(scenario, .before = 1)

scen_data %>%
  ggplot(aes(x=year, y=value, group=region, color=region))+
  geom_line() +
  ggtitle("Transport: Agg utilitarian")+
  ylim(0, 12000)

#ADD TO EXPORT DF
export_df <- rbind(export_df, scen_data)


####----SCENARIO 2 TRANSPORT prio----####
#PRIORITARIAN
##set growth rates individually via end value
##set end values in 2050; 0 means no change to present day
end_val = c(
  0, #Eastern and Western Europe (i.e., the EU28)
  0, #North America; primarily the United States of America and Canada
  0, #Countries of centrally-planned Asia; primarily China
  0, #Countries of the Middle East; Iran, Iraq, Israel, Saudi Arabia, Qatar, etc.
  4800, #Countries of South Asia; primarily India
  4650, #Countries of Latin America and the Caribbean
  3800, #Reforming Economies of Eastern Europe and the Former Soviet Union; primarily Russia
  3500, #Countries of Sub-Saharan Africa
  3400) #Pacific OECD

#add growth rates/ uniform linear growth rates
growth_rates <- hist_vals %>%
  filter(year == 2020) %>%
  arrange(desc(value)) %>%
  mutate(end_val = end_val) %>%
  mutate(gr = if_else(end_val == 0,
                      0, 
                      LG_calculator(starting_value = value,
                                    end_value = end_val,
                                    n = length(years))))

#FORECAST
#create empty df
df_list <- list()
##add starting values
df_list[[1]] <- hist_vals %>% filter(year==2020)
##add starting index
index = 1
for (r in regions_list){
  index = index + 1 #iterate index
  new_df = forecaster(starting_year =  2020,
                      starting_value = filter(hist_vals, region == r, year==2020)$value,
                      years = years,
                      growth_rate = filter(growth_rates,region == r)$gr,
                      region = r)
  #add to data list
  df_list[[index]] <- new_df
}

scen_data = do.call(rbind, df_list)
#name scenario
scen_data <- scen_data %>%
  #convert value column to numeric
  mutate(value = as.numeric(value)) %>%
  #add column to identify scenario
  mutate(scenario = "transport_pri")%>%
  #add identifier at beginning of df
  relocate(scenario, .before = 1)

scen_data %>%
  ggplot(aes(x=year, y=value, group=region, color=region))+
  geom_line() +
  ggtitle("Transport: Prioritarian")+
  ylim(0, 12000)

#ADD TO EXPORT DF
export_df <- rbind(export_df, scen_data)



####----SCENARIO 3 TRANSPORT egal----####
#convergence at 8000

#GET GROWTH RATES
##get CAGR growth rates for each region
growth_rates <- hist_vals %>%
  filter(year == 2020) %>%
  mutate(gr = CAGR_calculator(starting_value = value,
                                end_value = 8000,
                                n = length(years)))

#FORECAST
#create empty df
df_list <- list()
##add starting values
df_list[[1]] <- hist_vals %>% filter(year==2020)
##add starting index
index = 1
for (r in regions_list){
  index = index + 1 #iterate index
  new_df = forecaster(starting_year =  2020,
                      starting_value = filter(hist_vals, region == r, year==2020)$value,
                      years = years,
                      growth_rate = filter(growth_rates,region == r)$gr,
                      region = r)
  #add to data list
  df_list[[index]] <- new_df
}

scen_data = do.call(rbind, df_list)
#name scenario
scen_data <- scen_data %>%
  #convert value column to numeric
  mutate(value = as.numeric(value)) %>%
  #add column to identify scenario
  mutate(scenario = "transport_ega")%>%
  #add identifier at beginning of df
  relocate(scenario, .before = 1)


scen_data %>%
  ggplot(aes(x=year, y=value, group=region, color=region))+
  geom_line() +
  ggtitle("Transport: Convergence at 8.000 pkm")

#ADD TO EXPORT DF
export_df <- rbind(export_df, scen_data)

####----SCENARIO 4 TRANSPORT suf----####
#countries above threshold stay constant, lowest reach threshold by 2040
#GET GROWTH RATES
##set growth rates individually via end value
##set end values in 2050; 0 means no change to present day
##set threshold
threshold = 2500
end_val = c(
  0, #Eastern and Western Europe (i.e., the EU28)
  0, #North America; primarily the United States of America and Canada
  0, #Countries of centrally-planned Asia; primarily China
  0, #Countries of the Middle East; Iran, Iraq, Israel, Saudi Arabia, Qatar, etc.
  0, #Countries of South Asia; primarily India
  0, #Countries of Latin America and the Caribbean
  threshold, #Reforming Economies of Eastern Europe and the Former Soviet Union; primarily Russia
  threshold, #Countries of Sub-Saharan Africa
  threshold) #Pacific OECD

#add growth rates
growth_rates <- hist_vals %>%
  filter(year == 2020) %>%
  arrange(desc(value)) %>%
  mutate(end_val = end_val) %>%
  mutate(gr = if_else(end_val == 0,
                               0, 
                               CAGR_calculator(starting_value = value,
                                               end_value = end_val,
                                               n = length(years)-2)))

#FORECAST
#create empty df
df_list <- list()
##add starting values
df_list[[1]] <- hist_vals %>% filter(year==2020)
##add starting index
index = 1
for (r in regions_list){
  index = index + 1 #iterate index
  new_df = forecaster(starting_year =  2020,
                      starting_value = filter(hist_vals, region == r, year==2020)$value,
                      years = years,
                      growth_rate = filter(growth_rates,region == r)$gr,
                      region = r)
  #change 2045 and 2050 values to threshold for affected years
  if (new_df$value[6] != new_df$value[5]){ #affected years grow until end
    new_df <- new_df %>%
      mutate(value = if_else(year %in% c(2045, 2050), as.numeric(threshold), as.numeric(value)))
    
  }
  #add to data list
  df_list[[index]] <- new_df
}

scen_data = do.call(rbind, df_list)
#name scenario
scen_data <- scen_data %>%
  #convert value column to numeric
  mutate(value = as.numeric(value)) %>%
  #add column to identify scenario
  mutate(scenario = "transport_suf")%>%
  #add identifier at beginning of df
  relocate(scenario, .before = 1)


scen_data %>%
  ggplot(aes(x=year, y=value, group=region, color=region))+
  geom_line()+
  ggtitle("Transport: Sufficitarian")+
  ylim(0, 12000)

#ADD TO EXPORT DF
export_df <- rbind(export_df, scen_data)


####----SCENARIO 5 TRANSPORT lim----####
#countries below threshold stay constant, highest reach threshold by 2040
#GET GROWTH RATES
##set growth rates individually via end value
##set end values in 2050; 0 means no change to present day
##set threshold
threshold = 7500
end_val = c(
  threshold, #Eastern and Western Europe (i.e., the EU28)
  threshold, #North America; primarily the United States of America and Canada
  0, #Countries of centrally-planned Asia; primarily China
  0, #Countries of the Middle East; Iran, Iraq, Israel, Saudi Arabia, Qatar, etc.
  0, #Countries of South Asia; primarily India
  0, #Countries of Latin America and the Caribbean
  0, #Reforming Economies of Eastern Europe and the Former Soviet Union; primarily Russia
  0, #Countries of Sub-Saharan Africa
  0) #Pacific OECD

#add growth rates
growth_rates <- hist_vals %>%
  filter(year == 2020) %>%
  arrange(desc(value)) %>%
  mutate(end_val = end_val) %>%
  mutate(gr = if_else(end_val == 0,
                      0, 
                      CAGR_calculator(starting_value = value,
                                      end_value = end_val,
                                      n = length(years)-2)))

#FORECAST
#create empty df
df_list <- list()
##add starting values
df_list[[1]] <- hist_vals %>% filter(year==2020)
##add starting index
index = 1
for (r in regions_list){
  index = index + 1 #iterate index
  new_df = forecaster(starting_year =  2020,
                      starting_value = filter(hist_vals, region == r, year==2020)$value,
                      years = years,
                      growth_rate = filter(growth_rates,region == r)$gr,
                      region = r)
  #change 2045 and 2050 values to threshold for affected years
  if (new_df$value[6] != new_df$value[5]){ #affected years grow until end
    new_df <- new_df %>%
      mutate(value = if_else(year %in% c(2045, 2050), as.numeric(threshold), as.numeric(value)))
    
  }
  #add to data list
  df_list[[index]] <- new_df
}

scen_data = do.call(rbind, df_list)
#name scenario
scen_data <- scen_data %>%
  #convert value column to numeric
  mutate(value = as.numeric(value)) %>%
  #add column to identify scenario
  mutate(scenario = "transport_lim")%>%
  #add identifier at beginning of df
  relocate(scenario, .before = 1)


scen_data %>%
  ggplot(aes(x=year, y=value, group=region, color=region))+
  geom_line()+
  ggtitle("Transport: Limitarian")+
  ylim(0, 12000)

#ADD TO EXPORT DF
export_df <- rbind(export_df, scen_data)


#-------------------------#
#         BUILDING        #
#-------------------------#
#load data
df = pyam$read_iiasa(
  'ar6-public',
  model='REMIND-MAgPIE 2.1-4.2',
  scenario='2.1-4.2_SusDev_SDP-PkBudg1000',
  variable=c('Energy Service|Residential and Commercial|Floor Space',
             'Population'),
  meta=c('category')
)
#annual demand for floor space (and associated energy servide demand for heating and lighting) in residential and commerical buildings
#bn m2/yr with bn = billion	
#population in million

#get right format
df = df$data

#get starting values
hist_data <- c("2005", "2010", "2015", "2020")
#look at historic values and add floor space per capita
hist_vals <- df %>%
  #filter on year, scenario and region
  filter((year %in% hist_data) & (scenario == 'SusDev_SDP-PkBudg1000') & (region %in% regions_filter)) %>%
  select(region, variable, value, year)%>%
  pivot_wider(names_from = c("variable"), values_from = c("value")) %>%
  rename(Floor_Space = `Energy Service|Residential and Commercial|Floor Space`)%>%
  #transform variables
  #from million to single
  mutate(Population = Population * 1000000)%>%
  #from billion to meter
  mutate(Floor_Space = Floor_Space * 1000000000) %>%
  mutate(floor_space_pc = Floor_Space / Population)
  #unit = m2/year per inhabitant

hist_vals %>%
  ggplot(aes(x=year, y=floor_space_pc, color=region))+
  geom_line()

#limit hist_vals to floor_space_pc only
hist_vals <- hist_vals %>%
  select(region, year, floor_space_pc)%>%
  rename(value = floor_space_pc)

#specify years for scenarios
years <- c(2025, 2030, 2035, 2040, 2045, 2050)
#get regions for scenarios
regions_list <- unique(hist_vals$region)

####----SCENARIO 1 BUIDLING aggu----####
#AGGREGATE UTILITARIAN
#GET GROWTH RATES
increase = 20
end_val <-c(
98.7+increase,#North America; primarily the United States of America and Canada    
58.5+increase,#Pacific OECD                                                        
56.5+increase,#Countries of centrally-planned Asia; primarily China                
54.9+increase,#Eastern and Western Europe (i.e., the EU28)                         
36.3+increase,#Countries of Latin America and the Caribbean                        
33.8+increase,#Reforming Economies of Eastern Europe and the Former Soviet Union; …
24.6+increase,#Countries of the Middle East; Iran, Iraq, Israel, Saudi Arabia, Qat…
16.0+increase,#Countries of Sub-Saharan Africa                                     
14.9+increase#Countries of South Asia; primarily India  
)

growth_rates <- hist_vals %>%
  filter(year == 2020) %>%
  arrange(desc(value)) %>%
  mutate(end_val = end_val) %>%
  mutate(gr = if_else(end_val == 0,
                      0, 
                      LG_calculator(starting_value = value,
                                    end_value = end_val,
                                    n = length(years))))
#FORECAST
scen_data <- run_forecast(historic_values = hist_vals,
             starting_year = 2020,
             list_of_growth_rates = growth_rates,
             list_of_years = years,
             list_of_regions = regions_filter,
             scenario_name = "building_agg")

scen_data %>%
  ggplot(aes(x=year, y=value, group=region, color=region))+
  geom_line()+
  ggtitle("Building: Agg utilitarian")

#ADD TO EXPORT DF
export_df <- rbind(export_df, scen_data)

####----SCENARIO 2 BUILDING prio----####
#PRIORITARIAN
#GET GROWTH RATES
end_val <-c(
  0,#North America; primarily the United States of America and Canada    
  0,#Pacific OECD                                                        
  0,#Countries of centrally-planned Asia; primarily China                
  0,#Eastern and Western Europe (i.e., the EU28)                         
  46,#Countries of Latin America and the Caribbean                        
  44.5,#Reforming Economies of Eastern Europe and the Former Soviet Union; …
  40,#Countries of the Middle East; Iran, Iraq, Israel, Saudi Arabia, Qat…
  35,#Countries of Sub-Saharan Africa                                     
  34.5#Countries of South Asia; primarily India  
)

growth_rates <- hist_vals %>%
  filter(year == 2020) %>%
  arrange(desc(value)) %>%
  mutate(end_val = end_val) %>%
  mutate(gr = if_else(end_val == 0,
                      0, 
                      CAGR_calculator(starting_value = value,
                                      end_value = end_val,
                                      n = length(years))))

#FORECAST
scen_data <- run_forecast(historic_values = hist_vals,
                          starting_year = 2020,
                          list_of_growth_rates = growth_rates,
                          list_of_years = years,
                          list_of_regions = regions_filter,
                          scenario_name = "building_pri")

scen_data %>%
  ggplot(aes(x=year, y=value, group=region, color=region))+
  geom_line()+
  ggtitle("Building: Prioritarian")

#ADD TO EXPORT DF
export_df <- rbind(export_df, scen_data)


####----SCENARIO 3 BUILDING egal----####
#EGALITARIAN
#convergence at 45
growth_rates <- hist_vals %>%
  filter(year == 2020) %>%
  arrange(desc(value)) %>%
  mutate(end_val = 45) %>%
  mutate(gr = if_else(end_val == 0,
                      0, 
                      CAGR_calculator(starting_value = value,
                                      end_value = end_val,
                                      n = length(years))))

#FORECAST
scen_data <- run_forecast(historic_values = hist_vals,
                          starting_year = 2020,
                          list_of_growth_rates = growth_rates$gr,
                          list_of_years = years,
                          list_of_regions = regions_filter,
                          scenario_name = "building_ega")

scen_data %>%
  ggplot(aes(x=year, y=value, group=region, color=region))+
  geom_line()+
  ggtitle("Building: Egalitarian")

#ADD TO EXPORT DF
export_df <- rbind(export_df, scen_data)

####----SCENARIO 4 BUILDING suf----####
#countries above threshold stay constant, lowest reach threshold by 2040
#GET GROWTH RATES
##set growth rates individually via end value
##set end values in 2050; 0 means no change to present day
##set threshold
threshold = 30
end_val <-c(
  0,#North America; primarily the United States of America and Canada    
  0,#Pacific OECD                                                        
  0,#Countries of centrally-planned Asia; primarily China                
  0,#Eastern and Western Europe (i.e., the EU28)                         
  0,#Countries of Latin America and the Caribbean                        
  0,#Reforming Economies of Eastern Europe and the Former Soviet Union; …
  threshold,#Countries of the Middle East; Iran, Iraq, Israel, Saudi Arabia, Qat…
  threshold,#Countries of Sub-Saharan Africa                                     
  threshold#Countries of South Asia; primarily India  
)

#add growth rates
growth_rates <- hist_vals %>%
  filter(year == 2020) %>%
  arrange(desc(value)) %>%
  mutate(end_val = end_val) %>%
  mutate(gr = if_else(end_val == 0,
                      0, 
                      CAGR_calculator(starting_value = value,
                                      end_value = end_val,
                                      n = length(years)-2)))

#FORECAST
#create empty df
df_list <- list()
##add starting values
df_list[[1]] <- hist_vals %>% filter(year==2020)
##add starting index
index = 1
for (r in regions_list){
  index = index + 1 #iterate index
  new_df = forecaster(starting_year =  2020,
                      starting_value = filter(hist_vals, region == r, year==2020)$value,
                      years = years,
                      growth_rate = filter(growth_rates,region == r)$gr,
                      region = r)
  #change 2045 and 2050 values to threshold for affected years
  if (new_df$value[6] != new_df$value[5]){ #affected years grow until end
    new_df <- new_df %>%
      mutate(value = if_else(year %in% c(2045, 2050), as.numeric(threshold), as.numeric(value)))
    
  }
  #add to data list
  df_list[[index]] <- new_df
}

scen_data = do.call(rbind, df_list)

scen_data <- scen_data %>%
  #convert value column to numeric
  mutate(value = as.numeric(value)) %>%
  #add column to identify scenario
  mutate(scenario = "building_suf")%>%
  #add identifier at beginning of df
  relocate(scenario, .before = 1)


scen_data %>%
  ggplot(aes(x=year, y=value, group=region, color=region))+
  geom_line()+
  ggtitle("Building: Sufficitarian")+
  ylim(0, 100)

#ADD TO EXPORT DF
export_df <- rbind(export_df, scen_data)

####----SCENARIO 5 BUILDING lim----####
#countries below threshold stay constant, highest reach threshold by 2040
#GET GROWTH RATES
##set growth rates individually via end value
##set end values in 2050; 0 means no change to present day
##set threshold
threshold = 50
end_val <-c(
  threshold,#North America; primarily the United States of America and Canada    
  threshold,#Pacific OECD                                                        
  threshold,#Countries of centrally-planned Asia; primarily China                
  threshold,#Eastern and Western Europe (i.e., the EU28)                         
  0,#Countries of Latin America and the Caribbean                        
  0,#Reforming Economies of Eastern Europe and the Former Soviet Union; …
  0,#Countries of the Middle East; Iran, Iraq, Israel, Saudi Arabia, Qat…
  0,#Countries of Sub-Saharan Africa                                     
  0#Countries of South Asia; primarily India  
)

#add growth rates
growth_rates <- hist_vals %>%
  filter(year == 2020) %>%
  arrange(desc(value)) %>%
  mutate(end_val = end_val) %>%
  mutate(gr = if_else(end_val == 0,
                      0, 
                      CAGR_calculator(starting_value = value,
                                      end_value = end_val,
                                      n = length(years)-2)))

#FORECAST
#create empty df
df_list <- list()
##add starting values
df_list[[1]] <- hist_vals %>% filter(year==2020)
##add starting index
index = 1
for (r in regions_list){
  index = index + 1 #iterate index
  new_df = forecaster(starting_year =  2020,
                      starting_value = filter(hist_vals, region == r, year==2020)$value,
                      years = years,
                      growth_rate = filter(growth_rates,region == r)$gr,
                      region = r)
  #change 2045 and 2050 values to threshold for affected years
  if (new_df$value[6] != new_df$value[5]){ #affected years grow until end
    new_df <- new_df %>%
      mutate(value = if_else(year %in% c(2045, 2050), as.numeric(threshold), as.numeric(value)))
    
  }
  #add to data list
  df_list[[index]] <- new_df
}

scen_data = do.call(rbind, df_list)
#name scenario
scen_data <- scen_data %>%
  #convert value column to numeric
  mutate(value = as.numeric(value)) %>%
  #add column to identify scenario
  mutate(scenario = "building_lim")%>%
  #add identifier at beginning of df
  relocate(scenario, .before = 1)


scen_data %>%
  ggplot(aes(x=year, y=value, group=region, color=region))+
  geom_line()+
  ggtitle("Building: Limitarian")+
  ylim(0, 100)

#ADD TO EXPORT DF
export_df <- rbind(export_df, scen_data)

#-------------------------#
#           GDP           #
#-------------------------#
#load data
df = pyam$read_iiasa(
  'ar6-public',
  model='REMIND-MAgPIE 2.1-4.2',
  scenario='2.1-4.2_SusDev_SDP-PkBudg1000',
  variable=c('GDP|PPP','Population'),
  meta=c('category')
)
#units: GDP in billion US$2010/yr; Population in millions
#get right format
df = df$data

#check future trend
df %>%
  filter(((scenario == 'SusDev_SDP-PkBudg1000') & (region %in% regions_filter)))%>%
  select(region, variable, value, year)%>%
  pivot_wider(names_from = c("variable"), values_from = c("value")) %>%
  mutate(Population = Population * 1000000)%>%
  mutate(`GDP|PPP` = `GDP|PPP` * 1000000000)%>%
  mutate(gdp_pc = `GDP|PPP` / Population) %>%
  #filter(year==2050)
  ggplot(aes(x =  year, y = gdp_pc, color=region))+
  geom_line()

#get starting values
hist_data <- c("2005", "2010", "2015", "2020")
#look at historic values and add floor space per capita
hist_vals <- df %>%
  #filter on year, scenario and region
  filter((year %in% hist_data) & (scenario == 'SusDev_SDP-PkBudg1000') & (region %in% regions_filter)) %>%
  select(region, variable, value, year)%>%
  pivot_wider(names_from = c("variable"), values_from = c("value")) %>%
  rename(GDP = `GDP|PPP`)%>%
  #transform variables
  #from million to single
  mutate(Population = Population * 1000000)%>%
  #from billion to single
  mutate(GDP = GDP * 1000000000) %>%
  mutate(gdp_pc = GDP / Population)
#unit = GDP per capita per year

#limit hist_vals to gdp_pc only
hist_vals <- hist_vals %>%
  select(region, year, gdp_pc)%>%
  rename(value = gdp_pc)

hist_vals %>%
  ggplot(aes(x=year, y=value, color=region))+
  geom_line()


#specify years for scenarios
years <- c(2025, 2030, 2035, 2040, 2045, 2050)
#get regions for scenarios
regions_list <- unique(hist_vals$region)

####----SCENARIO 1 GDP aggu----####
#AGGREGATE UTILITARIAN
#GET GROWTH RATES
end_val <- hist_vals %>% filter(year == 2020) %>% mutate(value = value + 2000) %>%
  rename(end_val = value)

growth_rates <- hist_vals %>%
  filter(year == 2020) %>%
  arrange(desc(value)) %>%
  left_join(end_val, by = c("region")) %>%
  mutate(gr = if_else(end_val == 0,
                      0, 
                      LG_calculator(starting_value = value,
                                      end_value = end_val,
                                      n = length(years))))

#FORECAST
scen_data <- run_forecast(historic_values = hist_vals,
                          starting_year = 2020,
                          list_of_growth_rates = growth_rates,
                          list_of_years = years,
                          list_of_regions = regions_filter,
                          scenario_name = "gdp_agg")

scen_data %>%
  ggplot(aes(x=year, y=value, group=region, color=region))+
  geom_line()+
  ggtitle("GDP: Agg utilitarian ")+
  ylim(0, 70000)

#ADD TO EXPORT DF
export_df <- rbind(export_df, scen_data)


####----SCENARIO 2 GDP prio----####
#PRIORITARIAN
#GET GROWTH RATES
end_val <- c(
  0,#Based on scen data; North America; primarily the United States of America and…
  0,#Pacific OECD                                              
  0,#Eastern and Western Europe (i.e., the EU28)               
  0,#Countries of centrally-planned Asia; primarily China      
  16700,#Reforming Economies of Eastern Europe and the Former Sovi…
  15700,#Countries of Latin America and the Caribbean              
  14500,#Countries of the Middle East; Iran, Iraq, Israel, Saudi A…
  12000,#Countries of South Asia; primarily India                  
  10000#Countries of Sub-Saharan Africa  
)

growth_rates <- hist_vals %>%
  filter(year == 2020) %>%
  arrange(desc(value)) %>%
  mutate(end_val = end_val) %>%
  mutate(gr = if_else(end_val == 0,
                      0, 
                      LG_calculator(starting_value = value,
                                      end_value = end_val,
                                      n = length(years))))

#FORECAST
scen_data <- run_forecast(historic_values = hist_vals,
                          starting_year = 2020,
                          list_of_growth_rates = growth_rates,
                          list_of_years = years,
                          list_of_regions = regions_filter,
                          scenario_name = "gdp_pri")

scen_data %>%
  ggplot(aes(x=year, y=value, group=region, color=region))+
  geom_line()+
  ggtitle("GDP: Prioritarian")+
  ylim(0, 60000)

#ADD TO EXPORT DF
export_df <- rbind(export_df, scen_data)

####----SCENARIO 3 GDP egal----####
#convergence at 25.000
#GET GROWTH RATES
growth_rates <- hist_vals %>%
  filter(year == 2020) %>%
  arrange(desc(value)) %>%
  mutate(end_val = 25000) %>%
  mutate(gr = if_else(end_val == 0,
                      0, 
                      CAGR_calculator(starting_value = value,
                                      end_value = end_val,
                                      n = length(years))))

#FORECAST
scen_data <- run_forecast(historic_values = hist_vals,
                          starting_year = 2020,
                          list_of_growth_rates = growth_rates,
                          list_of_years = years,
                          list_of_regions = regions_filter,
                          scenario_name = "gdp_ega")

scen_data %>%
  ggplot(aes(x=year, y=value, group=region, color=region))+
  geom_line()+
  ggtitle("GDP: Egalitarian")

#ADD TO EXPORT DF
export_df <- rbind(export_df, scen_data)


####----SCENARIO 4 GDP suf----####
#countries above threshold stay constant, lowest reach threshold by 2040
#GET GROWTH RATES
##set growth rates individually via end value
##set end values in 2050; 0 means no change to present day
##set threshold
threshold = 15000
end_val = c(
  0, #Eastern and Western Europe (i.e., the EU28)
  0, #North America; primarily the United States of America and Canada
  0, #Countries of centrally-planned Asia; primarily China
  0, #Countries of the Middle East; Iran, Iraq, Israel, Saudi Arabia, Qatar, etc.
  0, #Countries of South Asia; primarily India
  threshold, #Countries of Latin America and the Caribbean
  threshold, #Reforming Economies of Eastern Europe and the Former Soviet Union; primarily Russia
  threshold, #Countries of Sub-Saharan Africa
  threshold) #Pacific OECD

#add growth rates
growth_rates <- hist_vals %>%
  filter(year == 2020) %>%
  arrange(desc(value)) %>%
  mutate(end_val = end_val) %>%
  mutate(gr = if_else(end_val == 0,
                      0, 
                      CAGR_calculator(starting_value = value,
                                      end_value = end_val,
                                      n = length(years)-2)))
#FORECAST
#create empty df
df_list <- list()
##add starting values
df_list[[1]] <- hist_vals %>% filter(year==2020)
##add starting index
index = 1
for (r in regions_list){
  index = index + 1 #iterate index
  new_df = forecaster(starting_year =  2020,
                      starting_value = filter(hist_vals, region == r, year==2020)$value,
                      years = years,
                      growth_rate = filter(growth_rates,region == r)$gr,
                      region = r)
  #change 2045 and 2050 values to threshold for affected years
  if (new_df$value[6] != new_df$value[5]){ #affected years grow until end
    new_df <- new_df %>%
      mutate(value = if_else(year %in% c(2045, 2050), as.numeric(threshold), as.numeric(value)))
    
  }
  #add to data list
  df_list[[index]] <- new_df
}

scen_data = do.call(rbind, df_list)
#name scenario
scen_data <- scen_data %>%
  #convert value column to numeric
  mutate(value = as.numeric(value)) %>%
  #add column to identify scenario
  mutate(scenario = "gdp_suf")%>%
  #add identifier at beginning of df
  relocate(scenario, .before = 1)


scen_data %>%
  ggplot(aes(x=year, y=value, group=region, color=region))+
  geom_line()+
  ggtitle("GDP: Sufficitarian")

#ADD TO EXPORT DF
export_df <- rbind(export_df, scen_data)

####----SCENARIO 5 GDP lim----####
#countries below threshold stay constant, highest reach threshold by 2040
#GET GROWTH RATES
##set growth rates individually via end value
##set end values in 2050; 0 means no change to present day
##set threshold
threshold = 35000
end_val <- c(
  threshold,#Based on scen data; North America; primarily the United States of America and…
  threshold,#Pacific OECD                                              
  threshold,#Eastern and Western Europe (i.e., the EU28)               
  0,#Countries of centrally-planned Asia; primarily China      
  0,#Reforming Economies of Eastern Europe and the Former Sovi…
  0,#Countries of Latin America and the Caribbean              
  0,#Countries of the Middle East; Iran, Iraq, Israel, Saudi A…
  0,#Countries of South Asia; primarily India                  
  0#Countries of Sub-Saharan Africa  
)

#add growth rates
growth_rates <- hist_vals %>%
  filter(year == 2020) %>%
  arrange(desc(value)) %>%
  mutate(end_val = end_val) %>%
  mutate(gr = if_else(end_val == 0,
                      0, 
                      CAGR_calculator(starting_value = value,
                                      end_value = end_val,
                                      n = length(years)-2)))

#FORECAST
#create empty df
df_list <- list()
##add starting values
df_list[[1]] <- hist_vals %>% filter(year==2020)
##add starting index
index = 1
for (r in regions_list){
  index = index + 1 #iterate index
  new_df = forecaster(starting_year =  2020,
                      starting_value = filter(hist_vals, region == r, year==2020)$value,
                      years = years,
                      growth_rate = filter(growth_rates,region == r)$gr,
                      region = r)
  #change 2045 and 2050 values to threshold for affected years
  if (new_df$value[6] != new_df$value[5]){ #affected years grow until end
    new_df <- new_df %>%
      mutate(value = if_else(year %in% c(2045, 2050), as.numeric(threshold), as.numeric(value)))
    
  }
  #add to data list
  df_list[[index]] <- new_df
}

scen_data = do.call(rbind, df_list)
#name scenario
scen_data <- scen_data %>%
  #convert value column to numeric
  mutate(value = as.numeric(value)) %>%
  #add column to identify scenario
  mutate(scenario = "gdp_lim")%>%
  #add identifier at beginning of df
  relocate(scenario, .before = 1)


scen_data %>%
  ggplot(aes(x=year, y=value, group=region, color=region))+
  geom_line()+
  ggtitle("GDP: Limitarian")

#ADD TO EXPORT DF
export_df <- rbind(export_df, scen_data)

#-------------------------#
#        NUTRITION        #
#-------------------------#
#starting vals from FAO 
#unit =  kCal meat consumption per day in 2018
hist_vals <- data.frame(
  region = c("Africa","China+","Europe","India+","Latin America","Middle East",
             "North America", "Pacific OECD","Reformed Economies"),
  year = rep(2018, 9),
  value = c(71.54330,480.77560,339.87086, 24.12279,354.55484, 130.56674,
            444.13868,247.16975,270.95007)
)
years <- c(2022, 2026, 2030, 2034, 2038, 2042, 2046, 2050)


####----SCENARIO 1 NUTRITION aggu----####
#AGGREGATE UTILITARIAN
#GET GROWTH RATES
end_val <- hist_vals %>% arrange(desc(value))%>% mutate(value = value+100) %>% select(value)

growth_rates <- hist_vals %>%
  arrange(desc(value)) %>%
  mutate(end_val = end_val) %>%
  mutate(gr = if_else(end_val$value == 0,
                      0, 
                      LG_calculator(starting_value = value,
                                      end_value = end_val$value,
                                      n = length(years))))

#FORECAST
scen_data <- run_forecast(historic_values = hist_vals,
                          starting_year = 2018,
                          list_of_growth_rates = growth_rates,
                          list_of_years = years,
                          list_of_regions = hist_vals$region,
                          scenario_name = "nutrition_agg")

scen_data %>%
  ggplot(aes(x=year, y=value, group=region, color=region))+
  geom_line()+
  ggtitle("Nutrition: Aggregate Uti")

#ADD TO EXPORT DF
export_df <- rbind(export_df, scen_data)

####----SCENARIO 2 NUTRITION prio----####
#PRIORITARIAN
#GET GROWTH RATES
end_val <- c(
  0,#China+
  0,#North America
  0,#Latin America
  0,#Europe
  300,#Reformed Economies
  285,#Pacific OECD
  240,#Middle East
  200,#Africa
  170#India+
)

growth_rates <- hist_vals %>%
  arrange(desc(value)) %>%
  mutate(end_val = end_val) %>%
  mutate(gr = if_else(end_val == 0,
                      0, 
                      CAGR_calculator(starting_value = value,
                                      end_value = end_val,
                                      n = length(years))))

#FORECAST
scen_data <- run_forecast(historic_values = hist_vals,
                          starting_year = 2018,
                          list_of_growth_rates = growth_rates,
                          list_of_years = years,
                          list_of_regions = hist_vals$region,
                          scenario_name = "nutrition_pri")

scen_data %>%
  ggplot(aes(x=year, y=value, group=region, color=region))+
  geom_line()+
  ggtitle("Nutrition: Prioritarian")+
  ylim(0, 700)

#ADD TO EXPORT DF
export_df <- rbind(export_df, scen_data)



####----SCENARIO 3 NUTRITION egal----####
#Convergence at 250
#GET GROWTH RATES
end_val <- c(
  90,#China+
  90,#North America
  90,#Latin America
  90,#Europe
  90,#Reformed Economies
  90,#Pacific OECD
  90,#Middle East
  90,#Africa
  90#India+
)

growth_rates <- hist_vals %>%
  arrange(desc(value)) %>%
  mutate(end_val = end_val) %>%
  mutate(gr = if_else(end_val == 0,
                      0, 
                      CAGR_calculator(starting_value = value,
                                      end_value = end_val,
                                      n = length(years))))

#FORECAST
scen_data <- run_forecast(historic_values = hist_vals,
                          starting_year = 2018,
                          list_of_growth_rates = growth_rates,
                          list_of_years = years,
                          list_of_regions = hist_vals$region,
                          scenario_name = "nutrition_ega")

scen_data %>%
  ggplot(aes(x=year, y=value, group=region, color=region))+
  geom_line()+
  ggtitle("Nutrition: Convergence")

#ADD TO EXPORT DF
export_df <- rbind(export_df, scen_data)


####----SCENARIO 4 NUTRITION suf----####
#countries above threshold stay constant, lowest reach threshold by 2040
#GET GROWTH RATES
##set growth rates individually via end value
##set end values in 2050; 0 means no change to present day
##set threshold
threshold = 75
end_val <- c(
  0,#China+
  0,#North America
  0,#Latin America
  0,#Europe
  0,#Reformed Economies
  0,#Pacific OECD
  0,#Middle East
  threshold,#Africa
  threshold#India+
)

#add growth rates
growth_rates <- hist_vals %>%
  filter(year == 2018) %>%
  arrange(desc(value)) %>%
  mutate(end_val = end_val) %>%
  mutate(gr = if_else(end_val == 0,
                      0, 
                      CAGR_calculator(starting_value = value,
                                      end_value = end_val,
                                      n = length(years)-2)))

#FORECAST
#create empty df
df_list <- list()
##add starting values
df_list[[1]] <- hist_vals %>% filter(year==2018)
##add starting index
index = 1
for (r in unique(hist_vals$region)){
  index = index + 1 #iterate index
  new_df = forecaster(starting_year =  2018,
                      starting_value = filter(hist_vals, region == r, year==2018)$value,
                      years = years,
                      growth_rate = filter(growth_rates,region == r)$gr,
                      region = r)
  
  if (new_df$value[6] != new_df$value[5]){ #affected years grow until end
    new_df <- new_df %>%
      mutate(value = if_else(year %in% c(2046, 2050), as.numeric(threshold), as.numeric(value)))
  }
  #add to data list
  df_list[[index]] <- new_df
}

scen_data = do.call(rbind, df_list)
#name scenario
scen_data <- scen_data %>%
  #convert value column to numeric
  mutate(value = as.numeric(value)) %>%
  #add column to identify scenario
  mutate(scenario = "nutrition_suf")%>%
  #add identifier at beginning of df
  relocate(scenario, .before = 1)


scen_data %>%
  ggplot(aes(x=year, y=value, group=region, color=region))+
  geom_line()+
  ggtitle("Nutrition: Sufficitarian")+
  ylim(0, 400)

#ADD TO EXPORT DF
export_df <- rbind(export_df, scen_data)


####----SCENARIO 5 NUTRITION lim----####
#countries below threshold stay constant, highest reach threshold by 2040
#GET GROWTH RATES
##set growth rates individually via end value
##set end values in 2050; 0 means no change to present day
##set threshold
threshold = 300
end_val <- c(
  threshold,#China+
  threshold,#North America
  threshold,#Latin America
  threshold,#Europe
  0,#Reformed Economies
  0,#Pacific OECD
  0,#Middle East
  0,#Africa
  0#India+
)

#add growth rates
growth_rates <- hist_vals %>%
  filter(year == 2018) %>%
  arrange(desc(value)) %>%
  mutate(end_val = end_val) %>%
  mutate(gr = if_else(end_val == 0,
                      0, 
                      CAGR_calculator(starting_value = value,
                                      end_value = end_val,
                                      n = length(years)-2)))

#FORECAST
#create empty df
df_list <- list()
##add starting values
df_list[[1]] <- hist_vals %>% filter(year==2018)
##add starting index
index = 1
for (r in unique(hist_vals$region)){
  index = index + 1 #iterate index
  new_df = forecaster(starting_year =  2018,
                      starting_value = filter(hist_vals, region == r, year==2018)$value,
                      years = years,
                      growth_rate = filter(growth_rates,region == r)$gr,
                      region = r)
  #change 2045 and 2050 values to threshold for affected years
  if (new_df$value[6] != new_df$value[5]){ #affected years grow until end
    new_df <- new_df %>%
      mutate(value = if_else(year %in% c(2046, 2050), as.numeric(threshold), as.numeric(value)))
    
  }
  #add to data list
  df_list[[index]] <- new_df
}

scen_data = do.call(rbind, df_list)
#name scenario
scen_data <- scen_data %>%
  #convert value column to numeric
  mutate(value = as.numeric(value)) %>%
  #add column to identify scenario
  mutate(scenario = "nutrition_lim")%>%
  #add identifier at beginning of df
  relocate(scenario, .before = 1)


scen_data %>%
  ggplot(aes(x=year, y=value, group=region, color=region))+
  geom_line()+
  ggtitle("Nutrition: Limitarian")+
  ylim(0, 500)

#ADD TO EXPORT DF
export_df <- rbind(export_df, scen_data)

#-------------------------#
#          EXPORT         #
#-------------------------#
write.csv(export_df,
          #IIASA
          "C:\\Users\\scheifinger\\OneDrive - IIASA\\Interactive Tools\\output.csv",
          #Home
          #"C:\\Users\\schei\\OneDrive - IIASA\\Interactive Tools\\Scenario Archetypes\\output.csv",
          row.names = FALSE)
