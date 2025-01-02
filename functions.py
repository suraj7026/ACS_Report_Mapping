import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import io
from datetime import datetime, timedelta

def calculate_interval(data):
    first_timestamp = datetime.strptime(data[0], "%d-%m-%Y %H:%M:%S")
    second_timestamp = datetime.strptime(data[1], "%d-%m-%Y %H:%M:%S")
    interval = (second_timestamp - first_timestamp).total_seconds() / 60
    return int(interval)

def adjust_timestamps(data):
    interval_minutes = calculate_interval(data)
    first_timestamp = datetime.strptime(data[0], "%d-%m-%Y %H:%M:%S")
    rounded_start_time = first_timestamp.replace(minute=0, second=0, microsecond=0)
    if first_timestamp.minute >= 30:
        rounded_start_time += timedelta(hours=1)
    
    adjusted_data = []
    for idx, timestamp in enumerate(data):
        current_timestamp = datetime.strptime(timestamp, "%d-%m-%Y %H:%M:%S")
        time_difference = current_timestamp - first_timestamp
        adjusted_timestamp = rounded_start_time + time_difference
        adjusted_data.append(adjusted_timestamp.strftime("%d-%m-%Y %H:%M:%S"))
    
    return adjusted_data

def preprocess_excel(file):  
    try:
        df = pd.read_excel(file)
        df = df.iloc[10:]
        df.columns = df.iloc[0]
        df = df[1:]
        df = df.reset_index(drop=True)
        df = df.dropna(axis=1, how='all')

        if 'id' in df.columns:
            df = df.set_index('id')
        if 'Date/time' in df.columns:
            df['Date/time'] = adjust_timestamps(df['Date/time'].tolist())
        return df
    
    except Exception as e:
        
        print(f"Error preprocessing file: {e}")
        return None




def plot_all_sensors_streamlit(df):
    

    temp_cols = [col for col in df.columns if 'TEMP' in col]
    rh_cols = [col for col in df.columns if 'RH' in col]
    fig_temp = go.Figure()
    for col in temp_cols:
        fig_temp.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=col))
    fig_temp.update_layout(
        title="All Temperatures from all Sensors",
        xaxis_title="Date/Time",
        yaxis_title="Temperature (°C)",
    )
    fig_temp.update_xaxes(tickformat="%Y-%m-%d %H:%M", tickangle=45)    
    st.plotly_chart(fig_temp, use_container_width=True)

    
    fig_rh = go.Figure()
    for col in rh_cols:
        fig_rh.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=col))
    fig_rh.update_layout(
        title="All RH from all Sensors",
        xaxis_title="Date/Time",
        yaxis_title="Relative Humidity (%)",
    )
    fig_rh.update_xaxes(tickformat="%Y-%m-%d %H:%M", tickangle=45)   
    st.plotly_chart(fig_rh, use_container_width=True)


def plot_sensor_data_streamlit_detailed(df):

    temp_cols = [col for col in df.columns if 'TEMP' in col]
    rh_cols = [col for col in df.columns if 'RH' in col]

   
    for col in temp_cols:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=col))
        fig.update_layout(
            title=f"{col} Over Time",
            xaxis_title="Date/Time",
            yaxis_title="Temperature (°C)"
        )
        fig.update_xaxes(tickformat="%Y-%m-%d %H:%M", tickangle=90)  
        st.plotly_chart(fig, use_container_width=True)

    
    for col in rh_cols:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=col))
        fig.update_layout(
            title=f"{col} Over Time",
            xaxis_title="Date/Time",
            yaxis_title="Relative Humidity (%)"
        )
        fig.update_xaxes(tickformat="%Y-%m-%d %H:%M", tickangle=90)  
        st.plotly_chart(fig, use_container_width=True)

# def calculate_statistics(df):
    
#     temp_cols = [col for col in df.columns if "TEMP" in col]
#     rh_cols = [col for col in df.columns if "RH" in col]
    
#     temp_stats = df[temp_cols].agg(["min", "max", "mean", "std"])
#     rh_stats = df[rh_cols].agg(["min", "max", "mean", "std"])
    
#     return temp_stats, rh_stats

def calculate_statistics(df):
    
    temp_cols = [col for col in df.columns if "TEMP" in col]
    rh_cols = [col for col in df.columns if "RH" in col]

   
    temp_stats = df[temp_cols].apply(pd.to_numeric, errors="coerce").dropna(axis=1, how="all").agg(
        ["min", "max", "mean", "std"]
    )
    rh_stats = df[rh_cols].apply(pd.to_numeric, errors="coerce").dropna(axis=1, how="all").agg(
        ["min", "max", "mean", "std"]
    )
    return temp_stats, rh_stats
