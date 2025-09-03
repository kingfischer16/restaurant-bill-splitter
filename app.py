import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Restaurant Bill Splitter",
    page_icon="🧾",
    layout="wide"
)

# Initialize session state
if 'bill_items' not in st.session_state or not isinstance(st.session_state.bill_items, list):
    st.session_state.bill_items = []
if 'bill_friends' not in st.session_state or not isinstance(st.session_state.bill_friends, list):
    st.session_state.bill_friends = []

# Main title
st.title("🧾 Restaurant Bill Splitter")
st.markdown("Split restaurant bills easily among friends")

# Two-column layout
col1, col2 = st.columns([1, 1])

# Left Column: Input Section
with col1:
    st.subheader("📝 Input Details")
    
    # Restaurant name input
    restaurant_name = st.text_input("Restaurant Name", placeholder="Enter restaurant name...")
    
    # Menu item form
    st.markdown("**Add Menu Items**")
    with st.form("add_item_form"):
        item_name = st.text_input("Item Name", placeholder="e.g., Caesar Salad")
        item_category = st.selectbox("Category", ["Starter", "Main", "Dessert", "Drink", "Other"])
        item_cost = st.number_input("Cost ($)", min_value=0.01, step=0.01, format="%.2f")
        
        submitted_item = st.form_submit_button("Add Item", type="primary")
        
        if submitted_item:
            if item_name.strip():
                new_item = {
                    "name": item_name.strip(),
                    "category": item_category,
                    "cost": float(item_cost),
                    "ordered_by": []
                }
                st.session_state.bill_items.append(new_item)
                st.success(f"Added {item_name} (${item_cost:.2f})")
                st.rerun()
            else:
                st.error("Please enter a valid item name")
    
    # Display current items
    if st.session_state.bill_items:
        st.markdown("**Current Items:**")
        # Ensure items is a list before iterating
        if isinstance(st.session_state.bill_items, list):
            for i, item in enumerate(st.session_state.bill_items):
                st.write(f"{i+1}. {item['name']} ({item['category']}) - ${item['cost']:.2f}")
        else:
            # Reset if corrupted
            st.session_state.bill_items = []
            st.error("Session state was corrupted. Please refresh the page.")
    
    st.divider()
    
    # Friends form
    st.markdown("**Add Friends**")
    with st.form("add_friend_form"):
        friend_name = st.text_input("Friend Name", placeholder="e.g., John")
        
        submitted_friend = st.form_submit_button("Add Friend", type="primary")
        
        if submitted_friend:
            if friend_name.strip():
                friend_name_clean = friend_name.strip()
                # Check for duplicates (case-insensitive)
                if friend_name_clean.lower() not in [f.lower() for f in st.session_state.bill_friends]:
                    st.session_state.bill_friends.append(friend_name_clean)
                    st.success(f"Added {friend_name_clean}")
                    st.rerun()
                else:
                    st.error("This friend is already added")
            else:
                st.error("Please enter a valid friend name")
    
    # Display current friends
    if st.session_state.bill_friends:
        st.markdown("**Current Friends:**")
        # Ensure friends is a list before iterating
        if isinstance(st.session_state.bill_friends, list):
            for i, friend in enumerate(st.session_state.bill_friends):
                st.write(f"{i+1}. {friend}")
        else:
            # Reset if corrupted
            st.session_state.bill_friends = []
            st.error("Session state was corrupted. Please refresh the page.")

# Right Column: Assignment Section
with col2:
    st.subheader("🎯 Assign Items")
    
    # Placeholder for item display and assignment (Step 3)
    st.markdown("*Item assignments will appear here after adding items and friends*")
    st.empty()

# Actions & Results Section
st.divider()
st.subheader("💰 Calculate & Export")

# Placeholder for calculate button (Step 4)
st.markdown("**Calculate Button** *(Coming in Step 4)*")
st.empty()

# Placeholder for results display (Step 4)
st.markdown("**Results Display** *(Coming in Step 4)*")
st.empty()

# Placeholder for export functionality (Step 5)
st.markdown("**XLSX Export** *(Coming in Step 5)*")
st.empty()

# Placeholder for reset functionality (Step 6)
st.markdown("**Reset Session** *(Coming in Step 6)*")
st.empty()