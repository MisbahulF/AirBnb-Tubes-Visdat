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

# Filter for Cancellation Policy
cancellation_policy = st.sidebar.multiselect(
    "Select Cancellation Policy",
    options=data["cancellation_policy"].unique(),
    default=data["cancellation_policy"].unique()
)

# Filter for Price Range
price_range = st.sidebar.slider(
    "Select Price Range",
    min_value=int(data["price"].min()),
    max_value=int(data["price"].max()),
    value=(int(data["price"].min()), int(data["price"].max()))
)

# Filters for New Features (Reversed Logic)
smoking_filter = st.sidebar.checkbox("Smoking Allowed")
party_filter = st.sidebar.checkbox("Parties Allowed")
pet_filter = st.sidebar.checkbox("Pets Allowed")


# Apply all filters
filtered_data = data[
    (data["neighbourhood group"].isin(neighbourhood_group)) &
    (data["room type"].isin(room_type)) &
    (data["price"] >= price_range[0]) &
    (data["price"] <= price_range[1]) &
    ((data["neighbourhood"].isin(neighbourhood_filter)) if neighbourhood_filter else True) &  # Neighbourhood filter applied
    ((data["no_smoking"] == False) if smoking_filter else True) &  # Smoking allowed
    ((data["no_party"] == False) if party_filter else True) &      # Parties allowed
    ((data["no_pet"] == False) if pet_filter else True)        # Pets allowed
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
            f"""
            <p style='color: inherit; font-size: 1rem; line-height: 1.5;'>{best_listing['house_rules'] if 'house_rules' in best_listing else 'No description available.'}</p>
            """,
            unsafe_allow_html=True,
        )

        # Add "More Detail" drop-down section
        with st.expander("More Detail on Highlighted Listing Logic"):
            st.markdown("""
            The highlighted listing is chosen based on the following logic:
            1. **Review Rate Number** (descending): Listings with the highest review ratings are prioritized.
            2. **Number of Reviews** (descending): If multiple listings have the same review rate, the one with more reviews is chosen.
            3. **Price** (ascending): If the above two criteria are equal, the listing with the lower price is selected.

            This ensures that the selected listing is both highly rated and cost-effective, with a preference for those with a strong review history.
            """)
    else:
        st.write("No listings match your filter criteria.")



# Tab 2: Visualization Page
with tab2:
    st.title("Airbnb Visualization Dashboard")

    # Geographical Insights
    st.header("Geographical Insights")

    st.subheader("Property Locations by Price")
    map_data = filtered_data  # Use the filtered data from the sidebar
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

    # Add explanation section
    with st.expander("More Detail"):
        st.markdown(f"""
        This map displays properties based on their price and availability. The properties shown here reflect the 
        filters you've applied. There are **{len(map_data)} properties** in the current view. The size of each point 
        indicates the price, while the color scale represents the price intensity. Use this map to explore geographical 
        pricing patterns across neighborhoods.
        """)

    # Distribution of Prices
    st.subheader("Distribution of Prices by Room Type")
    fig_price_dist = px.violin(
        filtered_data,
        x="room type",
        y="price",
        color="room type",
        box=True, 
        title="Price Distribution by Room Type",
        labels={"room type": "Room Type", "price": "Price ($)"}
    )
    st.plotly_chart(fig_price_dist, use_container_width=True)
    with st.expander("More Detail"):
        st.markdown(f"""
        This box plot shows the distribution of prices across different room types. Each box represents the interquartile range 
        (25th to 75th percentile) of prices, while the whiskers show the overall range excluding outliers. 
        The data includes **{len(filtered_data)} properties** after applying filters.
        """)
    # Violin Plot: Price vs. Neighbourhood Group
    st.subheader("Price Distribution by Neighbourhood Group (Violin Plot)")
    fig_price_neighbourhood_violin = px.violin(
        filtered_data,
        x="neighbourhood group",
        y="price",
        color="neighbourhood group",
        box=True,  # Include box plot inside the violin plot
        title="Price Distribution by Neighbourhood Group (Violin Plot)",
        labels={"neighbourhood group": "Neighbourhood Group", "price": "Price ($)"}
    )
    st.plotly_chart(fig_price_neighbourhood_violin, use_container_width=True)

    # Add explanation section
    with st.expander("More Detail"):
        st.markdown(f"""
        This violin plot visualizes the distribution of property prices for each neighbourhood group. 
        Unlike a box plot, it shows the data's density (wider areas represent higher density).

        Key Observations:
        - **Neighbourhood Groups**: The plot includes **{len(filtered_data['neighbourhood group'].unique())} groups** based on your filters.
        - **Price Range**: Prices range from **${filtered_data['price'].min()}** to **${filtered_data['price'].max()}** in the filtered data.
        - **Density**: The width of the violin represents the density of data points. Wider sections indicate that more properties fall within that price range.

        Use this plot to understand how property prices are distributed within each neighbourhood group, and to identify areas with higher or lower density of properties.
        """)


    # Availability Insights
    st.subheader("Availability Across Neighbourhood Groups")
    fig_availability = px.histogram(
        filtered_data,
        x="availability 365",
        color="neighbourhood group",
        title="Yearly Availability by Neighbourhood Group",
        labels={"availability 365": "Days Available per Year", "count": "Number of Listings"},
        opacity=0.5  # Set transparency level (0.0 = fully transparent, 1.0 = fully opaque)
    )
    st.plotly_chart(fig_availability, use_container_width=True)
    with st.expander("More Detail"):
        st.markdown(f"""
        This histogram shows the availability of properties (in days per year) grouped by neighborhood groups. 
        Properties are counted based on the number of days they are available for booking in a year. 
        The current data includes **{len(filtered_data)} properties** with availability ranging from **{filtered_data['availability 365'].min()} to {filtered_data['availability 365'].max()} days/year**.
        """)


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
    with st.expander("More Detail"):
        st.markdown(f"""
        This scatter plot explores the relationship between property price and the number of reviews received. 
        Each point represents a property, sized by its availability and colored by neighborhood group. 
        The plot includes **{len(filtered_data)} properties**, reflecting the current filters applied.
        """)




# Tab 3: Detail Page
with tab3:
    st.title("Detailed Data Overview")
    st.write(filtered_data)
    st.write("Summary Statistics:")
    st.write(filtered_data.describe())
