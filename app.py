import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

# --- 1. SETTINGS ---
st.set_page_config(page_title="E-Commerce Dashboard", page_icon="🛒", layout="wide")

# --- 2. BACKEND CONNECTION (SQL Data Fetching) ---
@st.cache_data
def get_data_from_db():
    db_path = r'C:\Users\hp\OneDrive\Desktop\Ecommerce_EDA_Project\anaconda_projects\ecommerce_backend.db'
    conn = sqlite3.connect(db_path)
    
    # Asli SQL Query (Ab isme Delivery aur Payment bhi hai)
    query = """
    SELECT 
        o.order_id, 
        o.order_purchase_timestamp, 
        o.order_delivered_customer_date,
        p.payment_value, 
        p.payment_type,
        c.customer_city 
    FROM orders_table o
    JOIN payments_table p ON o.order_id = p.order_id
    JOIN customers_table c ON o.customer_id = c.customer_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Dates ko theek format mein karna
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'])
    return df

df = get_data_from_db()

# --- 3. FRONTEND / UI MENU ---
st.sidebar.title("🛒 Dashboard Menu")
page = st.sidebar.radio("Go to", [
    "🏠 Home", 
    "📈 Revenue Engine", 
    "🚚 Delivery Performance", 
    "📍 Top Cities", 
    "💳 Payment Methods"
])

# --- 4. PAGES LOGIC ---
if page == "🏠 Home":
    st.title("Brazilian E-Commerce Analytics 🇧🇷")
    st.success("🟢 Connected to SQLite Backend Database successfully. Full Data fetched using SQL Joins.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", f"{df['order_id'].nunique():,}")
    col2.metric("Total Revenue", f"R$ {df['payment_value'].sum():,.0f}")
    col3.metric("Backend Status", "Active 🟢")
    
    # YAHAN CHANGE KIYA HAI - use_container_width=True
    st.image("https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=800&q=80", use_container_width=True)
    st.markdown("### Welcome to the Full-Stack Analytics Dashboard")
    st.write("Use the sidebar on the left to navigate through different business insights.")

elif page == "📈 Revenue Engine":
    st.title("🚀 The Revenue Engine")
    st.markdown("Monthly revenue trend over the years.")
    
    df['month_year'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)
    monthly_revenue = df.groupby('month_year')['payment_value'].sum().reset_index()
    
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(data=monthly_revenue, x='month_year', y='payment_value', marker='o', color='crimson', ax=ax)
    plt.xticks(rotation=45)
    plt.xlabel("Month-Year")
    plt.ylabel("Revenue (BRL)")
    st.pyplot(fig)

elif page == "🚚 Delivery Performance":
    st.title("🚚 Delivery Performance")
    st.markdown("How many days does it take to deliver an order?")
    
    # Delivery days calculate karna
    df['delivery_days'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days
    
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(df['delivery_days'].dropna(), bins=50, kde=True, color='purple', ax=ax)
    plt.xlim(0, 50)
    plt.xlabel("Days to Deliver")
    plt.ylabel("Number of Orders")
    st.pyplot(fig)
    
    st.info(f"💡 Average delivery time is **{df['delivery_days'].mean():.1f} days**.")

elif page == "📍 Top Cities":
    st.title("📍 Customer Hotspots")
    st.markdown("Top 10 cities generating the most orders.")
    
    top_cities = df['customer_city'].value_counts().head(10)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(y=top_cities.index, x=top_cities.values, palette='viridis', ax=ax)
    plt.xlabel("Total Orders")
    plt.ylabel("City")
    st.pyplot(fig)

elif page == "💳 Payment Methods":
    st.title("💳 Payment Preferences")
    st.markdown("How do Brazilian customers prefer to pay?")
    
    payment_counts = df['payment_type'].value_counts()
    
    fig, ax = plt.subplots(figsize=(8, 8))
    plt.pie(payment_counts.values, labels=payment_counts.index, autopct='%1.1f%%', 
            colors=sns.color_palette("pastel"), startangle=140)
    st.pyplot(fig)