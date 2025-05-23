
def run_visualization_dashboard():
    # All your code from visualization.py goes here

    import streamlit as st
    import pandas as pd
    import plotly.express as px
    import numpy as np

    # Load datasets
    df = pd.read_csv("E:/be project final/dmart_sales_with_locations.csv")

    cat_df = pd.read_csv("E:/be project final/dmart cat.csv")

    # Rename column for consistency
    cat_df.rename(columns={"Categoty": "Category"}, inplace=True)

    # Convert date
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df['Month'] = df['Date'].dt.month

    # Sidebar
    st.sidebar.title("Home")
    selected_location = st.sidebar.selectbox("Select Location", df['Location'].unique())

    # Filtered data
    filtered_df = df[df['Location'] == selected_location].copy()
    filtered_df['Revenue'] = filtered_df['Quantity'] * filtered_df['UnitPrice']

    # Merge
    merged_df = pd.merge(filtered_df, cat_df[['Name', 'Category', 'SubCategory', 'Brand']], on='Name', how='left')

    # Summary boxes before tabs
    st.title("📊 Dmart Sales Dashboard")

    # Calculate metrics
    total_sales = int(filtered_df['Revenue'].sum())
    total_quantity = int(filtered_df['Quantity'].sum())
    top_category = merged_df.groupby('Category')['Revenue'].sum().idxmax()
    top_location = filtered_df.groupby('Location')['Revenue'].sum().idxmax()

    # Custom HTML for metrics
    box_style = """
        <div style="
            background-color:#f0f2f6;
            padding:10px;
            border-radius:12px;
            text-align:center;
            box-shadow:0 2px 5px rgba(0,0,0,0.05);
            font-size: 14px;
        ">
            <h6 style="color:#333;margin-bottom:5px;">{icon} {title}</h6>
            <h4 style="color:{color};margin-top:5px;">{value}</h4>
        </div>
    """

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(box_style.format(icon="💰", title="Total Sales", value=f"₹ {total_sales:,}", color="green"), unsafe_allow_html=True)
    with col2:
        st.markdown(box_style.format(icon="📦", title="Quantity Sold", value=f"{total_quantity:,}", color="dodgerblue"), unsafe_allow_html=True)
    with col3:
        st.markdown(box_style.format(icon="🏆", title="Top Category", value=top_category, color="darkorange"), unsafe_allow_html=True)
    with col4:
        st.markdown(box_style.format(icon="📍", title="Top Location", value=top_location, color="purple"), unsafe_allow_html=True)

    # Tabs
    home, sales, trends, products, location, category, shipping = st.tabs([
        "🏠 Home", "📊 Sales", "📈 Trends", "🛒 Products", "🌍 Location", "📂 Category", "🚚 Shipping"])

    # ---------------- HOME ----------------
    with home:
        st.header("Welcome to Dmart Dashboard")
        st.image("E:/be project final/dmart_logo.jpg", use_column_width=False, width=800)

    # ---------------- SALES ----------------
    with sales:
        st.header("Sales Overview")

        st.subheader("Sales by Category")
        category_sales = merged_df.groupby('Category')['Quantity'].sum().reset_index()
        fig = px.bar(category_sales, x='Category', y='Quantity', color='Category',
                    color_discrete_sequence=px.colors.qualitative.Bold, text='Quantity')
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Sales by Location")
        location_sales = df.groupby('Location')['Quantity'].sum().reset_index()
        fig = px.bar(location_sales, x='Location', y='Quantity', color='Location',
                    color_discrete_sequence=px.colors.qualitative.Vivid, text='Quantity')
        st.plotly_chart(fig, use_container_width=True)

    # ---------------- TRENDS ----------------
    with trends:
        st.header("Monthly Sales Trends")
        monthly_sales = filtered_df.groupby(filtered_df['Date'].dt.to_period('M'))['Quantity'].sum().reset_index()
        monthly_sales['Date'] = monthly_sales['Date'].dt.to_timestamp()
        fig = px.line(monthly_sales, x='Date', y='Quantity', title="Monthly Quantity Sold",
                    markers=True, color_discrete_sequence=["#FF6F61"])
        st.plotly_chart(fig, use_container_width=True)

    # ---------------- PRODUCTS ----------------
    with products:
        st.header("Product Insights")

        product_list = merged_df['Name'].dropna().unique()
        selected_product = st.selectbox("Select a Product", options=np.append(["All"], np.sort(product_list)))

        if selected_product != "All":
            product_data = merged_df[merged_df['Name'] == selected_product]
            total_quantity = int(product_data['Quantity'].sum())
            total_revenue = float(product_data['Revenue'].sum())

            st.metric("Total Quantity Sold", total_quantity)
            st.metric("Total Revenue", f"₹ {total_revenue:,.2f}")

            product_trend = product_data.groupby('Date')['Quantity'].sum().reset_index()
            fig = px.line(product_trend, x='Date', y='Quantity',
                        title=f"Sales Trend for {selected_product}",
                        color_discrete_sequence=["#00BFFF"])
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.subheader("Top 10 Selling Products")
            top_products = filtered_df.groupby('Name')['Quantity'].sum().sort_values(ascending=False).head(10).reset_index()
            fig = px.bar(top_products, x='Quantity', y='Name', orientation='h',
                        title="Top 10 Products by Quantity",
                        color='Name', color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Top 10 Revenue Products")
            top_revenue = filtered_df.groupby('Name')['Revenue'].sum().sort_values(ascending=False).head(10).reset_index()
            fig = px.bar(top_revenue, x='Revenue', y='Name', orientation='h',
                        title="Top 10 Products by Revenue",
                        color='Name', color_discrete_sequence=px.colors.qualitative.Prism)
            st.plotly_chart(fig, use_container_width=True)

    # ---------------- LOCATION ----------------
    with location:
        st.header("Location Insights")

        location_sales = df.groupby('Location')['Quantity'].sum().reset_index()
        location_sales['lat'] = np.random.uniform(17.0, 20.0, len(location_sales))
        location_sales['lon'] = np.random.uniform(73.0, 76.0, len(location_sales))

        fig = px.scatter_mapbox(location_sales, lat='lat', lon='lon', size='Quantity', color='Location',
                                color_discrete_sequence=px.colors.qualitative.Safe,
                                hover_name='Location', zoom=5, mapbox_style="open-street-map")
        st.plotly_chart(fig, use_container_width=True)

    # ---------------- CATEGORY ----------------
    with category:
        st.header("Category-Level Analysis")

        category_list = merged_df['Category'].dropna().unique()
        selected_cat = st.selectbox("Select a Category", options=np.append(["All"], np.sort(category_list)))

        if selected_cat != "All":
            cat_data = merged_df[merged_df['Category'] == selected_cat]

            st.subheader(f"Revenue Breakdown for '{selected_cat}'")
            subcat = cat_data.groupby('SubCategory')['Revenue'].sum().reset_index()
            fig = px.pie(subcat, names='SubCategory', values='Revenue',
                        color_discrete_sequence=px.colors.sequential.Rainbow)
            st.plotly_chart(fig, use_container_width=True)

            top_cat_prods = cat_data.groupby('Name')['Revenue'].sum().sort_values(ascending=False).head(10).reset_index()
            st.subheader("Top 10 Products in this Category")
            fig = px.bar(top_cat_prods, x='Revenue', y='Name', orientation='h',
                        color='Name', color_discrete_sequence=px.colors.qualitative.Alphabet)
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.subheader("Revenue by Category")
            cat_rev = merged_df.groupby('Category')['Revenue'].sum().reset_index()
            fig = px.bar(cat_rev, x='Revenue', y='Category', orientation='h',
                        color='Category', color_discrete_sequence=px.colors.qualitative.Set1)
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("SubCategory Performance")
            subcat = merged_df.groupby('SubCategory')['Revenue'].sum().reset_index()
            fig = px.pie(subcat, names='SubCategory', values='Revenue',
                        color_discrete_sequence=px.colors.sequential.Viridis)
            st.plotly_chart(fig, use_container_width=True)

    # ---------------- SHIPPING ----------------
    with shipping:
        st.header("Order & Shipping Overview")

        daily = filtered_df.groupby('Date').agg({'Quantity': 'sum', 'UnitPrice': 'mean'}).reset_index()

        st.subheader("Orders Over Time")
        fig = px.line(daily, x='Date', y='Quantity',
                    title="Daily Order Quantities",
                    color_discrete_sequence=["#4CAF50"])
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Average Unit Price Over Time")
        fig = px.line(daily, x='Date', y='UnitPrice',
                    title="Daily Avg Unit Price",
                    color_discrete_sequence=["#FF69B4"])
        st.plotly_chart(fig, use_container_width=True)

