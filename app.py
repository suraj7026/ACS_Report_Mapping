import streamlit as st
import pandas as pd
from functions import *

# # Set page configuration to wide layout and light mode
# st.set_page_config(layout="wide", page_title="ACS Report Mapping", initial_sidebar_state="expanded")


# st.title("ACS Report Mapping")

# # Create a file uploader for multiple Excel files
# uploaded_files = st.file_uploader("Drop your Excel files here", type=["xls", "xlsx"], accept_multiple_files=True)

# # Display the count of uploaded files
# if uploaded_files:
#      st.warning(f"**You have uploaded {len(uploaded_files)} file(s).**")

# # Add an upload button to process files
# if uploaded_files:
#     if st.button("Upload Files"):
#         dfs = []  # List to hold preprocessed DataFrames

#         for uploaded_file in uploaded_files:
#             try:
#                 # Preprocess the uploaded Excel file
#                 df = preprocess_excel(uploaded_file)
#                 if df is not None:
#                     new_cols = {col: f"{uploaded_file.name}_{col}" for col in df.columns if col not in ['Date/time']}
#                     df = df.rename(columns=new_cols)
#                     dfs.append(df)
#             except Exception as e:
#                 st.error(f"Error processing file {uploaded_file.name}: {e}")
#                 continue

#         if dfs:
#             merged_df = dfs[0]
#             for df in dfs[1:]:
#                 if 'Date/time' in merged_df.columns and 'Date/time' in df.columns:
#                     try:
#                         merged_df = pd.merge(merged_df, df, on='Date/time', how='outer')
#                     except Exception as e:
#                         st.error(f"Error merging dataframes: {e}")
#                         continue
#                 else:
#                     st.warning("Warning: 'Date/time' column not found in one or more DataFrames.")

#             if 'Unnamed: 0' in merged_df.columns:
#                 merged_df = merged_df.drop(columns=['Unnamed: 0'])

#             # Display the merged DataFrame
#             st.write("### Annexure Sheet")
#             st.dataframe(merged_df)
#             if not merged_df.empty:
#                 st.header("Sensor Data Graphs")
#                 plot_sensor_data_streamlit_detailed(merged_df)
#                 plot_all_sensors_streamlit(merged_df)
#                 temp_stats, rh_stats = calculate_statistics(merged_df)

#                 # Display DataFrames
#                 st.subheader("Temperature Statistics")
#                 st.dataframe(temp_stats)

#                 st.subheader("Relative Humidity (RH) Statistics")
#                 st.dataframe(rh_stats)

#                 try:
#                     st.subheader("Summary of Statistics")

#                     # Overall Min and Max
#                     overall_min_temp_value = temp_stats.loc['min'].min()
#                     overall_min_temp_sensor = temp_stats.loc['min'].idxmin()
#                     overall_max_temp_value = temp_stats.loc['max'].max()
#                     overall_max_temp_sensor = temp_stats.loc['max'].idxmax()

#                     # Display overall min and max temperature with sensor details
#                     st.markdown("### Overall Temperature Summary")
#                     st.write(f"**Overall Min Temperature:** {overall_min_temp_value} from Sensor: {overall_min_temp_sensor}")
#                     st.write(f"**Overall Max Temperature:** {overall_max_temp_value} from Sensor: {overall_max_temp_sensor}")

#                     # Overall Min and Max for RH
#                     overall_min_rh_value = rh_stats.loc['min'].min()
#                     overall_min_rh_sensor = rh_stats.loc['min'].idxmin()
#                     overall_max_rh_value = rh_stats.loc['max'].max()
#                     overall_max_rh_sensor = rh_stats.loc['max'].idxmax()

#                     # Display overall min and max RH with sensor details
#                     st.markdown("### Overall Relative Humidity (RH) Summary")
#                     st.write(f"**Overall Min RH:** {overall_min_rh_value} from Sensor: {overall_min_rh_sensor}")
#                     st.write(f"**Overall Max RH:** {overall_max_rh_value} from Sensor: {overall_max_rh_sensor}")

#                 except KeyError as e:
#                     st.error(f"KeyError: Could not calculate summary statistics. Missing key: {e}")
#                 except Exception as e:
#                     st.error(f"An error occurred while summarizing statistics: {e}")

#         else:
#             st.warning("No valid DataFrames to merge.")


import streamlit as st
import pandas as pd
from functions import * # Imports all functions from functions.py, including MKT
import io # Not explicitly used in this snippet, but often for file handling

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
    if st.button("Upload and Process Files"): # Changed button text for clarity
        dfs = []  # List to hold preprocessed DataFrames
        file_names_processed = [] # To keep track of successfully processed files for renaming

        with st.spinner("Processing files..."): # Added a spinner for better UX
            for uploaded_file in uploaded_files:
                st.write(f"--- Processing: {uploaded_file.name} ---")
                try:
                    # Preprocess the uploaded Excel file
                    df = preprocess_excel(uploaded_file)
                    if df is not None and not df.empty:
                        # Create unique column names by prefixing with the filename
                        # Exclude 'Date/time' from renaming if it's the merge key
                        # Also, ensure 'id' if it was the index is handled or not present as a regular column
                        
                        # Store original column names before renaming, excluding 'Date/time'
                        original_cols_to_rename = [col for col in df.columns if col != 'Date/time']
                        
                        # If 'id' was set as index and reset_index was not called in preprocess_excel for it,
                        # it won't be in df.columns. If it is, it should also be renamed.
                        # The current preprocess_excel sets 'id' as index.
                        
                        new_cols = {col: f"{uploaded_file.name}_{col}" for col in original_cols_to_rename}
                        df = df.rename(columns=new_cols)
                        
                        dfs.append(df)
                        file_names_processed.append(uploaded_file.name)
                        st.success(f"Successfully processed: {uploaded_file.name}")
                    elif df is None:
                        st.error(f"Failed to process (returned None): {uploaded_file.name}")
                    else: # df is empty
                        st.warning(f"Processed but empty or invalid data in: {uploaded_file.name}")

                except Exception as e:
                    st.error(f"Error processing file {uploaded_file.name}: {e}")
                    continue

        if dfs:
            st.write("--- Merging DataFrames ---")
            # Initialize merged_df with the first DataFrame
            # Ensure the first DataFrame has 'Date/time' or handle appropriately
            if 'Date/time' in dfs[0].columns:
                merged_df = dfs[0]
            else:
                # If the first df doesn't have 'Date/time', we might need to create it or handle error
                # For now, let's assume it exists or merging will fail gracefully later
                st.error(f"The first processed file ({file_names_processed[0]}) does not contain a 'Date/time' column for merging.")
                merged_df = pd.DataFrame() # Start with empty if first is problematic

            # Merge subsequent DataFrames
            for i, df_to_merge in enumerate(dfs[1:], start=1):
                if not merged_df.empty and 'Date/time' in df_to_merge.columns and 'Date/time' in merged_df.columns:
                    try:
                        # Using outer merge to keep all data; consider suffixes if column names clash post-rename
                        merged_df = pd.merge(merged_df, df_to_merge, on='Date/time', how='outer', 
                                             suffixes=(f'_file{0}', f'_file{i}')) # Add suffixes to avoid duplicate columns from merge itself
                    except Exception as e:
                        st.error(f"Error merging DataFrame from {file_names_processed[i]} with previous data: {e}")
                        continue
                elif merged_df.empty and 'Date/time' in df_to_merge.columns : # If merged_df became empty due to previous error
                     merged_df = df_to_merge # Try to start merging with current df
                elif 'Date/time' not in df_to_merge.columns:
                     st.warning(f"Warning: 'Date/time' column not found in {file_names_processed[i]}. Skipping merge for this file.")
                elif 'Date/time' not in merged_df.columns and not merged_df.empty: # Should not happen if first df is good
                     st.error("Critical Error: 'Date/time' column lost from merged DataFrame.")
                     break


            if not merged_df.empty:
                # Drop a common problematic column if it exists after merge
                if 'Unnamed: 0' in merged_df.columns:
                    merged_df = merged_df.drop(columns=['Unnamed: 0'])
                
                # Optional: Convert 'Date/time' to datetime objects and sort
                if 'Date/time' in merged_df.columns:
                    try:
                        merged_df['Date/time'] = pd.to_datetime(merged_df['Date/time'], format="%d-%m-%Y %H:%M:%S", errors='coerce')
                        merged_df = merged_df.sort_values(by='Date/time').reset_index(drop=True)
                        # Convert back to string if needed by downstream functions, or update functions
                        # merged_df['Date/time'] = merged_df['Date/time'].dt.strftime("%d-%m-%Y %H:%M:%S")
                    except Exception as e:
                        st.warning(f"Could not sort by Date/time: {e}")


                st.write("### Annexure Sheet (Merged Data)")
                st.dataframe(merged_df)
                
                # --- Plotting and Statistics ---
                st.header("Sensor Data Graphs and Statistics")
                
                # Ensure 'Date/time' is suitable for plotting functions or set as index
                # For now, assuming plotting functions can handle 'Date/time' as a column
                
                plot_sensor_data_streamlit_detailed(merged_df) # Individual sensor plots
                plot_all_sensors_streamlit(merged_df) # Combined sensor plots
                
                temp_stats, rh_stats = calculate_statistics(merged_df)

                if not temp_stats.empty:
                    st.subheader("Temperature Statistics")
                    st.dataframe(temp_stats)
                else:
                    st.info("No temperature data available for statistics.")

                if not rh_stats.empty:
                    st.subheader("Relative Humidity (RH) Statistics")
                    st.dataframe(rh_stats)
                else:
                    st.info("No RH data available for statistics.")

                # --- MKT Calculation and Display ---
                st.subheader("Mean Kinetic Temperature (MKT) Values")
                mkt_values_df = calculate_mkt_for_df(merged_df) # DEFAULT_DELTA_H_OVER_R is used from functions.py
                
                if not mkt_values_df.empty and not mkt_values_df.isnull().all().all():
                    st.dataframe(mkt_values_df)
                    # You can also display individual MKT values if needed:
                    # for col_name in mkt_values_df.columns:
                    #    st.write(f"MKT for {col_name}: {mkt_values_df[col_name]['MKT_calculated_Celsius']:.2f}")
                else:
                    st.info("MKT could not be calculated or no relevant data found.")

                # --- Summary Statistics ---
                try:
                    st.subheader("Summary of Min/Max Statistics")
                    # Overall Min and Max Temperature
                    if not temp_stats.empty and 'min' in temp_stats.index and 'max' in temp_stats.index:
                        overall_min_temp_value = temp_stats.loc['min'].min()
                        overall_min_temp_sensor = temp_stats.loc['min'].idxmin()
                        overall_max_temp_value = temp_stats.loc['max'].max()
                        overall_max_temp_sensor = temp_stats.loc['max'].idxmax()
                        st.markdown("#### Overall Temperature Summary")
                        st.write(f"**Overall Min Temperature:** {overall_min_temp_value:.2f}°C (from Sensor: {overall_min_temp_sensor})")
                        st.write(f"**Overall Max Temperature:** {overall_max_temp_value:.2f}°C (from Sensor: {overall_max_temp_sensor})")
                    else:
                        st.markdown("#### Overall Temperature Summary")
                        st.write("Not available (no temperature statistics).")

                    # Overall Min and Max for RH
                    if not rh_stats.empty and 'min' in rh_stats.index and 'max' in rh_stats.index:
                        overall_min_rh_value = rh_stats.loc['min'].min()
                        overall_min_rh_sensor = rh_stats.loc['min'].idxmin()
                        overall_max_rh_value = rh_stats.loc['max'].max()
                        overall_max_rh_sensor = rh_stats.loc['max'].idxmax()
                        st.markdown("#### Overall Relative Humidity (RH) Summary")
                        st.write(f"**Overall Min RH:** {overall_min_rh_value:.2f}% (from Sensor: {overall_min_rh_sensor})")
                        st.write(f"**Overall Max RH:** {overall_max_rh_value:.2f}% (from Sensor: {overall_max_rh_sensor})")
                    else:
                        st.markdown("#### Overall Relative Humidity (RH) Summary")
                        st.write("Not available (no RH statistics).")

                except KeyError as e:
                    st.error(f"KeyError: Could not calculate summary statistics. Missing key: {e}. This might happen if stats tables are empty.")
                except Exception as e:
                    st.error(f"An error occurred while summarizing statistics: {e}")
            else:
                st.warning("Merged DataFrame is empty. No data to display or analyze.")
        else:
            st.warning("No valid DataFrames were processed from the uploaded files.")
else:
    st.info("Please upload Excel file(s) to begin.")

