import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mysql.connector

# Suppress warning messages
st.set_option('deprecation.showPyplotGlobalUse', False)

# Database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'Abhishek',
    'auth_plugin':'caching_sha2_password'
}

# Establish a connection to the MySQL database
connection = mysql.connector.connect(**db_config)

# Query the database for available datasets
cursor = connection.cursor()
cursor.execute("SHOW TABLES")
datasets = [table[0] for table in cursor.fetchall()]

# Streamlit web application
st.title('5G Private Network Data Viewer and Visualizer')

# Create sidebar
st.sidebar.title('Navigation')
page = st.sidebar.selectbox('Select a page:', ['Home', 'View Data', 'Visualize Data'])

if page == 'Home':
    st.write('Welcome to the 5G Private Network Data Viewer and Visualizer!')
    st.write('Use the navigation on the left to explore data and visualizations.')
    st.write('Click on GitHub Link to access Data collection code and requirements text file: https://github.com/AbhishekPadir/Streamlit_Test_WebApp8')

elif page == 'View Data':
    st.header('View Data')
    selected_dataset = st.selectbox('Select a dataset:', datasets)

    if selected_dataset:
        query = f'SELECT * FROM {selected_dataset} LIMIT 10'
        cursor.execute(query)
        data = cursor.fetchall()

        if data:
            st.write(f'Fetched Data from {selected_dataset}:')

            num_columns = len(cursor.description)
            column_names = [desc[0] for desc in cursor.description]

            data_for_df = [list(row) for row in data]
            df = pd.DataFrame(data_for_df, columns=column_names)
            st.dataframe(df)

            st.subheader('Data Summary')
            st.write(df.describe())
            
            # Correlation Matrix
            st.subheader('Correlation Matrix')
            selected_columns_corr = st.multiselect('Select columns for correlation matrix:', column_names)

            if selected_columns_corr:
                selected_data_corr = df[selected_columns_corr]
                correlation_matrix = selected_data_corr.corr()
                st.write(correlation_matrix)

                # Heatmap option
                show_heatmap = st.checkbox('Show Heatmap')
                if show_heatmap:
                    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
                    st.pyplot()

            else:
                st.write('Select at least two columns for the correlation matrix.')

        else:
            st.write('No data available for the selected dataset.')
    else:
        st.write('No dataset selected.')
    

elif page == 'Visualize Data':
    st.header('Visualize Data')
    selected_dataset_viz = st.selectbox('Select a dataset for visualization:', datasets)

    if selected_dataset_viz:
        visualization_type = st.selectbox('Select a visualization type:', ['None', 'Line Chart', 'Scatter Plot', 'Bar Chart'])

        if visualization_type != 'None':
            viz_query = f'SELECT * FROM {selected_dataset_viz}'
            cursor.execute(viz_query)
            viz_data = cursor.fetchall()

            if viz_data:
                viz_column_names = [desc[0] for desc in cursor.description]

                x_axis = st.selectbox('Select X-axis column:', viz_column_names)
                y_axis = st.selectbox('Select Y-axis column:', viz_column_names)

                timestamp_columns = [col for col in viz_column_names if 'timestamp' in col.lower()]
                if timestamp_columns:
                    selected_timestamp_column = timestamp_columns[0]
                    min_timestamp = min(row[viz_column_names.index(selected_timestamp_column)] for row in viz_data)
                    max_timestamp = max(row[viz_column_names.index(selected_timestamp_column)] for row in viz_data)
                    timestamp_range = st.slider('Select Time Range', min_value=min_timestamp, max_value=max_timestamp, value=(min_timestamp, max_timestamp))

                    filtered_data = [row for row in viz_data if timestamp_range[0] <= row[viz_column_names.index(selected_timestamp_column)] <= timestamp_range[1]]

                    plt.figure(figsize=(8, 6))
                    if visualization_type == 'Line Chart':
                        plt.plot([row[viz_column_names.index(x_axis)] for row in filtered_data],
                                 [row[viz_column_names.index(y_axis)] for row in filtered_data])
                        plt.xlabel(x_axis)
                        plt.ylabel(y_axis)
                        plt.title('Line Chart')
                        st.pyplot()

                    elif visualization_type == 'Scatter Plot':
                        plt.scatter([row[viz_column_names.index(x_axis)] for row in filtered_data],
                                    [row[viz_column_names.index(y_axis)] for row in filtered_data])
                        plt.xlabel(x_axis)
                        plt.ylabel(y_axis)
                        plt.title('Scatter Plot')
                        st.pyplot()

                    elif visualization_type == 'Bar Chart':
                        plt.bar([row[viz_column_names.index(x_axis)] for row in filtered_data],
                                [row[viz_column_names.index(y_axis)] for row in filtered_data])
                        plt.xlabel(x_axis)
                        plt.ylabel(y_axis)
                        plt.title('Bar Chart')
                        st.pyplot()

                else:
                    st.write('No timestamp columns found in the dataset.')

            else:
                st.write('No data available for visualization.')

        else:
            st.write('No dataset selected for visualization.')

# Close the connection
connection.close()
