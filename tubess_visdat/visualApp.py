import streamlit as st
import pandas as pd
import plotly.express as px
st.markdown("""
    <style>
    /* Pindahkan sidebar ke kanan */
    .css-1d391kg { /* Sidebar container */
        position: fixed;
        top: 0;
        right: 0;
        width: 20%; /* Atur lebar sidebar */
    }
    /* Konten utama disesuaikan */
    .main-content { 
        margin-left: 0; /* Hilangkan margin kiri */
        margin-right: 22%; /* Beri margin kanan agar konten tidak tertutup */
    }
    .css-1gk3ngh { /* Kontainer konten utama Streamlit */
        padding-right: 22%; /* Sesuaikan padding agar konten tetap rapi */
    }
    </style>
""", unsafe_allow_html=True)

# Load dataset with extracted features
@st.cache_data
def load_data():
    file_path = "AirbnbData_with_features.csv"  # Ganti dengan path file hasil ekstraksi
    data = pd.read_csv(file_path)
    return data

data = load_data()

# Sidebar filters
st.sidebar.header("Filters")

# Filter for Neighbourhood Group
neighbourhood_group = st.sidebar.multiselect(
    "Select Neighbourhood Group",
    options=data["neighbourhood group"].unique(),
    default=data["neighbourhood group"].unique()
)

# Toggleable Filter for Specific Neighbourhoods
with st.sidebar.expander("Advanced Filters: Neighbourhood", expanded=False):
    neighbourhood_filter = st.multiselect(
        "Select Specific Neighbourhoods",
        options=data["neighbourhood"].unique(),
        default=[]  # Default is empty
    )

# Filter for Room Type
room_type = st.sidebar.multiselect(
    "Select Room Type",
    options=data["room type"].unique(),
    default=data["room type"].unique()
)

# Filter for Price Range
price_range = st.sidebar.slider(
    "Select Price Range",
    min_value=int(data["price"].min()),
    max_value=int(data["price"].max()),
    value=(int(data["price"].min()), int(data["price"].max()))
)

# Filters for New Features
no_smoking_filter = st.sidebar.checkbox("No Smoking")
no_party_filter = st.sidebar.checkbox("No Parties")
no_pet_filter = st.sidebar.checkbox("No Pets")

# Apply all filters
filtered_data = data[
    (data["neighbourhood group"].isin(neighbourhood_group)) &
    (data["room type"].isin(room_type)) &
    (data["price"] >= price_range[0]) &
    (data["price"] <= price_range[1]) &
    ((data["neighbourhood"].isin(neighbourhood_filter)) if neighbourhood_filter else True) &  # Neighbourhood filter applied
    ((data["no_smoking"] == True) if no_smoking_filter else True) &
    ((data["no_party"] == True) if no_party_filter else True) &
    ((data["no_pet"] == True) if no_pet_filter else True)
]

# Add custom CSS for improved spacing and content size
st.markdown("""
    <style>
    .small-title {
        margin-bottom: -10px; /* Reduce spacing between title and content */
        font-size: 1rem; /* Slightly smaller font for titles */
        color: gray;
    }
    .content {
        margin-bottom: 20px; /* Adjust spacing between content items */
        font-size: 2rem; /* Double size for content */
        font-weight: bold; /* Bold content */
    }
    </style>
""", unsafe_allow_html=True)

# Tab-based Navigation
tab1, tab2, tab3 = st.tabs(["Home", "Visualization", "Detail Page"])

# Tab 1: Home Page
with tab1:
    st.title("Airbnb Listings - Highlights Based on Your Filters")
    
    # Determine the "best" listing based on review rate, reviews, and price
    if not filtered_data.empty:
        best_listing = filtered_data.sort_values(
            by=["review rate number", "number of reviews", "price"], 
            ascending=[False, False, True]
        ).iloc[0]

        # Display best listing details with smaller title and improved spacing
        st.markdown(f"<h3>{best_listing['NAME']}</h3>", unsafe_allow_html=True)

        # Use 3x3 grid for the listing details
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<p class='small-title'>Host Name</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='content'>{best_listing['host name']}</p>", unsafe_allow_html=True)
            
            st.markdown("<p class='small-title'>Room Type</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='content'>{best_listing['room type']}</p>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<p class='small-title'>Price per Night</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='content'>${best_listing['price']}</p>", unsafe_allow_html=True)
            
            st.markdown("<p class='small-title'>Review Rate</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='content'>{best_listing['review rate number']}</p>", unsafe_allow_html=True)

        with col3:
            st.markdown("<p class='small-title'>Number of Reviews</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='content'>{best_listing['number of reviews']}</p>", unsafe_allow_html=True)
            
            st.markdown("<p class='small-title'>Availability</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='content'>{best_listing['availability 365']} days/year</p>", unsafe_allow_html=True)

        # Add description below the grid
        st.markdown("<p class='small-title'>Description</p>", unsafe_allow_html=True)
        st.markdown(
            f"<p style='color: black;'>{best_listing['house_rules'] if 'house_rules' in best_listing else 'No description available.'}</p>",
            unsafe_allow_html=True,
        )
    else:
        st.write("No listings match your filter criteria.")

# Tab 2: Visualization Page
with tab2:
    st.title("Airbnb Visualization Dashboard")

    # Geographical Insights
    st.header("Geographical Insights")

    st.subheader("Property Locations by Price")
    # Filter map data based on all applied filters
    map_data = filtered_data  # Use the filtered data from the sidebar
    # Create scatter mapbox
    fig_map = px.scatter_mapbox(
        map_data,
        lat="lat",
        lon="long",
        color="price",
        size="price",
        hover_name="NAME",
        hover_data=["neighbourhood", "price"],
        title=f"Map of Properties After Applying Filters",
        mapbox_style="open-street-map",
        zoom=10
    )
    st.plotly_chart(fig_map, use_container_width=True)


    # Distribution of Prices
    st.subheader("Distribution of Prices by Room Type")
    fig_price_dist = px.box(
        filtered_data,
        x="room type",
        y="price",
        color="room type",
        title="Price Distribution by Room Type",
        labels={"room type": "Room Type", "price": "Price ($)"}
    )
    st.plotly_chart(fig_price_dist, use_container_width=True)

    # Availability Insights
    st.subheader("Availability Across Neighbourhood Groups")
    fig_availability = px.histogram(
        filtered_data,
        x="availability 365",
        color="neighbourhood group",
        title="Yearly Availability by Neighbourhood Group",
        labels={"availability 365": "Days Available per Year", "count": "Number of Listings"}
    )
    st.plotly_chart(fig_availability, use_container_width=True)

    # Correlation Between Price and Reviews
    st.subheader("Price vs. Number of Reviews")
    fig_price_reviews = px.scatter(
        filtered_data,
        x="number of reviews",
        y="price",
        color="neighbourhood group",
        size="availability 365",
        hover_name="NAME",
        title="Correlation Between Price and Number of Reviews",
        labels={"number of reviews": "Number of Reviews", "price": "Price ($)"}
    )
    st.plotly_chart(fig_price_reviews, use_container_width=True)



# Tab 3: Detail Page
with tab3:
    st.title("Detailed Data Overview")
    st.write(filtered_data)
    st.write("Summary Statistics:")
    st.write(filtered_data.describe())
