#Importing Dependencies 
import streamlit as st
import pandas as pd
import streamlit_option_menu
from streamlit_option_menu import option_menu
import squarify
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import date
import random

#Data Load
claimTable = pd.read_excel("/Users/geyne/Desktop/CrabiTest/DataBase/claim.xlsx").convert_dtypes()
peopleTable = pd.read_excel("/Users/geyne/Desktop/CrabiTest/DataBase/people.xlsx").convert_dtypes()
ServiceTable = pd.read_excel("/Users/geyne/Desktop/CrabiTest/DataBase/service.xlsx").convert_dtypes()
StatusTypeTable = pd.read_excel("/Users/geyne/Desktop/CrabiTest/DataBase/status_type.xlsx").convert_dtypes()
StatusTable = pd.read_excel("/Users/geyne/Desktop/CrabiTest/DataBase/status.xlsx").convert_dtypes()
#Def constants
PrimasDevengadas = 200000
Deducible = 100000 * 0.05
hoy = pd.Timestamp("today")

#Defininng Data Frames
df_Service = ServiceTable
df_people = peopleTable
df_Claim = claimTable
df_StatusType = StatusTypeTable
df_Status = StatusTable
#Cleaning Status 
df_Status = df_Status[["id","status_type_id","name"]]
#Cleaning Status Type
df_StatusType =df_StatusType[["id","name"]]
#merging table Status with status_Type
df_Status = df_Status.merge(df_StatusType,left_on="status_type_id",right_on="id",how="left")
df_Status = df_Status.rename(columns={'id_x':'type_status_id','name_x':'Status Name','name_y':'Status Type'})
df_Status = df_Status.drop(columns=['status_type_id','id_y'])
#cleaning Service and merging with Status
df_Service.fillna({"amount":0}, inplace=True)
df_Service = df_Service.merge(df_Status,on='type_status_id',how='left')
df_Service = df_Service.drop(columns=['type_status_id','provider_id','subprovider_id','description','created_by','seq','created_at','updated_at'])
#Cleaning People 
df_people = df_people.drop(columns=['type_status_id','license_id','vehicle_id','address_id','cancelled_at','created_by','created_at','updated_at','phone'])
df_people['Nombre'] = df_people['first_name'].fillna(" ").astype("string") + ' ' + df_people['first_last_name'].fillna(" ").astype("string")  + ' ' + df_people['second_last_name'].fillna(" ").astype("string") 
df_people = df_people.drop(columns=['first_name','first_last_name','second_last_name'])
df_people['gender'] = df_people['gender'].fillna('Not Defined')
df_people['birthdate'] = df_people['birthdate'].fillna('Not Defined')
df_people['email'] = df_people['email'].fillna('Not Defined')
#Merging Service with people
df_Service  = df_Service.merge(df_people, left_on='people_id',right_on='id',how="left")
df_Service = df_Service.drop(columns=['id_x','number','id_y','Status Type','policy_id','people_id','gender','Nombre','email','birthdate'])
#En caso de que no exista amount en el servicio, ignorar el servicio para el cálculo de la siniestralidad.
df_Service = df_Service[df_Service['amount']!=0]
#Service apply coverage?
df_Service["Cobertura"] = np.where(
    df_Service["coverage_id"].notna(),
    True,
    False)
df_Service = df_Service.drop(columns=['coverage_id'])
orden = [ 'claim_id','Status Name','amount','deductible','Cobertura']
df_Service = df_Service[orden]
#Amount after deductible and Coverage
df_Service['Amount After conditions'] = np.where(
    (df_Service['deductible'] == True) & (df_Service['Cobertura'] == True),
    #deducibl is Positive here because this is an income for Crabi
    df_Service['amount']+ Deducible,
    df_Service['amount']
)
df_Service = df_Service.sort_values(by=['claim_id'],ascending=True)
#Calculating Severity by Grouping Claim ID
df_severity = (
    df_Service
        .groupby("claim_id", as_index=False)["Amount After conditions"]
        .sum()
        .rename(columns={"Amount After conditions": "Severidad"})
)
df_severity["Severidad"] = pd.to_numeric(
    df_severity["Severidad"],
    errors="coerce"
)
df_severity['Severidad'].describe()
#Eliminando columnas
df_Claim = df_Claim.drop(columns=
                         ['address_id',
                          'original_claim_id',
                          'liability_status_id',
                          'cancelled_reason_status_id',
                          'seq',
                          'policy_id',
                          'created_by',
                          'declaration_cabin',
                          'reporting_name',
                          'third_car_description',
                          'conclusion',
                          'reporting_phone',
                          'scheduled_at',
                          'updated_at',
                          'amis_reported_at',
                          'declaration',
                          ])
#Merge Claim to severity table
df_Claim = df_Claim.merge(df_severity,left_on='id',right_on='claim_id',how='left')
df_Claim = df_Claim.drop(columns=['id','claim_id'])
df_Claim = df_Claim.merge(df_Status,left_on='type_status_id',right_on='type_status_id',how='left')
df_Claim = df_Claim.drop(columns = ['type_status_id','status_cause_type_id','policy_person_id','occurred_at'])
df_Claim['Severidad'] = df_Claim['Severidad'].fillna(0)
def boxPlot(df):
    fig, ax = plt.subplots()
    ax.boxplot(df["Severidad"].dropna())
    ax.set_title("Boxplot de Severidad")
    ax.set_ylabel("Severidad")
    return fig

#calculando Percentiles
Q1 = df_Claim["Severidad"].quantile(0.25)
Q3 = df_Claim["Severidad"].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
#Calculando DF Outliers
outliers = df_Claim[
    (df_Claim["Severidad"] < lower_bound) |
    (df_Claim["Severidad"] > upper_bound)
]
df_sin_outliers = df_Claim[
    (df_Claim["Severidad"] >= lower_bound) &
    (df_Claim["Severidad"] <= upper_bound)
]
def boxplotWithoutoutliers(df):
    fig, ax = plt.subplots()
    ax.boxplot(df["Severidad"].dropna())
    ax.set_title("Boxplot de Severidad (Sin outliers)")
    ax.set_ylabel("Severidad")
    return fig

def histogram(df):  
    data = df.loc[df["Severidad"] < 0, "Severidad"]

    mean = data.mean()
    median = data.median()

    fig, ax = plt.subplots()
    ax.hist(data, bins=20)

    ax.axvline(mean, linestyle="--", linewidth=2, label=f"Media: {mean:,.0f}")
    ax.axvline(median, linestyle="-", linewidth=2, label=f"Mediana: {median:,.0f}")

    ax.set_title("Histograma de Severidad (Costos)")
    ax.set_xlabel("Severidad")
    ax.set_ylabel("Frecuencia")
    ax.legend()
    return fig
#--------------------------------------------CLAIMS BY COVERAGE--------------------------------------------------
# Definiendo Nuevos Data Frames 
df_Service_claim = ServiceTable
#Merging Service table with Status
df_Service_claim = df_Service_claim.merge(df_Status,left_on='coverage_id',right_on='type_status_id',how='left')
#Merging new Service with People
df_Service_claim = df_Service_claim.merge(df_people,left_on='people_id',right_on='id',how='left')
#Cleaning Columns 
cols = ['claim_id','Status Type','Status Name']
df_Service_claim= df_Service_claim[cols]
#Creating new Data frame for Clame table called: claim coverage 
df_Claim_coverage = claimTable
#Merging new table with Claim 
df_Claim_coverage = df_Claim_coverage.merge(df_Service_claim,left_on='id',right_on='claim_id',how='left')
cols = ['number','policy_number','Status Type','Status Name']
df_Claim_coverage = df_Claim_coverage[cols]
df_Claim_coverage.convert_dtypes()
#Filtrando by CoverageType
df_Claim_coverage = df_Claim_coverage[df_Claim_coverage['Status Type'] == 'CoverageType']
#Grouping by Status Name 
coverage_counts = (
    df_Claim_coverage
        .groupby('Status Name')
        .size()
        .reset_index(name='num_claims')
        .sort_values('num_claims', ascending=False)
)
#Plotting  Number of claims
def bar_claims_by_coverage(df):
    fig, ax = plt.subplots()

    ax.bar(
        df['Status Name'],
        df['num_claims']
    )

    ax.set_xlabel('Coverage Type')
    ax.set_ylabel('Number of Claims')
    ax.set_title('Number of Claims by Coverage Type')

    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig
#----------------------------------------------Rango Etario------------------------------------------------------
#Defining new data Frames
df_Claim_Age = claimTable
df_people_Age = peopleTable
df_service_Age = ServiceTable
#Cleaning Cols 
cols = ['id','number']
df_Claim_Age = df_Claim_Age[cols]
#Merging with Service Table
df_Claim_Age = df_Claim_Age.merge(df_people_Age,left_on='id',right_on='claim_id',how='inner')

#Cleaning cols 
cols = ['number','id_y','type_status_id','first_name','birthdate']
df_Claim_Age = df_Claim_Age[cols]

#Merging with status, Mi hipotesis es que los Status Name NA son los Asegurados de Crabi 
df_Claim_Age = df_Claim_Age.merge(df_Status,left_on='type_status_id',right_on='type_status_id',how='left')
df_Claim_Age['Status Name']= df_Claim_Age['Status Name'].fillna('Asegurado De Crabi')

#Merging with Service
df_Claim_Age = df_Claim_Age.merge(df_service_Age,left_on='id_y',right_on='people_id',how='inner')

#Cleaning table
cols = ['number_x','first_name','birthdate','Status Name','Status Type','amount','deductible']
df_Claim_Age = df_Claim_Age[cols]
#Calculando edad
df_Claim_Age['birthdate'] = pd.to_datetime(df_Claim_Age['birthdate'])
df_Claim_Age['edad'] = np.where(
df_Claim_Age['birthdate'].notna(),
#Si no es NA calcula la diferencia de hoy entre la fecha de naciemiento
hoy.year -df_Claim_Age['birthdate'].dt.year,
#Si es 0 escoge un numero al azar del 0 al 90
random.randint(0,90)
)
def age_range_distribution(df_Claim_Age):
    df_Claim_Age["edad"] = pd.to_numeric(df_Claim_Age["edad"], errors="coerce")

    # Defining bins and labels
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 120]
    labels = ["0-9","10-19","20-29","30-39","40-49","50-59","60-69","70-79","80+"]

    df_Claim_Age["rango_etario"] = pd.cut(
        df_Claim_Age["edad"],
        bins=bins,
        labels=labels,
        right=False
    )

    order = df_Claim_Age["rango_etario"].value_counts().sort_index()

    fig, ax = plt.subplots()
    ax.bar(order.index.astype(str), order.values)

    ax.set_title("Distribución por rango etario")
    ax.set_xlabel("Rango etario")
    ax.set_ylabel("Número de personas")

    plt.tight_layout()

    return fig



#------------------------------------------------STREAMLIT APP----------------------------------------------------


with st.sidebar:
    st.image("/Users/geyne/Desktop/CrabiTest/Images/unnamed.png", width=180)

    selected = option_menu(
        menu_title="Crabi Menu",
        options=["Daily Dashboard"],
        icons=["bar-chart"],
        menu_icon="cast",
        default_index=0,
    )

if selected == "Daily Dashboard":
    st.title("Crabi – Daily Dashboard")

    col1, col2 = st.columns(2)
    with col1:
        st.pyplot(boxPlot(df_Claim))

    with col2:
        st.pyplot(boxplotWithoutoutliers(df_sin_outliers))

    st.pyplot(histogram(df_sin_outliers))

    st.title("¿Cuál es la cobertura con mayor y menor cantidad de siniestros?")
    st.pyplot(bar_claims_by_coverage(coverage_counts))
    st.markdown("""
                * La cobertura con mas incidencias es Danos Materiales con 220 incidencias 
                * La cobertura con menos incidencias es Robo Total con 8 claims 
                """)
    st.title("¿Dentro de qué rango etario se encuentra la mayor y menor cantidad de usuarios siniestrados?")
    st.pyplot(age_range_distribution(df_Claim_Age))
    st.markdown("""
                * El rango Etario de personas que mas incidencia tienen es el de 30 a 39, seguido del rango 50-59
                * El rango Etario con menos incidencias es de 40-49 
                """)



    
