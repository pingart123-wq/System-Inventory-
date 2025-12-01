import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px  # <-- RE-ADDED PLOTLY IMPORT
import time

# --- CONFIGURATION ---
st.set_page_config(
    page_title="ElectroVault | Inventory Manager",
    page_icon="🔌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DATA MANAGEMENT (JSON PERSISTENCE) ---
DATA_FILE = "electro_inventory.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        # Default initial data matching your HTML
        default_data = [
            {"id": 1, "name": "GeForce RTX 4090", "category": "GPU", "price": 109990.00, "qty": 3},
            {"id": 2, "name": "MacBook Pro M2", "category": "Laptop", "price": 84990.00, "qty": 8},
            {"id": 3, "name": "Samsung S24 Ultra", "category": "Mobile", "price": 75990.00, "qty": 12},
            {"id": 4, "name": "Sony WH-1000XM5", "category": "Accessory", "price": 18999.00, "qty": 25},
        ]
        return pd.DataFrame(default_data)
    
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            return pd.DataFrame(data)
    except:
        return pd.DataFrame(columns=["id", "name", "category", "price", "qty"])

def save_data(df):
    # Convert dataframe to list of dicts and save
    data = df.to_dict(orient="records")
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# Initialize Session State
if 'inventory' not in st.session_state:
    st.session_state.inventory = load_data()

# --- CUSTOM CSS (THEME) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');

    /* Global Variables based on your CSS */
    :root {
        --bg-dark: #0a0b10;
        --panel-bg: #13141c;
        --accent-cyan: #00f3ff;
        --accent-purple: #bc13fe;
        --text-main: #e0e6ed;
        --text-muted: #94a3b8;
        --danger: #ff2a6d;
    }

    /* App Background */
    .stApp {
        background-color: var(--bg-dark);
        background-image: radial-gradient(circle at 10% 20%, rgba(188, 19, 254, 0.1) 0%, transparent 20%), radial-gradient(circle at 90% 80%, rgba(0, 243, 255, 0.1) 0%, transparent 20%);
        font-family: 'Rajdhani', sans-serif;
    }

    /* Text Styling */
    h1, h2, h3 { font-family: 'Orbitron', sans-serif !important; color: var(--text-main) !important; }
    p, div, span { font-family: 'Rajdhani', sans-serif !important; color: var(--text-main); }

    /* Custom Cards (Metrics) */
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 4px solid var(--accent-cyan);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-purple), #7a00ff);
        color: white;
        border: none;
        border-radius: 50px;
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        transition: 0.3s;
    }
    .stButton > button:hover {
        box-shadow: 0 0 15px rgba(188, 19, 254, 0.6);
        transform: translateY(-2px);
    }

    /* Delete Button Specifics */
    button[kind="secondary"] {
        background: rgba(255, 42, 109, 0.1) !important;
        color: var(--danger) !important;
        border: 1px solid var(--danger) !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: var(--panel-bg);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    
    /* Input Fields */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(0,0,0,0.3);
        color: white;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR & NAVIGATION ---
with st.sidebar:
    st.markdown("""
        <div style="font-family: 'Orbitron'; font-size: 1.5rem; color: #00f3ff; margin-bottom: 2rem; text-shadow: 0 0 10px rgba(0, 243, 255, 0.5);">
            <i class="fa-solid fa-microchip"></i> ELECTRO<b>VAULT</b>
        </div>
    """, unsafe_allow_html=True)
    
    selected_view = st.radio("Navigation", ["Inventory", "Analytics", "Settings"], label_visibility="collapsed")
    
    st.divider()
    
    # "Add Item" via Streamlit Dialog (acts like a Modal)
    @st.dialog("Add New Component")
    def add_item_modal():
        with st.form("add_item_form"):
            new_name = st.text_input("Item Name", placeholder="e.g. RTX 4090")
            new_cat = st.selectbox("Category", ["GPU", "CPU", "Mobile", "Laptop", "Accessory", "Other"])
            
            c1, c2 = st.columns(2)
            new_price = c1.number_input("Price (₱)", min_value=0.0, step=100.0)
            new_qty = c2.number_input("Quantity", min_value=0, step=1)
            
            submitted = st.form_submit_button("ADD TO VAULT")
            
            if submitted:
                if new_name:
                    new_id = int(time.time()) # Simple ID generation
                    new_row = pd.DataFrame([{
                        "id": new_id, 
                        "name": new_name, 
                        "category": new_cat, 
                        "price": new_price, 
                        "qty": new_qty
                    }])
                    st.session_state.inventory = pd.concat([new_row, st.session_state.inventory], ignore_index=True)
                    save_data(st.session_state.inventory)
                    st.success("Item Added!")
                    st.rerun()
                else:
                    st.error("Name is required.")

    if st.button("+ ADD ITEM", use_container_width=True):
        add_item_modal()

# --- LOGIC & VIEWS ---

df = st.session_state.inventory

# 1. INVENTORY VIEW
if selected_view == "Inventory":
    # Header & Search
    c1, c2 = st.columns([3, 1])
    with c1:
        search_term = st.text_input("Search", placeholder="Search components...", label_visibility="collapsed")
    
    # Filter Logic
    if search_term:
        df_display = df[df['name'].str.contains(search_term, case=False) | df['category'].str.contains(search_term, case=False)]
    else:
        df_display = df

    # Stats
    total_items = df['qty'].sum() if not df.empty else 0
    total_value = (df['price'] * df['qty']).sum() if not df.empty else 0
    low_stock = len(df[df['qty'] < 5]) if not df.empty else 0

    s1, s2, s3 = st.columns(3)
    s1.metric("Total Items", f"{total_items}")
    s2.metric("Inventory Value", f"₱{total_value:,.2f}")
    s3.metric("Low Stock Alerts", f"{low_stock}", delta_color="inverse")

    st.markdown("---")

    # Inventory Grid (Using containers to simulate cards)
    if df_display.empty:
        st.info("No items found in the vault.")
    else:
        # Create a grid layout (e.g., 3 columns wide)
        cols = st.columns(3)
        
        for index, row in df_display.iterrows():
            # Cycle through columns
            with cols[index % 3]:
                with st.container(border=True):
                    # Category Badge
                    st.markdown(f"**{row['category']}**", unsafe_allow_html=True)
                    # Name
                    st.subheader(row['name'])
                    
                    # Stats inside card
                    sc1, sc2 = st.columns(2)
                    sc1.caption("Price")
                    sc1.markdown(f"**₱{row['price']:,.2f}**")
                    
                    sc2.caption("Stock")
                    stock_color = "red" if row['qty'] < 5 else "#00f3ff"
                    sc2.markdown(f"<span style='color:{stock_color}; font-weight:bold'>{row['qty']}</span>", unsafe_allow_html=True)
                    
                    # Delete Button
                    if st.button("DELETE", key=f"del_{row['id']}", type="secondary", use_container_width=True):
                        st.session_state.inventory = df[df['id'] != row['id']]
                        save_data(st.session_state.inventory)
                        st.rerun()

# 2. ANALYTICS VIEW
elif selected_view == "Analytics":
    st.title("System Diagnostics")
    
    col_charts1, col_charts2 = st.columns([2, 1])
    
    with col_charts1:
        st.subheader("Inventory Value Distribution")
        if not df.empty:
            df['total_val'] = df['price'] * df['qty']
            chart_data = df.groupby('category')['total_val'].sum().reset_index()
            
            # RE-ADDED PLOTLY CODE
            fig = px.bar(chart_data, x='total_val', y='category', orientation='h', 
                         text_auto='.2s', color='total_val',
                         color_continuous_scale=['#00f3ff', '#bc13fe'])
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e0e6ed', family="Rajdhani"),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available for charts.")

    with col_charts2:
        st.subheader("Most Expensive Assets")
        if not df.empty:
            top_items = df.sort_values(by='price', ascending=False).head(5)
            # Display as a clean table
            st.dataframe(
                top_items[['name', 'price']], 
                hide_index=True, 
                column_config={
                    "name": "Asset",
                    "price": st.column_config.NumberColumn("Value (₱)", format="₱%.2f")
                }
            )

# 3. SETTINGS VIEW
elif selected_view == "Settings":
    st.title("System Configuration")
    
    with st.container(border=True):
        st.subheader("Export Database")
        st.caption("Download your current inventory as a JSON file.")
        
        json_str = df.to_json(orient="records")
        st.download_button(
            label="DOWNLOAD JSON",
            data=json_str,
            file_name=f"electrovault_backup_{int(time.time())}.json",
            mime="application/json",
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        st.subheader("System Purge")
        st.caption("Permanently delete all inventory records.")
        
        if st.button("PURGE ALL DATA", type="primary", use_container_width=True):
            st.session_state.inventory = pd.DataFrame(columns=["id", "name", "category", "price", "qty"])
            save_data(st.session_state.inventory)
            st.success("System Purged. Memory cleared.")
            time.sleep(1)
            st.rerun()

    st.markdown("<br><center style='color:#94a3b8'>ElectroVault Streamlit v1.0<br>Secure Connection Established</center>", unsafe_allow_html=True)
