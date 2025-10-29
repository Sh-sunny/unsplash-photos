import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


st.set_page_config(
    page_title="California Housing Data Analysis",
    page_icon="🏠",
    layout="wide"
)


st.title("California Housing Data (1990)")
st.write("Developed by Shaxinru")  


@st.cache_data
def load_data():
  
    try:
        data = pd.read_csv('housing.csv')
    except FileNotFoundError:
     
        st.warning("housing.csv not found. Using sample data.")
        np.random.seed(42)
        n_samples = 1000
        
        data = pd.DataFrame({
            'longitude': np.random.uniform(-124.3, -114.3, n_samples),
            'latitude': np.random.uniform(32.5, 42.0, n_samples),
            'housing_median_age': np.random.randint(1, 52, n_samples),
            'total_rooms': np.random.randint(2, 40000, n_samples),
            'total_bedrooms': np.random.randint(1, 6500, n_samples),
            'population': np.random.randint(3, 15000, n_samples),
            'households': np.random.randint(1, 5000, n_samples),
            'median_income': np.random.uniform(0.5, 15.0, n_samples),
            'median_house_value': np.random.randint(15000, 500000, n_samples),
            'ocean_proximity': np.random.choice(['INLAND', 'NEAR BAY', 'NEAR OCEAN', 'ISLAND'], n_samples)
        })
    
    return data


data = load_data()


st.sidebar.header("Filters")


price_range = st.sidebar.slider(
    "Select Price Range:",
    min_value=int(data['median_house_value'].min()),
    max_value=int(data['median_house_value'].max()),
    value=(int(data['median_house_value'].min()), int(data['median_house_value'].max())),
    step=10000
)


if 'ocean_proximity' in data.columns:
    location_options = data['ocean_proximity'].unique().tolist()
else:
    location_options = ["Coastal", "Inland", "Urban", "Rural"]

location_types = st.sidebar.multiselect(
    "Select Location Type:",
    options=location_options,
    default=location_options
)


income_level = st.sidebar.radio(
    "Select Income Level:",
    options=["Low (±2.5)", "Medium (> 2.5 & < 4.5)", "High (> 4.5)"]
)

if income_level == "Low (±2.5)":
    filtered_data = data[data['median_income'] <= 2.5]
elif income_level == "Medium (> 2.5 & < 4.5)":
    filtered_data = data[(data['median_income'] > 2.5) & (data['median_income'] < 4.5)]
else:  
    filtered_data = data[data['median_income'] >= 4.5]


filtered_data = filtered_data[
    (filtered_data['median_house_value'] >= price_range[0]) & 
    (filtered_data['median_house_value'] <= price_range[1])
]


if 'ocean_proximity' in data.columns and location_types:
    filtered_data = filtered_data[filtered_data['ocean_proximity'].isin(location_types)]


st.write(f"Showing {len(filtered_data)} out of {len(data)} records")


col1, col2 = st.columns([2, 1])

with col1:

    st.subheader("Housing Distribution Map")
    
    if not filtered_data.empty:
 
        fig, ax = plt.subplots(figsize=(10, 8))
        
        scatter = ax.scatter(
            filtered_data['longitude'], 
            filtered_data['latitude'],
            c=filtered_data['median_house_value'],
            s=filtered_data['median_income'] * 10,
            alpha=0.6,
            cmap='viridis'
        )
        
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_title('California Housing Prices Distribution')
        

        cbar = plt.colorbar(scatter)
        cbar.set_label('Median House Value')
        
        st.pyplot(fig)
    else:
        st.warning("No data available for the selected filters.")

with col2:

    st.subheader("Data Summary")
    if not filtered_data.empty:
        st.metric("Average Price", f"${filtered_data['median_house_value'].mean():,.0f}")
        st.metric("Average Income", f"${filtered_data['median_income'].mean():.2f}")
        if 'housing_median_age' in filtered_data.columns:
            st.metric("Average House Age", f"{filtered_data['housing_median_age'].mean():.1f} years")
        

        st.subheader("Sample Data")
        display_columns = ['median_income', 'median_house_value']
        if 'housing_median_age' in filtered_data.columns:
            display_columns.append('housing_median_age')
        if 'ocean_proximity' in filtered_data.columns:
            display_columns.append('ocean_proximity')
        display_columns.extend(['longitude', 'latitude'])
        
        st.dataframe(filtered_data.head(10)[display_columns])


st.subheader("Distribution of Median House Value")
if not filtered_data.empty:
    fig_hist, ax_hist = plt.subplots(figsize=(10, 6))
    
    ax_hist.hist(filtered_data['median_house_value'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    ax_hist.set_xlabel('Median House Value')
    ax_hist.set_ylabel('Count')
    ax_hist.set_title('Histogram of Median House Values (30 bins)')
    
 
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    st.pyplot(fig_hist)
else:
    st.warning("No data available to display histogram.")


with st.expander("Show Raw Data"):
    st.dataframe(data)


with st.expander("Data Information"):
    st.write("**Data Columns:**")
    st.write(data.columns.tolist())
    st.write("**Data Shape:**", data.shape)
    st.write("**Data Types:**")
    st.write(data.dtypes)
  