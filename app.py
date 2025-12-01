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
            # Ensure price and qty are numeric
            df = pd.DataFrame(data)
            df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
            df['qty'] = pd.to_numeric(df['qty'], errors='coerce').fillna(0).astype(int)
            return df
    except Exception:
        # Return empty DataFrame on error
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
    # st.rerun() # Removed redundant rerun call if placed in button logic

def add_item_callback(new_name, new_cat, new_price, new_qty):
    """Callback function for adding a new item."""
    if not new_name:
        st.error("Item Name is required.")
        return

    # Generate a unique ID using current timestamp
    new_id = int(time.time() * 1000)
    
    new_row = pd.DataFrame([{
        "id": new_id, 
        "name": new_name, 
        "category": new_cat, 
        "price": float(new_price), 
        "qty": int(new_qty)
    }])
    
    # Prepend new item and save
    st.session_state.inventory = pd.concat([new_row, st.session_state.inventory], ignore_index=True)
    save_data(st.session_state.inventory)
    st.success(f"Component '{new_name}' added to Vault.")
    st.rerun()

def delete_item_callback(item_id):
    """Callback function for deleting an item."""
    st.session_state.inventory = st.session_state.inventory[st.session_state.inventory['id'] != item_id]
    save_data(st.session_state.inventory)
    st.toast("Item Purged.")
    st.rerun()

# --- CUSTOM CSS (HTML/JS theme translated to Streamlit CSS) ---
# Note: Added CSS for the sidebar buttons
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');

    /* Variables for Dark Theme */
    :root {
        --bg-dark: #0a0b10;
        --panel-bg: #13141c;
        --accent-cyan: #00f3ff;
        --accent-purple: #bc13fe;
        --text-main: #e0e6ed;
        --text-muted: #94a3b8;
        --danger: #ff2a6d;
    }

    /* Streamlit overrides for background, fonts, and global text color */
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

    /* Sidebar Styling */
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
    
    /* Custom Styling for Sidebar Navigation Buttons */
    /* This overrides the default primary/secondary colors to use the custom theme */
    div.stButton > button {
        /* General styling for all custom buttons */
        border-radius: 8px;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        margin: 5px 0; /* Add vertical spacing */
        transition: 0.3s;
    }

    /* Primary Buttons (Active State/Major Actions) */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent-purple), #7a00ff) !important;
        color: white !important;
        border: 1px solid var(--accent-purple) !important;
    }
    div.stButton > button[kind="primary"]:hover {
        box-shadow: 0 0 15px rgba(188, 19, 254, 0.6);
        transform: translateY(-1px);
    }

    /* Secondary Buttons (Inactive State/Delete/Sidebar Nav) */
    div.stButton > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.05) !important; /* Muted background */
        color: var(--text-main) !important; /* Main text color */
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        background: rgba(0, 243, 255, 0.1) !important; /* Hover effect */
        border: 1px solid var(--accent-cyan) !important;
        color: var(--accent-cyan) !important;
    }

    /* Input Fields */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(0,0,0,0.3);
        color: white;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Custom Card/Metric Styling (replaces stat-card from HTML) */
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 4px solid var(--accent-cyan);
    }
    /* Metric Value Styling */
    div[data-testid="stMetricValue"] {
        font-family: 'Orbitron'; 
        font-size: 2rem; 
        color: var(--text-main);
    }
    
    /* Secondary Buttons (e.g., DELETE in card) */
    /* Override for the specific delete button look */
    button[kind="secondary"] {
        background: rgba(255, 42, 109, 0.1) !important;
        color: var(--danger) !important;
        border: 1px solid var(--danger) !important;
        border-radius: 8px !important;
    }
    
    /* Inventory Item Card Styling (using st.container) */
    .stContainer {
        border-radius: 16px !important;
        background: var(--panel-bg);
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .stContainer:hover {
        border-color: var(--accent-cyan) !important;
    }
    
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR & NAVIGATION (FIXED) ---
with st.sidebar:
    st.markdown("""
        <div class="sidebar-logo">
            <i class="fa-solid fa-microchip"></i> ELECTRO<b>VAULT</b>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Navigation")

    # Navigation is handled by simple buttons that call set_view
    nav_options = [("Inventory", "fa-layer-group"), ("Analytics", "fa-chart-line"), ("Settings", "fa-gear")]
    
    # Use native Streamlit buttons for reliable navigation
    for view, icon in nav_options:
        is_active = (st.session_state.current_view == view)
        
        # Use a consistent label with an icon
        button_label = f"<i class='fa-solid {icon}'></i> {view}"
        
        # Streamlit's primary type is used for the active view to highlight it
        # and secondary for the inactive views.
        if st.button(
            button_label, 
            key=f"nav_{view}", 
            use_container_width=True, 
            type="primary" if is_active else "secondary",
            help=f"Go to {view} view"
        ):
            set_view(view)
            st.rerun() # Trigger a rerun after setting the new view

    st.divider()
    
    # "Add Item" via Streamlit Dialog
    # Logic to show the dialog
    if st.button("+ ADD ITEM", key="sidebar_add_item", use_container_width=True):
        st.session_state.show_add_item_dialog = True
        st.rerun() # Rerunning to show the dialog
    
    st.markdown('<div style="margin-top: 100px;"></div>', unsafe_allow_html=True)
    
    st.markdown("<center style='color:var(--text-muted); font-size:0.8rem;'>Streamlit v1.0<br>CyberSec Protocol Active</center>", unsafe_allow_html=True)

# --- ADD ITEM DIALOG (MODAL) ---
if 'show_add_item_dialog' in st.session_state and st.session_state.show_add_item_dialog:
    # Use st.dialog to replicate the modal experience
    with st.dialog("New Component"):
        with st.form("add_item_form"):
            name = st.text_input("Item Name", placeholder="e.g. RTX 4090", key="dialog_name")
            category = st.selectbox("Category", ["GPU", "CPU", "Mobile", "Laptop", "Accessory", "Other"], key="dialog_cat")
            
            c1, c2 = st.columns(2)
            price = c1.number_input("Price (₱)", min_value=0.0, step=100.0, key="dialog_price")
            qty = c2.number_input("Quantity", min_value=0, step=1, key="dialog_qty")
            
            # Using the custom primary styling for the submit button
            submitted = st.form_submit_button("ADD TO VAULT")
            
            if submitted:
                # Call the callback with collected values
                add_item_callback(name, category, price, qty)
                # Cleanup state after submission
                st.session_state.show_add_item_dialog = False
            
        # Add a close button logic for the dialog (using secondary style)
        if st.button("Cancel", key="dialog_cancel", type="secondary"):
            st.session_state.show_add_item_dialog = False
            st.rerun()

# --- LOGIC & VIEWS ---

df = st.session_state.inventory

# 1. INVENTORY VIEW
if st.session_state.current_view == "Inventory":
    st.title("Inventory Index")
    
    col_header, col_add = st.columns([3, 1])
    
    with col_header:
        search_term = st.text_input("Search", placeholder="Search components...", label_visibility="collapsed")
    
    # Filter Logic
    df_display = df.copy()
    if search_term:
        df_display = df_display[
            df_display['name'].str.contains(search_term, case=False, na=False) | 
            df_display['category'].str.contains(search_term, case=False, na=False)
        ]

    # Stats Calculation
    total_items = df['qty'].sum() if not df.empty else 0
    total_value = (df['price'] * df['qty']).sum() if not df.empty else 0
    low_stock = len(df[df['qty'] < 5]) if not df.empty else 0

    s1, s2, s3 = st.columns(3)
    s1.metric("Total Items", f"{total_items}")
    s2.metric("Inventory Value", f"₱{total_value:,.2f}")
    s3.metric("Low Stock Alerts", f"{low_stock}", delta_color="inverse")

    st.markdown("---")

    # Inventory Grid Rendering (3 columns)
    if df_display.empty:
        st.info("No items found in the vault matching your search.")
    else:
        # Define grid columns
        cols = st.columns(3)
        
        # Dictionary to map category to Font Awesome icon (for visual appeal)
        category_icons = {
            'GPU': 'fa-memory', 'CPU': 'fa-microchip', 'Mobile': 'fa-mobile-screen',
            'Laptop': 'fa-laptop', 'Accessory': 'fa-headphones', 'Other': 'fa-box'
        }
        
        for index, row in df_display.iterrows():
            item_id = row['id']
            # Determine the current column index (0, 1, or 2)
            col_index = index % 3
            
            with cols[col_index]:
                # Use st.container to create the visual card
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

                    # Delete Button (uses the specific secondary style for danger)
                    if st.button("DELETE", key=f"del_{item_id}", type="secondary", use_container_width=True):
                        delete_item_callback(item_id)
                        
# 2. ANALYTICS VIEW
elif st.session_state.current_view == "Analytics":
    st.title("System Diagnostics")
    
    col_charts1, col_charts2 = st.columns([2, 1])
    
    with col_charts1:
        st.subheader("Inventory Value Distribution")
        if not df.empty:
            # Calculate total value and group by category
            chart_data = df.copy()
            chart_data['total_val'] = chart_data['price'] * chart_data['qty']
            
            # Group by category and sort (like the HTML version)
            chart_data = chart_data.groupby('category')['total_val'].sum().reset_index()
            chart_data = chart_data.sort_values(by='total_val', ascending=False)
            chart_data.set_index('category', inplace=True) 

            # Use Streamlit's native bar chart
            st.bar_chart(chart_data)
        else:
            st.warning("No data available for charts.")

    with col_charts2:
        st.subheader("Top Assets by Value")
        if not df.empty:
            df['item_value'] = df['price'] * df['qty']
            # Find the top 5 most valuable individual items (like HTML version)
            top_items = df.sort_values(by='price', ascending=False).head(5)
            
            st.dataframe(
                top_items[['name', 'price']], 
                hide_index=True, 
                column_config={
                    "name": "Asset",
                    "price": st.column_config.NumberColumn("Unit Value (₱)", format="₱%.2f")
                }
            )
        else:
            st.info("Inventory is empty.")

# 3. SETTINGS VIEW
elif st.session_state.current_view == "Settings":
    st.title("Configuration")
    
    # Export Section
    with st.container(border=True):
        st.subheader("Export Database")
        st.caption("Download your current inventory as a JSON file.")
        
        json_str = df.to_json(orient="records", indent=4)
        
        st.download_button(
            label="<i class='fa-solid fa-download'></i> EXPORT JSON",
            data=json_str,
            file_name=f"electrovault_backup_{int(time.time())}.json",
            mime="application/json",
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Purge Section
    with st.container(border=True):
        st.subheader("System Purge", help="Permanently delete all data.")
        st.markdown(f"<p style='color:var(--danger)'>Permanently delete all inventory records.</p>", unsafe_allow_html=True)
        
        # Confirmation logic should ideally use a dialog, but for simplicity, we'll keep the direct action.
        if st.button("PURGE ALL DATA", type="primary", use_container_width=True):
            # Clear inventory
            st.session_state.inventory = pd.DataFrame(columns=["id", "name", "category", "price", "qty"])
            save_data(st.session_state.inventory)
            st.toast("System Purged. Memory cleared.")
            # time.sleep(1) # Removed sleep for faster user experience
            st.rerun()

    st.markdown("<br><center style='color:var(--text-muted)'>ElectroVault Streamlit v1.0<br>Secure Connection Established</center>", unsafe_allow_html=True)
