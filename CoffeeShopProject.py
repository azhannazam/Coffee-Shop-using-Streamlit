import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Load the dataset
data = pd.read_csv("C:/Users/USER/OneDrive - Universiti Teknologi PETRONAS/Documents/1.2 SEM 8/Data Visualization/archive (1)/Project.csv")

# Convert transaction_date to datetime format
data['transaction_date'] = pd.to_datetime(data['transaction_date'], format='%d-%m-%Y')

# Check if the hour and day_of_week columns are available in the dataset
if 'Hour' not in data.columns or 'Day of Week' not in data.columns:
    st.error("The 'Hour' and 'Day of Week' columns are not available in the dataset.")
else:
    # Check if there are missing values in 'Hour' and 'Day of Week' columns
    missing_data = data[['Hour', 'Day of Week']].isnull().sum()
    if missing_data.any():
        st.warning(f"Missing values in 'Hour' or 'Day of Week' columns: {missing_data}")

# Function to display the About Page
def display_about_page():
    st.markdown("<h2 style='color: #3D3E3D;'>☕ About Brew & Bites</h2>", unsafe_allow_html=True)
    st.write(
        """
        Brew & Bites, located in Seri Iskandar, is a coffee shop designed to cater to the needs of busy students at 
        Universiti Teknologi PETRONAS (UTP). The goal of Brew & Bites is to offer good coffee and a friendly ambiance 
        for students to grab a drink, get some work done, or just hang out.
        """
    )

    st.markdown("<h4 style='color: #3D3E3D;'>📋 Team Members</h4>", unsafe_allow_html=True)

    # Display team member details in a clean table format with better styling
    team_data = {
        "Name": ["Muhammad Azhan bin Muhammad Nazam", "Nur Alia Chern binti Irwan Chern"],
        "Student ID": ["21000377", "21000199"],
        "Program": ["Computer Science", "Computer Science"]
    }
    team_df = pd.DataFrame(team_data)
    st.table(team_df)

    # Button to proceed to login/signup
    if st.button("Proceed to Login or Sign Up", key="proceed_button"):
        st.session_state.show_about = False  # Move to the login/signup screen
        st.session_state.show_login = True  # Show the login page
        st.experimental_rerun()  # Refresh to load the login/signup page

# Function to authenticate the user
def authenticate_user():
    if 'show_about' not in st.session_state:
        st.session_state.show_about = True  # Default to About page if session state is not set
    
    if 'show_login' not in st.session_state:
        st.session_state.show_login = False  # Default to not showing login if session state is not set
    
    if st.session_state.show_about:
        display_about_page()
    elif st.session_state.show_login:
        display_login_page()
    else:
        # If user is logged in, show the app, otherwise show login/sign-up
        if 'user' in st.session_state:
            st.write(f"Welcome, {st.session_state['user']}!")
            show_sales_data()
        else:
            st.write("Please log in or sign up to access the app.")
            display_login_page()

# Login page to enter username and password with UI enhancements
def display_login_page():
    st.subheader("Login to your account")
    
    # Simple login form with better user interaction
    username = st.text_input("Username", help="Enter your username")
    password = st.text_input("Password", type="password", help="Enter your password")
    login_button = st.button("Log In", help="Click to log in to your account")
    
    if login_button:
        if username and password:
            st.session_state['user'] = username  # Set session state for user
            st.session_state.show_login = False  # Hide the login page
            st.success("Logged in successfully!")
            st.experimental_rerun()  # Refresh to show the app after login
        else:
            st.error("Please enter valid username and password.")
            
    if st.button("Sign Up", help="Create a new account"):
        # Simple placeholder for sign up
        st.session_state['user'] = username  # Set session state for new user
        st.session_state.show_login = False  # Hide the login page
        st.success("Sign Up successful!")
        st.experimental_rerun()  # Refresh to show the app after sign up

# Function to show the sales data visualizations (after login)
def show_sales_data():
    # Sidebar for navigation menu with icons and more spacing
    st.sidebar.title("🚀 Navigation")
    page_selection = st.sidebar.radio("Select a page", ["📈 Sales Trend Over Time", 
                                                       "🏪 Sales by Store Location", 
                                                       "📊 Sales by Product Category", 
                                                       "⏰ Sales by Hour of the Day", 
                                                       "🔍 Product Analysis"])

    # Sidebar filters for general use (used in product analysis)
    st.sidebar.markdown("### Filter Options")
    month_filter = st.sidebar.selectbox("Select Month", options=data['Month Name'].unique(), help="Choose the month to analyze")
    
    # Dynamic Product Filters
    st.sidebar.markdown("### Product Filters")
    product_category_filter = st.sidebar.selectbox("Select Product Category", options=data['product_category'].unique(), help="Choose a product category")
    filtered_product_types = data[data['product_category'] == product_category_filter]['product_type'].unique()
    product_type_filter = st.sidebar.selectbox("Select Product Type", options=filtered_product_types, help="Choose a product type")
    
    filtered_product_details = data[(data['product_category'] == product_category_filter) & (data['product_type'] == product_type_filter)]['product_detail'].unique()
    product_detail_filter = st.sidebar.selectbox("Select Product Detail", options=filtered_product_details, help="Choose a specific product detail")

    # Filter data based on user input
    filtered_data = data[(data['Month Name'] == month_filter) & 
                         (data['product_category'] == product_category_filter) & 
                         (data['product_type'] == product_type_filter) & 
                         (data['product_detail'] == product_detail_filter)]

    # 📈 Sales Trend Over Time
    if page_selection == "📈 Sales Trend Over Time":
        st.subheader("Sales Trend Over Time")
        
        # Group the data by transaction date and calculate the sum of Total_Bill for each day
        sales_time = filtered_data.groupby('transaction_date').agg({'Total_Bill': 'sum'}).reset_index()

        if sales_time.empty:
            st.write("No sales data available for the selected filters.")
        else:
            # Add cumulative sales
            sales_time['Cumulative Sales'] = sales_time['Total_Bill'].cumsum()

            # Add a moving average (7-day moving average)
            sales_time['7-Day Moving Average'] = sales_time['Total_Bill'].rolling(window=7).mean()

            # Plotting the Total Sales and Cumulative Sales
            fig_time = px.line(sales_time, 
                               x='transaction_date', 
                               y=['Total_Bill', 'Cumulative Sales', '7-Day Moving Average'], 
                               title="Total Sales, Cumulative Sales, and Moving Average Over Time", 
                               template="plotly_dark")
            st.plotly_chart(fig_time)

            # Explanation and Recommendation
            st.markdown("### Explanation:")
            st.write("This graph shows the trend of total sales, cumulative sales, and the 7-day moving average over time. Cumulative sales help track the overall growth, and the moving average smooths fluctuations.")
            
            st.markdown("### Recommendation:")
            st.write("Consider running promotions during slow periods (e.g., weekdays) to boost sales. Identify the months with high sales and plan for additional stock during those periods.")

    # 🏪 Sales by Store Location
    elif page_selection == "🏪 Sales by Store Location":
        st.subheader("Sales by Store Location")
        
        # Allow users to select multiple stores for comparison
        store_options = data['store_location'].unique()
        selected_stores = st.multiselect("Select Stores to Compare", options=store_options, default=store_options[:2])
        
        # Filter data based on selected stores
        store_filtered_data = data[data['store_location'].isin(selected_stores)]
        
        # Group by store location and sum the Total_Bill for each store
        sales_store = store_filtered_data.groupby('store_location').agg({'Total_Bill': 'sum'}).reset_index()

        if sales_store.empty:
            st.write("No sales data available for the selected filters.")
        else:
            # Assign unique colors for each store
            colors = px.colors.qualitative.Set1[:len(sales_store)]
            fig_store = px.bar(sales_store, 
                               x='store_location', 
                               y='Total_Bill', 
                               color='store_location', 
                               color_discrete_sequence=colors, 
                               title="Sales by Store Location", 
                               template="plotly_dark")
            st.plotly_chart(fig_store)

            # Explanation and Recommendation
            st.markdown("### Explanation:")
            st.write("This bar chart shows the total sales by each store location. The size of the bar represents the total sales amount for each store.")
            
            st.markdown("### Recommendation:")
            st.write("Focus on boosting performance at stores with lower sales by allocating more resources (staff, marketing, etc.) to these locations.")

    # 📊 Sales by Product Category
    elif page_selection == "📊 Sales by Product Category":
        st.subheader("Sales by Product Category")
        
        # Allow users to select a product category
        selected_category = st.selectbox("Select Product Category", options=data['product_category'].unique())
        
        # Filter data based on selected category
        category_filtered_data = data[data['product_category'] == selected_category]
        
        # Group by product type and sum the Total_Bill for each type
        sales_product_type = category_filtered_data.groupby('product_type').agg({'Total_Bill': 'sum'}).reset_index()

        if sales_product_type.empty:
            st.write("No sales data available for the selected filters.")
        else:
            # Assign unique colors for each product type
            colors = px.colors.qualitative.Set1[:len(sales_product_type)]
            fig_product_type = px.bar(sales_product_type, 
                                      x='product_type', 
                                      y='Total_Bill', 
                                      color='product_type', 
                                      color_discrete_sequence=colors, 
                                      title=f"Sales by Product Type in {selected_category}", 
                                      template="plotly_dark")
            st.plotly_chart(fig_product_type)

            # Explanation and Recommendation
            st.markdown("### Explanation:")
            st.write("This bar chart shows the total sales by product type within the selected product category.")
            
            st.markdown("### Recommendation:")
            st.write("Focus on promoting high-performing product types and consider improving or discontinuing underperforming ones.")

    # ⏰ Sales by Hour of the Day
    elif page_selection == "⏰ Sales by Hour of the Day":
        st.subheader("Sales by Hour of the Day")
        
        # Use the 'Hour' and 'Day of Week' directly from the dataset
        filtered_data['Hour'] = filtered_data['Hour']
        filtered_data['Day of Week'] = filtered_data['Day of Week']
        
        # Group by Hour and Day of Week to calculate total sales
        sales_hour_day = filtered_data.groupby(['Hour', 'Day of Week']).agg({'Total_Bill': 'sum'}).reset_index()

        if sales_hour_day.empty:
            st.write("No sales data available for the selected filters.")
        else:
            # Create a heatmap using Plotly
            fig_heatmap = px.density_heatmap(sales_hour_day, 
                                             x='Hour', 
                                             y='Day of Week', 
                                             z='Total_Bill', 
                                             title="Sales Heatmap by Hour and Day of Week", 
                                             template="plotly_dark")
            st.plotly_chart(fig_heatmap)

            # Explanation and Recommendation
            st.markdown("""
                ### Heatmap Explanation:
                The heatmap shows how sales (Total_Bill) are distributed across **hours of the day** and **days of the week**.
                - **X-axis (Hour)**: Represents the hour of the day, from 0 (midnight) to 23 (11 PM). This shows how sales vary across each hour.
                - **Y-axis (Day of Week)**: Represents the days of the week, where **0** = Sunday, **1** = Monday, and so on, up to **6** = Saturday.
                - **Color Intensity**: The color scale indicates the **total sales** for each combination of hour and day:
                    - **Bright colors (yellow and orange)** represent **peak sales hours**, meaning the total sales are high during these times.
                    - **Darker colors (blue and purple)** indicate **less activity and lower sales**, meaning the total sales are lower during these times.
                
                ### How to Read:
                - If you see **yellow or orange** at a particular hour and day, that indicates a **high sales period**.
                - If you see **blue or purple**, that indicates **low sales periods** during those hours and days.

                ### Recommendation:
                - **Peak Hours**: Focus on increasing staff and optimizing resources during the bright yellow/orange areas to handle customer demand.
                - **Slow Hours**: Consider offering promotions or adjusting marketing strategies during the blue/purple areas to boost sales during slower times.
            """)

    # 🔍 Product Analysis Page (Best Seller and Restocking)
    elif page_selection == "🔍 Product Analysis":
        st.subheader("Product Performance Analysis")
        
        # Allow users to select multiple product categories
        selected_categories = st.multiselect("Select Product Categories", options=data['product_category'].unique(), default=data['product_category'].unique())
        
        # Filter data based on selected categories
        filtered_product_sales = data[data['product_category'].isin(selected_categories)]
        
        # Group by product details to analyze performance
        product_sales = filtered_product_sales.groupby(['product_category', 'product_type', 'product_detail']).agg({'Total_Bill': 'sum', 'transaction_id': 'count'}).reset_index()
        
        # Best Seller Analysis - Highlight the product with the highest total sales
        best_seller = product_sales.loc[product_sales['Total_Bill'].idxmax()]
        st.markdown(f"**Best Seller:** {best_seller['product_category']} - {best_seller['product_type']} ({best_seller['product_detail']})")
        st.markdown(f"**Total Sales:** RM{best_seller['Total_Bill']:.2f}")
        
        # Visualize the product performance with a bar chart for better insight
        fig_product_performance = px.bar(product_sales, 
                                         x='product_detail', 
                                         y='Total_Bill', 
                                         color='product_type', 
                                         title="Product Performance by Category, Type, and Detail", template="plotly_dark")
        st.plotly_chart(fig_product_performance)
        
        # Additional Analysis - Restocking Recommendations
        st.markdown("### Restocking Insights")
        st.write("Based on total sales, we can identify products that are performing well and others that may require more attention.")
        
        # Identify underperforming products based on sales volume (low total sales)
        underperforming_products = product_sales[product_sales['Total_Bill'] < product_sales['Total_Bill'].mean()]
        
        # Show a table of underperforming products
        if not underperforming_products.empty:
            st.write("**Underperforming Products (Low Sales)**")
            st.dataframe(underperforming_products[['product_category', 'product_type', 'product_detail', 'Total_Bill']].sort_values(by='Total_Bill'))
        else:
            st.write("No underperforming products found. All selected products are performing well!")
        
        # Highlighting Top-Selling Products
        st.markdown("### Top-Selling Products")
        top_selling_products = product_sales[product_sales['Total_Bill'] >= product_sales['Total_Bill'].max() * 0.75]
        if not top_selling_products.empty:
            st.write("**Top-Selling Products**")
            st.dataframe(top_selling_products[['product_category', 'product_type', 'product_detail', 'Total_Bill']].sort_values(by='Total_Bill', ascending=False))
        else:
            st.write("No top-selling products found. Consider evaluating sales strategies.")
        
        # Visualizing the Product Sales with Pie Chart
        st.markdown("### Sales Distribution by Product Type")
        product_type_sales = filtered_product_sales.groupby('product_type').agg({'Total_Bill': 'sum'}).reset_index()
        fig_product_type_sales = px.pie(product_type_sales, names='product_type', values='Total_Bill', title="Sales Distribution by Product Type", template="plotly_dark")
        st.plotly_chart(fig_product_type_sales)
        
        # Explanation and Recommendations
        st.markdown("### Explanation:")
        st.write("The bar chart shows the product sales performance by category, type, and detail. The pie chart shows the distribution of sales across different product types.")
        
        st.markdown("### Recommendations:")
        st.write("""
            - For underperforming products, consider running targeted promotions or adjusting the inventory mix.
            - For top-selling products, maintain or increase stock and continue promoting these items to maximize sales.
            - Evaluate product types with high sales potential and explore new flavors or variations to increase sales further.
        """)

# Main content function
def main_content():
    authenticate_user()

# Call the main content function
if __name__ == "__main__":
    main_content()
