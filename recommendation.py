def run_recommendation_dashboard():
    # All your code from recommendation.py goes here

    import streamlit as st
    import pandas as pd
    import plotly.graph_objects as go
    from statsmodels.tsa.arima.model import ARIMA
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    import numpy as np
    from mlxtend.frequent_patterns import apriori, association_rules
    from mlxtend.preprocessing import TransactionEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.linear_model import LinearRegression


    # Load datasets
    @st.cache_data
    def load_sales_data():
        try:
            data = pd.read_csv('E:/be project final/dmart_sales_with_names fi.csv')
            data['Date'] = pd.to_datetime(data['Date'], format='%d-%m-%Y', errors='coerce')
            data.dropna(subset=['Date'], inplace=True)
            return data
        except Exception as e:
            st.error(f"Error loading sales data: {e}")
            return pd.DataFrame()

    @st.cache_data
    def load_apriori_data():
        try:
            df = pd.read_csv('E:/be project final/enhanced_apriori_dataset1.csv')
            transactions = df.apply(lambda x: x.dropna().tolist(), axis=1).tolist()
            te = TransactionEncoder()
            te_ary = te.fit(transactions).transform(transactions)
            df_encoded = pd.DataFrame(te_ary, columns=te.columns_)
            return df_encoded, te
        except Exception as e:
            st.error(f"Error loading Apriori data: {e}")
            return pd.DataFrame(), None

    # Train ARIMA Model
    def train_arima_model():
        data = load_sales_data()
        if data.empty:
            return None, None, None, None, None, None, None

        monthly_sales = data.resample('M', on='Date')['Quantity'].sum().reset_index()

        # Define ARIMA order manually
        arima_order = (1, 1, 1)  # (p, d, q) - Can be tuned
        model = ARIMA(monthly_sales['Quantity'], order=arima_order)
        model_fit = model.fit()
        
        predictions = model_fit.predict(start=1, end=len(monthly_sales) - 1)
        forecast = model_fit.forecast(steps=2)

        mae = mean_absolute_error(monthly_sales['Quantity'][1:], predictions)
        rmse = np.sqrt(mean_squared_error(monthly_sales['Quantity'][1:], predictions))
        mape = np.mean(np.abs((monthly_sales['Quantity'][1:] - predictions) / monthly_sales['Quantity'][1:])) * 100
        accuracy = 100 - mape
        
        return monthly_sales, predictions, forecast, mae, rmse, mape, accuracy

    # Hybrid Model Sales Forecasting
    def train_hybrid_model():
        try:
            df = pd.read_csv("E:/be project final/processed_dmart_sales1.csv")
            X = df.drop(columns=["SalesAmount", "Name"], errors='ignore')
            y = df["SalesAmount"]

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            rf = RandomForestRegressor(n_estimators=100, random_state=42)
            dt = DecisionTreeRegressor(random_state=42)
            lr = LinearRegression()

            rf.fit(X_train, y_train)
            dt.fit(X_train, y_train)
            lr.fit(X_train, y_train)

            rf_pred = rf.predict(X_test)
            dt_pred = dt.predict(X_test)
            lr_pred = lr.predict(X_test)

            hybrid_pred = (rf_pred + dt_pred + lr_pred) / 3
            mae = mean_absolute_error(y_test, hybrid_pred)

            df["PredictedSalesAmount"] = (rf.predict(X) + dt.predict(X) + lr.predict(X)) / 3
            product_sales = df.groupby("Name").agg(
                ActualSalesAmount=("SalesAmount", "sum"),
                PredictedSalesAmount=("PredictedSalesAmount", "sum")
            ).reset_index()
            return product_sales, mae
        except Exception as e:
            st.error(f"Error in hybrid model training: {e}")
            return pd.DataFrame(), None

    # Apply Apriori Algorithm
    def apply_apriori_algorithm():
        df_encoded, te = load_apriori_data()
        if df_encoded.empty:
            return pd.DataFrame()

        frequent_itemsets = apriori(df_encoded, min_support=0.01, use_colnames=True)

        rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.0) if not frequent_itemsets.empty else pd.DataFrame()
        return rules

    # Get top recommendations
    def get_top_recommendations(product, rules_df, top_n=5):
        recommendations = rules_df[rules_df['antecedents'].apply(lambda x: product in x)]
        recommendations = recommendations.sort_values(by="lift", ascending=False).head(top_n)
        recommendations = recommendations[['consequents']].explode('consequents')
        return recommendations['consequents'].value_counts().head(top_n).index.tolist()

    # Sales Forecasting UI
    def sales_forecasting():
        st.markdown("## 🔮 Sales Forecasting")
        
        monthly_sales, predictions, forecast, mae, rmse, mape, accuracy = train_arima_model()
        product_sales, hybrid_mae = train_hybrid_model()
        
        if monthly_sales is None:
            st.error("Sales data not available!")
            return

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly_sales['Date'], y=monthly_sales['Quantity'], mode='lines+markers', name='Actual Sales'))
        fig.add_trace(go.Scatter(x=monthly_sales['Date'][1:], y=predictions, mode='lines', name='Predicted Sales (ARIMA)', line=dict(dash='dash')))
        fig.add_trace(go.Scatter(x=pd.date_range(start=monthly_sales['Date'].iloc[-1] + pd.DateOffset(1), periods=2, freq='M'), 
                                y=forecast, mode='lines+markers', name='Forecasted Sales', line=dict(color='red', dash='dot')))

        fig.update_layout(title='Monthly Sales Forecast', xaxis_title='Date', yaxis_title='Sales Quantity', template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📊 Model Accuracy Metrics")
        st.write(f"🎯 ARIMA MAE: {mae:.2f}")
        st.write(f"📏 RMSE: {rmse:.2f}")
        st.write(f"📊 MAPE: {mape:.2f}%")
        st.write(f"🏆 ARIMA Accuracy: {accuracy:.2f}%")
        st.write(f"🤖 Hybrid Model MAE: {hybrid_mae:.2f}")

        st.subheader("📊 Product-wise Sales Predictions (Hybrid Model)")
        if not product_sales.empty:
            selected_product = st.selectbox("Select a product to view predictions:", product_sales["Name"].unique())
            product_data = product_sales[product_sales["Name"] == selected_product]
            st.dataframe(product_data)

    # Product Recommendation Section
    def product_recommendation():
        st.markdown("## 🛍 Product Recommendation (Apriori)")
        
        rules = apply_apriori_algorithm()
        
        if not rules.empty:
            all_products = sorted(set(item for sublist in rules['antecedents'].apply(list) for item in sublist))
            selected_product = st.selectbox("Select a product to get recommendations:", all_products)
            
            if selected_product:
                top_product_recommendations = get_top_recommendations(selected_product, rules)
                st.write(f"Top 5 Product Recommendations for {selected_product}:")
                st.write(top_product_recommendations)
        else:
            st.write("No association rules found.")

    # # Main App
    # st.set_page_config(page_title="D-Mart Sales Dashboard", layout="wide", page_icon="📊")

    with st.sidebar:
        st.title("📊 D-Mart Analytics")
        page = st.radio("Navigation", ["📈 Sales Forecasting", "🤝 Product Recommendation"], index=0)

    if page == "📈 Sales Forecasting":
        sales_forecasting()
    elif page == "🤝 Product Recommendation":
        product_recommendation()



