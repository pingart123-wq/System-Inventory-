import streamlit as st
import pandas as pd
import json
import os
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
    """Loads inventory from JSON file or initializes default data."""
    if not os.path.exists(DATA_FILE):
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
            if not data:
                return pd.DataFrame(columns=["id", "name", "category", "price", "qty"])
            # Ensure price and qty are numeric
            df = pd.DataFrame(data)
            df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0.0)
            df['qty'] = pd.to_numeric(df['qty'], errors='coerce').fillna(0).astype(int)
            return df
    except Exception:
        st.error("Error loading data file. Initializing empty inventory.")
        return pd.DataFrame(columns=["id", "name", "category", "price", "qty"])

def save_data(df):
    """Saves DataFrame inventory to JSON file."""
    data = df.to_dict(orient="records")
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# Initialize Session State
if 'inventory' not in st.session_state:
    st.session_state.inventory = load_data()
if 'current_view' not in st.session_state:
    st.session_state.current_view = "Inventory"

# --- HELPER FUNCTIONS ---

def set_view(view):
    """Callback function for navigation buttons."""
    st.session_state.current_view = view

def delete_item_callback(item_id):
    """Callback function for deleting an item."""
    st.session_state.inventory = st.session_state.inventory[st.session_state.inventory['id'] != item_id]
    save_data(st.session_state.inventory)
    st.toast("Item Purged.")
    # No rerun needed here if button used inside a container that refreshes, 
    # but strictly speaking, st.rerun() ensures the UI updates immediately.
    st.rerun()

# --- MODAL: ADD ITEM (Corrected @st.dialog usage) ---
@st.dialog("New Component")
def show_add_item_dialog():
    with st.form("add_item_form"):
        name = st.text_input("Item Name", placeholder="e.g. RTX 4090")
        category = st.selectbox("Category", ["GPU", "CPU", "Mobile", "Laptop", "Accessory", "Other"])
        
        c1, c2 = st.columns(2)
        price = c1.number_input("Price (₱)", min_value=0.0, step=100.0)
        qty = c2.number_input("Quantity", min_value=0, step=1)
        
        submitted = st.form_submit_button("ADD TO VAULT")
        
        if submitted:
            if not name:
                st.error("Item Name is required.")
            else:
                # Generate ID
                new_id = int(time.time() * 1000)
                new_row = pd.DataFrame([{
                    "id": new_id, 
                    "name": name, 
                    "category": category, 
                    "price": float(price), 
                    "qty": int(qty)
                }])
                
                # Update State and Save
                st.session_state.inventory = pd.concat([new_row, st.session_state.inventory], ignore_index=True)
                save_data(st.session_state.inventory)
                st.success(f"Component '{name}' added.")
                time.sleep(0.5) # Brief pause to show success message
                st.rerun()

# --- CUSTOM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css');

    /* Variables */
    :root {
        --bg-dark: #0a0b10;
        --panel-bg: #13141c;
        --accent-cyan: #00f3ff;
        --accent-purple: #bc13fe;
        --text-main: #e0e6ed;
        --text-muted: #94a3b8;
        --danger: #ff2a6d;
    }

    .stApp {
        background-color: var(--bg-dark);
        background-image: radial-gradient(circle at 10% 20%, rgba(188, 19, 254, 0.1) 0%, transparent 20%), 
                          radial-gradient(circle at 90% 80%, rgba(0, 243, 255, 0.1) 0%, transparent 20%);
        font-family: 'Rajdhani', sans-serif;
    }

    h1, h2, h3, h4, .stSidebar h1, .stSidebar h2 { 
        font-family: 'Orbitron', sans-serif !important; 
        color: var(--text-main) !important; 
    }
    p, div, span, label, .stMarkdown { 
        font-family: 'Rajdhani', sans-serif !important; 
        color: var(--text-main); 
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: var(--panel-bg);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    .sidebar-logo {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.5rem;
        color: var(--accent-cyan);
        margin-bottom: 2rem;
        text-shadow: 0 0 10px rgba(0, 243, 255, 0.5);
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

    /* Sidebar Nav Buttons */
    section[data-testid="stSidebar"] div.stButton > button {
        border-radius: 8px;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 500;
        margin: 5px 0;
        height: 3rem;
        letter-spacing: 2px; 
    }
    
    /* Active Nav */
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background: rgba(0, 243, 255, 0.1) !important;
        color: var(--accent-cyan) !important;
        border: 1px solid var(--accent-cyan) !important;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.4);
    }
    /* Inactive Nav */
    section[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.05) !important;
        color: var(--text-main) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    section[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
        background: rgba(0, 243, 255, 0.08) !important;
        color: var(--accent-cyan) !important;
    }

    /* Delete Button */
    button[kind="secondary"] {
        background: rgba(255, 42, 109, 0.1) !important;
        color: var(--danger) !important;
        border: 1px solid var(--danger) !important;
        border-radius: 8px !important;
    }
    
    /* Cards */
    .stContainer {
        border-radius: 16px !important;
        background: var(--panel-bg);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .stContainer:hover {
        border-color: var(--accent-cyan) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div class="sidebar-logo">
            <i class="fa-solid fa-microchip"></i> ELECTRO<b>VAULT</b>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Navigation")

    nav_options = ["Inventory", "Analytics", "Settings"]
    
    for view in nav_options:
        is_active = (st.session_state.current_view == view)
        if st.button(
            f"<< {view.upper()} >>", 
            key=f"nav_{view}", 
            use_container_width=True, 
            type="primary" if is_active else "secondary"
        ):
             set_view(view)
             st.rerun()

    st.divider()
    
    # Add Item Button triggers the function decorated with @st.dialog
    if st.button("<< + ADD ITEM >>", key="sidebar_add_item_button", use_container_width=True):
        show_add_item_dialog()
    
    st.markdown('<div style="margin-top: 100px;"></div>', unsafe_allow_html=True)
    st.markdown("<center style='color:var(--text-muted); font-size:0.8rem;'>Streamlit v1.0<br>CyberSec Protocol Active</center>", unsafe_allow_html=True)


# --- MAIN LOGIC ---
df = st.session_state.inventory

# 1. INVENTORY VIEW
if st.session_state.current_view == "Inventory":
    st.title("Inventory Index")
    
    # Search Bar
    search_term = st.text_input("Search", placeholder="Search components...", label_visibility="collapsed")
    
    # Filter Logic
    df_display = df.copy()
    if search_term:
        df_display = df_display[
            df_display['name'].str.contains(search_term, case=False, na=False) | 
            df_display['category'].str.contains(search_term, case=False, na=False)
        ]

    # Stats
    total_items = df['qty'].sum() if not df.empty else 0
    total_value = (df['price'] * df['qty']).sum() if not df.empty else 0
    low_stock = len(df[df['qty'] < 5]) if not df.empty else 0

    s1, s2, s3 = st.columns(3)
    s1.metric("Total Items", f"{total_items}")
    s2.metric("Inventory Value", f"₱{total_value:,.2f}")
    s3.metric("Low Stock Alerts", f"{low_stock}", delta_color="inverse")

    st.markdown("---")

    # Grid Rendering
    if df_display.empty:
        st.info("No items found in the vault matching your search.")
    else:
        # Define 3 strict columns
        cols = st.columns(3)
        
        category_icons = {
            'GPU': 'fa-memory', 'CPU': 'fa-microchip', 'Mobile': 'fa-mobile-screen',
            'Laptop': 'fa-laptop', 'Accessory': 'fa-headphones', 'Other': 'fa-box'
        }
        
        # FIX: Use enumerate on df_display.iterrows() to ensure grid fills 0-1-2-0-1-2 regardless of search filtering
        for i, (index, row) in enumerate(df_display.iterrows()):
            item_id = row['id']
            col_index = i % 3
            
            with cols[col_index]:
                with st.container(border=True):
                    icon_class = category_icons.get(row['category'], 'fa-box')
                    stock_color = "var(--danger)" if row['qty'] < 5 else "var(--accent-cyan)"
                    
                    st.markdown(f"""
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="width: 50px; height: 50px; background: rgba(0, 243, 255, 0.1); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: var(--accent-cyan); font-size: 1.5rem; margin-bottom:10px;">
                                <i class="fa-solid {icon_class}"></i>
                            </div>
                            <span style="color:var(--accent-purple); font-size:0.8rem; font-weight:700;">{row['category']}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.subheader(row['name'])
                    
                    sc1, sc2 = st.columns(2)
                    sc1.caption("Price")
                    sc1.markdown(f"**₱{row['price']:,.2f}**")
                    
                    sc2.caption("Stock")
                    sc2.markdown(f"<span style='color:{stock_color}; font-weight:bold; font-size:1.1rem;'>{row['qty']}</span>", unsafe_allow_html=True)
                    
                    st.markdown("---")

                    if st.button("DELETE", key=f"del_{item_id}", type="secondary", use_container_width=True):
                        delete_item_callback(item_id)

# 2. ANALYTICS VIEW
elif st.session_state.current_view == "Analytics":
    st.title("System Diagnostics")
    
    col_charts1, col_charts2 = st.columns([2, 1])
    
    with col_charts1:
        st.subheader("Inventory Value Distribution")
        if not df.empty:
            chart_data = df.copy()
            chart_data['total_val'] = chart_data['price'] * chart_data['qty']
            chart_data = chart_data.groupby('category')['total_val'].sum().reset_index()
            chart_data = chart_data.sort_values(by='total_val', ascending=False)
            chart_data.set_index('category', inplace=True) 
            st.bar_chart(chart_data)
        else:
            st.warning("No data available for charts.")

    with col_charts2:
        st.subheader("Top Assets by Value")
        if not df.empty:
            df_temp = df.copy()
            df_temp['item_value'] = df_temp['price'] * df_temp['qty']
            top_items = df_temp.sort_values(by='price', ascending=False).head(5)
            
            st.dataframe(
                top_items[['name', 'price']], 
                hide_index=True, 
                column_config={
                    "name": "Asset",
                    "price": st.column_config.NumberColumn("Unit Value", format="₱%.2f")
                }
            )
        else:
            st.info("Inventory is empty.")

# 3. SETTINGS VIEW
elif st.session_state.current_view == "Settings":
    st.title("Configuration")
    
    with st.container(border=True):
        st.subheader("Export Database")
        st.caption("Download your current inventory as a JSON file.")
        
        json_str = df.to_json(orient="records", indent=4)
        
        st.download_button(
            label="EXPORT JSON",
            data=json_str,
            file_name=f"electrovault_backup_{int(time.time())}.json",
            mime="application/json",
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        st.subheader("System Purge", help="Permanently delete all data.")
        st.markdown(f"<p style='color:var(--danger)'>Permanently delete all inventory records.</p>", unsafe_allow_html=True)
        
        if st.button("PURGE ALL DATA", type="primary", use_container_width=True):
            st.session_state.inventory = pd.DataFrame(columns=["id", "name", "category", "price", "qty"])
            save_data(st.session_state.inventory)
            st.toast("System Purged. Memory cleared.")
            time.sleep(1)
            st.rerun()

    st.markdown("<br><center style='color:var(--text-muted)'>ElectroVault Streamlit v1.0<br>Secure Connection Established</center>", unsafe_allow_html=True)
