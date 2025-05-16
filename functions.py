# import pandas as pd
# import streamlit as st
# import plotly.graph_objects as go
# import io
# from datetime import datetime, timedelta

# def calculate_interval(data):
#     first_timestamp = datetime.strptime(data[0], "%d-%m-%Y %H:%M:%S")
#     second_timestamp = datetime.strptime(data[1], "%d-%m-%Y %H:%M:%S")
#     interval = (second_timestamp - first_timestamp).total_seconds() / 60
#     return int(interval)

# def adjust_timestamps(data):
#     interval_minutes = calculate_interval(data)
#     first_timestamp = datetime.strptime(data[0], "%d-%m-%Y %H:%M:%S")
#     rounded_start_time = first_timestamp.replace(minute=0, second=0, microsecond=0)
#     if first_timestamp.minute >= 30:
#         rounded_start_time += timedelta(hours=1)
    
#     adjusted_data = []
#     for idx, timestamp in enumerate(data):
#         current_timestamp = datetime.strptime(timestamp, "%d-%m-%Y %H:%M:%S")
#         time_difference = current_timestamp - first_timestamp
#         adjusted_timestamp = rounded_start_time + time_difference
#         adjusted_data.append(adjusted_timestamp.strftime("%d-%m-%Y %H:%M:%S"))
    
#     return adjusted_data

# def preprocess_excel(file):  
#     try:
#         df = pd.read_excel(file)
#         df = df.iloc[10:]
#         df.columns = df.iloc[0]
#         df = df[1:]
#         df = df.reset_index(drop=True)
#         df = df.dropna(axis=1, how='all')

#         if 'id' in df.columns:
#             df = df.set_index('id')
#         if 'Date/time' in df.columns:
#             df['Date/time'] = adjust_timestamps(df['Date/time'].tolist())
#         return df
    
#     except Exception as e:
        
#         print(f"Error preprocessing file: {e}")
#         return None




# def plot_all_sensors_streamlit(df):
    

#     temp_cols = [col for col in df.columns if 'TEMP' in col]
#     rh_cols = [col for col in df.columns if 'RH' in col]
#     fig_temp = go.Figure()
#     for col in temp_cols:
#         fig_temp.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=col))
#     fig_temp.update_layout(
#         title="All Temperatures from all Sensors",
#         xaxis_title="Date/Time",
#         yaxis_title="Temperature (°C)",
#     )
#     fig_temp.update_xaxes(tickformat="%Y-%m-%d %H:%M", tickangle=45)    
#     st.plotly_chart(fig_temp, use_container_width=True)

    
#     fig_rh = go.Figure()
#     for col in rh_cols:
#         fig_rh.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=col))
#     fig_rh.update_layout(
#         title="All RH from all Sensors",
#         xaxis_title="Date/Time",
#         yaxis_title="Relative Humidity (%)",
#     )
#     fig_rh.update_xaxes(tickformat="%Y-%m-%d %H:%M", tickangle=45)   
#     st.plotly_chart(fig_rh, use_container_width=True)


# def plot_sensor_data_streamlit_detailed(df):

#     temp_cols = [col for col in df.columns if 'TEMP' in col]
#     rh_cols = [col for col in df.columns if 'RH' in col]

   
#     for col in temp_cols:
#         fig = go.Figure()
#         fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=col))
#         fig.update_layout(
#             title=f"{col} Over Time",
#             xaxis_title="Date/Time",
#             yaxis_title="Temperature (°C)"
#         )
#         fig.update_xaxes(tickformat="%Y-%m-%d %H:%M", tickangle=90)  
#         st.plotly_chart(fig, use_container_width=True)

    
#     for col in rh_cols:
#         fig = go.Figure()
#         fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=col))
#         fig.update_layout(
#             title=f"{col} Over Time",
#             xaxis_title="Date/Time",
#             yaxis_title="Relative Humidity (%)"
#         )
#         fig.update_xaxes(tickformat="%Y-%m-%d %H:%M", tickangle=90)  
#         st.plotly_chart(fig, use_container_width=True)

# # def calculate_statistics(df):
    
# #     temp_cols = [col for col in df.columns if "TEMP" in col]
# #     rh_cols = [col for col in df.columns if "RH" in col]
    
# #     temp_stats = df[temp_cols].agg(["min", "max", "mean", "std"])
# #     rh_stats = df[rh_cols].agg(["min", "max", "mean", "std"])
    
# #     return temp_stats, rh_stats

# def calculate_statistics(df):
    
#     temp_cols = [col for col in df.columns if "TEMP" in col]
#     rh_cols = [col for col in df.columns if "RH" in col]

   
#     temp_stats = df[temp_cols].apply(pd.to_numeric, errors="coerce").dropna(axis=1, how="all").agg(
#         ["min", "max", "mean", "std"]
#     )
#     rh_stats = df[rh_cols].apply(pd.to_numeric, errors="coerce").dropna(axis=1, how="all").agg(
#         ["min", "max", "mean", "std"]
#     )
#     return temp_stats, rh_stats


import pandas as pd
from datetime import datetime, timedelta
import numpy as np # Added for MKT calculation
import plotly.graph_objects as go
# streamlit is not directly used in this file, but often imported alongside plotly if functions also render
# import streamlit as st # Not strictly needed here unless st calls are made directly in functions.py

# Constant for MKT calculation (as derived from the spreadsheet's "10000/x" logic)
# This represents Delta H / R in Kelvin
DEFAULT_DELTA_H_OVER_R = 10000.0

def calculate_interval(data):
    """
    Calculates the interval in minutes between the first two timestamps in a list.

    Args:
        data (list): A list of timestamp strings in "%d-%m-%Y %H:%M:%S" format.
                     Assumes at least two timestamps are present.

    Returns:
        int: The interval in minutes.
    """
    if len(data) < 2:
        # Or raise an error, or return a specific value like 0 or None
        print("Warning: Not enough data points to calculate interval. Returning 0.")
        return 0
    first_timestamp = datetime.strptime(data[0], "%d-%m-%Y %H:%M:%S")
    second_timestamp = datetime.strptime(data[1], "%d-%m-%Y %H:%M:%S")
    interval = (second_timestamp - first_timestamp).total_seconds() / 60
    return int(interval)

def adjust_timestamps(data):
    """
    Adjusts a list of timestamps. The first timestamp is rounded to the nearest hour,
    and subsequent timestamps are adjusted to maintain the original relative intervals.

    Args:
        data (list): A list of timestamp strings in "%d-%m-%Y %H:%M:%S" format.

    Returns:
        list: A list of adjusted timestamp strings.
              Returns original data if input data is empty or has less than 2 elements for interval calculation.
    """
    if not data:
        return []
    if len(data) < 2: # calculate_interval needs at least 2 to determine the original pattern
        # If only one timestamp, round it and return
        try:
            first_timestamp_dt = datetime.strptime(data[0], "%d-%m-%Y %H:%M:%S")
            rounded_start_time = first_timestamp_dt.replace(minute=0, second=0, microsecond=0)
            if first_timestamp_dt.minute >= 30:
                rounded_start_time += timedelta(hours=1)
            return [rounded_start_time.strftime("%d-%m-%Y %H:%M:%S")]
        except ValueError as e:
            print(f"Error parsing single timestamp: {data[0]} - {e}")
            return data # Return original if parsing fails

    # Calculate interval (not directly used for adjustment logic here but was in original)
    # interval_minutes = calculate_interval(data) # This line is not strictly needed for the adjustment logic below

    first_timestamp = datetime.strptime(data[0], "%d-%m-%Y %H:%M:%S")
    # Round the start time to the nearest hour
    rounded_start_time = first_timestamp.replace(minute=0, second=0, microsecond=0)
    if first_timestamp.minute >= 30:
        rounded_start_time += timedelta(hours=1)
    
    adjusted_data = []
    for timestamp_str in data:
        try:
            current_timestamp = datetime.strptime(timestamp_str, "%d-%m-%Y %H:%M:%S")
            # Calculate the difference from the original first timestamp
            time_difference = current_timestamp - first_timestamp
            # Add this difference to the new rounded start time
            adjusted_timestamp = rounded_start_time + time_difference
            adjusted_data.append(adjusted_timestamp.strftime("%d-%m-%Y %H:%M:%S"))
        except ValueError as e:
            print(f"Error parsing timestamp: {timestamp_str} - {e}. Skipping this timestamp.")
            adjusted_data.append(timestamp_str) # Append original if error
            
    return adjusted_data

def preprocess_excel(file):  
    """
    Preprocesses an uploaded Excel file.
    - Skips the first 10 rows.
    - Sets the 11th row as header.
    - Resets index.
    - Drops columns that are entirely NaN.
    - Sets 'id' column as index if it exists.
    - Adjusts timestamps in 'Date/time' column.

    Args:
        file (UploadedFile): An Excel file uploaded via Streamlit.

    Returns:
        pd.DataFrame or None: The preprocessed DataFrame, or None if an error occurs.
    """
    try:
        df = pd.read_excel(file)
        if df.shape[0] <= 10:
            print("Error: File has 10 or fewer rows. Cannot skip 10 rows and set header.")
            return None # Or handle as an empty DataFrame with expected columns
            
        df = df.iloc[10:] # Skip first 10 rows
        if df.empty:
            print("Error: DataFrame is empty after skipping initial rows.")
            return None

        df.columns = df.iloc[0] # Set the new first row as header
        df = df[1:] # Remove the header row from data
        df = df.reset_index(drop=True)
        df = df.dropna(axis=1, how='all') # Drop columns where all values are NaN

        if 'id' in df.columns:
            df = df.set_index('id')
        
        if 'Date/time' in df.columns:
            # Ensure 'Date/time' column is not empty and contains valid strings before adjusting
            date_time_list = df['Date/time'].astype(str).tolist() # Convert to string to be safe
            if date_time_list:
                 df['Date/time'] = adjust_timestamps(date_time_list)
            else:
                print("Warning: 'Date/time' column is empty. Skipping timestamp adjustment.")
        else:
            print("Warning: 'Date/time' column not found. Skipping timestamp adjustment.")
            
        return df
    
    except Exception as e:
        print(f"Error preprocessing file: {e}")
        return None


def plot_all_sensors_streamlit(df):
    """
    Plots all temperature and RH sensor data on two separate graphs in Streamlit.
    Assumes 'Date/time' is the index or a column that can be used for x-axis.
    If 'Date/time' is a column, it should be converted to datetime objects for proper plotting.

    Args:
        df (pd.DataFrame): The DataFrame containing sensor data.
                           It should have a 'Date/time' column or index for the x-axis.
    """
    if df.empty:
        # st.warning("Cannot plot: DataFrame is empty.") # If st is available
        print("Cannot plot: DataFrame is empty.")
        return

    # Determine x-axis: use 'Date/time' column if exists, otherwise use index
    x_axis_data = df.index
    if 'Date/time' in df.columns:
        try:
            # Attempt to convert 'Date/time' to datetime objects for better plotting
            x_axis_data = pd.to_datetime(df['Date/time'], format="%d-%m-%Y %H:%M:%S", errors='coerce')
            if x_axis_data.isnull().all(): # If all conversions fail, fall back to index
                print("Warning: Could not parse 'Date/time' column for plotting. Using index.")
                x_axis_data = df.index
        except Exception as e:
            print(f"Error converting 'Date/time' for plotting, using index: {e}")
            x_axis_data = df.index


    temp_cols = [col for col in df.columns if isinstance(col, str) and 'TEMP' in col]
    rh_cols = [col for col in df.columns if isinstance(col, str) and 'RH' in col]

    if temp_cols:
        fig_temp = go.Figure()
        for col in temp_cols:
            # Ensure data is numeric for plotting
            y_data = pd.to_numeric(df[col], errors='coerce')
            fig_temp.add_trace(go.Scatter(x=x_axis_data, y=y_data, mode='lines', name=col))
        fig_temp.update_layout(
            title="All Temperatures from all Sensors",
            xaxis_title="Date/Time",
            yaxis_title="Temperature (°C)",
        )
        fig_temp.update_xaxes(tickformat="%Y-%m-%d %H:%M", tickangle=45)    
        st.plotly_chart(fig_temp, use_container_width=True)
    else:
        # st.info("No temperature (TEMP) data to plot.") # If st is available
        print("No temperature (TEMP) data to plot.")


    if rh_cols:
        fig_rh = go.Figure()
        for col in rh_cols:
            y_data = pd.to_numeric(df[col], errors='coerce')
            fig_rh.add_trace(go.Scatter(x=x_axis_data, y=y_data, mode='lines', name=col))
        fig_rh.update_layout(
            title="All RH from all Sensors",
            xaxis_title="Date/Time",
            yaxis_title="Relative Humidity (%)",
        )
        fig_rh.update_xaxes(tickformat="%Y-%m-%d %H:%M", tickangle=45)    
        st.plotly_chart(fig_rh, use_container_width=True)
    else:
        # st.info("No relative humidity (RH) data to plot.") # If st is available
        print("No relative humidity (RH) data to plot.")


def plot_sensor_data_streamlit_detailed(df):
    """
    Plots detailed graphs for each temperature and RH sensor in Streamlit.
    Assumes 'Date/time' is the index or a column that can be used for x-axis.

    Args:
        df (pd.DataFrame): The DataFrame containing sensor data.
    """
    if df.empty:
        # st.warning("Cannot plot detailed data: DataFrame is empty.") # If st is available
        print("Cannot plot detailed data: DataFrame is empty.")
        return

    x_axis_data = df.index
    if 'Date/time' in df.columns:
        try:
            x_axis_data = pd.to_datetime(df['Date/time'], format="%d-%m-%Y %H:%M:%S", errors='coerce')
            if x_axis_data.isnull().all():
                print("Warning: Could not parse 'Date/time' for detailed plots. Using index.")
                x_axis_data = df.index
        except Exception as e:
            print(f"Error converting 'Date/time' for detailed plotting, using index: {e}")
            x_axis_data = df.index
            
    temp_cols = [col for col in df.columns if isinstance(col, str) and 'TEMP' in col]
    rh_cols = [col for col in df.columns if isinstance(col, str) and 'RH' in col]

    for col in temp_cols:
        fig = go.Figure()
        y_data = pd.to_numeric(df[col], errors='coerce')
        fig.add_trace(go.Scatter(x=x_axis_data, y=y_data, mode='lines', name=col))
        fig.update_layout(
            title=f"{col} Over Time",
            xaxis_title="Date/Time",
            yaxis_title="Temperature (°C)"
        )
        fig.update_xaxes(tickformat="%Y-%m-%d %H:%M", tickangle=90)  
        st.plotly_chart(fig, use_container_width=True)

    for col in rh_cols:
        fig = go.Figure()
        y_data = pd.to_numeric(df[col], errors='coerce')
        fig.add_trace(go.Scatter(x=x_axis_data, y=y_data, mode='lines', name=col))
        fig.update_layout(
            title=f"{col} Over Time",
            xaxis_title="Date/Time",
            yaxis_title="Relative Humidity (%)"
        )
        fig.update_xaxes(tickformat="%Y-%m-%d %H:%M", tickangle=90)  
        st.plotly_chart(fig, use_container_width=True)

def calculate_statistics(df):
    """
    Calculates min, max, mean, and std deviation for temperature and RH columns.

    Args:
        df (pd.DataFrame): The DataFrame containing sensor data.

    Returns:
        tuple: (temp_stats_df, rh_stats_df)
               DataFrames containing statistics for temperature and RH.
               Returns empty DataFrames if no relevant columns are found or if data is non-numeric.
    """
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    temp_cols = [col for col in df.columns if isinstance(col, str) and "TEMP" in col]
    rh_cols = [col for col in df.columns if isinstance(col, str) and "RH" in col]

    temp_stats = pd.DataFrame()
    if temp_cols:
        # Apply to_numeric to each column individually to handle potential errors
        numeric_temp_df = df[temp_cols].apply(lambda x: pd.to_numeric(x, errors='coerce'))
        # Drop columns that are entirely NaN after conversion (e.g., if a column was all text)
        numeric_temp_df = numeric_temp_df.dropna(axis=1, how='all')
        if not numeric_temp_df.empty:
            temp_stats = numeric_temp_df.agg(["min", "max", "mean", "std"])

    rh_stats = pd.DataFrame()
    if rh_cols:
        numeric_rh_df = df[rh_cols].apply(lambda x: pd.to_numeric(x, errors='coerce'))
        numeric_rh_df = numeric_rh_df.dropna(axis=1, how='all')
        if not numeric_rh_df.empty:
            rh_stats = numeric_rh_df.agg(["min", "max", "mean", "std"])
            
    return temp_stats, rh_stats

# --- MKT Calculation Functions ---
def calculate_single_mkt(series, delta_h_over_r=DEFAULT_DELTA_H_OVER_R):
    """
    Calculates the Mean Kinetic Temperature (MKT) for a single series of readings
    based on the formula derived from the provided spreadsheet logic.

    The derived formula is:
    MKT_K = delta_h_over_r / ln(mean(exp(delta_h_over_r / K_i)))
    MKT_C = MKT_K - 273.15

    Args:
        series (pd.Series): A pandas Series of readings.
                            If temperatures, assumed to be in Celsius.
                            For RH values, they will be treated similarly by adding 273.15.
        delta_h_over_r (float): The activation energy divided by the gas constant (in Kelvin).
                                 Default is 10000 K.

    Returns:
        float: The MKT value (typically in Celsius if input is Celsius).
               Returns np.nan if calculation is not possible.
    """
    # Ensure data is numeric and drop NaNs.
    numeric_series = pd.to_numeric(series, errors='coerce').dropna()
    if numeric_series.empty:
        return np.nan

    # Convert readings to Kelvin.
    kelvin_values = numeric_series + 273.15

    # Filter out non-positive Kelvin values
    kelvin_values = kelvin_values[kelvin_values > 0]
    if kelvin_values.empty:
        return np.nan

    # Calculate exp(delta_h_over_r / K_i)
    exp_terms = np.exp(delta_h_over_r / kelvin_values)

    # Calculate the mean of these exponential terms.
    mean_exp_terms = np.mean(exp_terms)

    if not np.isfinite(mean_exp_terms) or mean_exp_terms <= 0:
        if np.isinf(mean_exp_terms) and mean_exp_terms > 0:
            log_mean_exp_terms = np.inf
        else:
            return np.nan
    else:
        log_mean_exp_terms = np.log(mean_exp_terms)

    if not np.isfinite(log_mean_exp_terms) or log_mean_exp_terms == 0:
        if np.isinf(log_mean_exp_terms) and log_mean_exp_terms > 0:
            mkt_kelvin = 0.0
        else:
            return np.nan
    else:
        mkt_kelvin = delta_h_over_r / log_mean_exp_terms

    mkt_final_unit = mkt_kelvin - 273.15
    return mkt_final_unit

def calculate_mkt_for_df(df, delta_h_over_r=DEFAULT_DELTA_H_OVER_R):
    """
    Calculates Mean Kinetic Temperature (MKT) for all temperature ('TEMP')
    and relative humidity ('RH') columns in the provided DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame containing sensor data.
        delta_h_over_r (float): The specific constant (Delta H / R) to be used, in Kelvin.

    Returns:
        pd.DataFrame: A DataFrame with MKT values. Index: 'MKT_calculated_Celsius'.
                      Columns: Original 'TEMP' and 'RH' column names.
                      Returns an empty DataFrame if no relevant columns or data.
    """
    mkt_results = {}
    if df.empty:
        return pd.DataFrame(index=['MKT_calculated_Celsius'])

    temp_cols = [col for col in df.columns if isinstance(col, str) and 'TEMP' in col]
    rh_cols = [col for col in df.columns if isinstance(col, str) and 'RH' in col]
    all_relevant_cols = temp_cols + rh_cols

    if not all_relevant_cols:
        return pd.DataFrame(index=['MKT_calculated_Celsius'])

    for col_name in all_relevant_cols:
        if col_name in df:
            series = df[col_name]
            numeric_series = pd.to_numeric(series, errors='coerce')
            if numeric_series.isnull().all():
                mkt_results[col_name] = np.nan
            else:
                mkt_results[col_name] = calculate_single_mkt(numeric_series, delta_h_over_r)
        else: # Should not happen if cols are from df.columns
             mkt_results[col_name] = np.nan


    if not mkt_results: # If no columns were processed (e.g. all were non-numeric)
        return pd.DataFrame(index=['MKT_calculated_Celsius'])
        
    mkt_df = pd.DataFrame.from_dict(mkt_results, orient='index', columns=['MKT_calculated_Celsius'])
    return mkt_df.transpose()
