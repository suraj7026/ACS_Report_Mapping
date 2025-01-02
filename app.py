import streamlit as st
import pandas as pd
from functions import *

# Set page configuration to wide layout and light mode
st.set_page_config(layout="wide", page_title="ACS Report Mapping", initial_sidebar_state="expanded")


st.title("ACS Report Mapping")

# Create a file uploader for multiple Excel files
uploaded_files = st.file_uploader("Drop your Excel files here", type=["xls", "xlsx"], accept_multiple_files=True)

# Display the count of uploaded files
if uploaded_files:
     st.warning(f"**You have uploaded {len(uploaded_files)} file(s).**")  

# Add an upload button to process files
if uploaded_files:
    if st.button("Upload Files"):
        dfs = []  # List to hold preprocessed DataFrames

        for uploaded_file in uploaded_files:
            try:
                # Preprocess the uploaded Excel file
                df = preprocess_excel(uploaded_file)
                if df is not None:
                    new_cols = {col: f"{uploaded_file.name}_{col}" for col in df.columns if col not in ['Date/time']}
                    df = df.rename(columns=new_cols)
                    dfs.append(df)
            except Exception as e:
                st.error(f"Error processing file {uploaded_file.name}: {e}")
                continue

        if dfs:
            merged_df = dfs[0]
            for df in dfs[1:]:
                if 'Date/time' in merged_df.columns and 'Date/time' in df.columns:
                    try:
                        merged_df = pd.merge(merged_df, df, on='Date/time', how='outer')
                    except Exception as e:
                        st.error(f"Error merging dataframes: {e}")
                        continue
                else:
                    st.warning("Warning: 'Date/time' column not found in one or more DataFrames.")

            if 'Unnamed: 0' in merged_df.columns:
                merged_df = merged_df.drop(columns=['Unnamed: 0'])

            # Display the merged DataFrame
            st.write("### Annexure Sheet")
            st.dataframe(merged_df)
            if not merged_df.empty:
                st.header("Sensor Data Graphs")
                plot_sensor_data_streamlit_detailed(merged_df)
                plot_all_sensors_streamlit(merged_df)
                temp_stats, rh_stats = calculate_statistics(merged_df)

                # Display DataFrames
                st.subheader("Temperature Statistics")
                st.dataframe(temp_stats)

                st.subheader("Relative Humidity (RH) Statistics")
                st.dataframe(rh_stats)
        else:
            st.warning("No valid DataFrames to merge.")
