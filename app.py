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

                try:
                    st.subheader("Summary of Statistics")

                    # Overall Min and Max
                    overall_min_temp_value = temp_stats.loc['min'].min()
                    overall_min_temp_sensor = temp_stats.loc['min'].idxmin()
                    overall_max_temp_value = temp_stats.loc['max'].max()
                    overall_max_temp_sensor = temp_stats.loc['max'].idxmax()

                    # Display overall min and max temperature with sensor details
                    st.markdown("### Overall Temperature Summary")
                    st.write(f"**Overall Min Temperature:** {overall_min_temp_value} from Sensor: {overall_min_temp_sensor}")
                    st.write(f"**Overall Max Temperature:** {overall_max_temp_value} from Sensor: {overall_max_temp_sensor}")

                    # Overall Min and Max for RH
                    overall_min_rh_value = rh_stats.loc['min'].min()
                    overall_min_rh_sensor = rh_stats.loc['min'].idxmin()
                    overall_max_rh_value = rh_stats.loc['max'].max()
                    overall_max_rh_sensor = rh_stats.loc['max'].idxmax()

                    # Display overall min and max RH with sensor details
                    st.markdown("### Overall Relative Humidity (RH) Summary")
                    st.write(f"**Overall Min RH:** {overall_min_rh_value} from Sensor: {overall_min_rh_sensor}")
                    st.write(f"**Overall Max RH:** {overall_max_rh_value} from Sensor: {overall_max_rh_sensor}")

                except KeyError as e:
                    st.error(f"KeyError: Could not calculate summary statistics. Missing key: {e}")
                except Exception as e:
                    st.error(f"An error occurred while summarizing statistics: {e}")

        else:
            st.warning("No valid DataFrames to merge.")
