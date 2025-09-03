import streamlit as st
import json
import os

# Page configuration
st.set_page_config(
    page_title="Restaurant Bill Splitter",
    page_icon="🧾",
    layout="wide"
)

# Load restaurants data
@st.cache_data
def load_restaurants():
    try:
        with open('restaurants.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("restaurants.json file not found")
        return {"restaurants": []}
    except json.JSONDecodeError:
        st.error("Invalid JSON format in restaurants.json")
        return {"restaurants": []}

restaurants_data = load_restaurants()

# Initialize session state
if 'bill_items' not in st.session_state or not isinstance(st.session_state.bill_items, list):
    st.session_state.bill_items = []
if 'bill_friends' not in st.session_state or not isinstance(st.session_state.bill_friends, list):
    st.session_state.bill_friends = []
if 'selected_restaurant' not in st.session_state:
    st.session_state.selected_restaurant = "Custom Restaurant"

# Main title
st.title("🧾 Restaurant Bill Splitter")
st.markdown("Split restaurant bills easily among friends")

# Single column layout - mobile first
st.markdown("---")
st.subheader("🏪 Restaurant Setup")

# Restaurant selection
restaurant_options = ["Custom Restaurant"] + [f"{r['name']} ({r['cuisine']})" for r in restaurants_data['restaurants']]

selected_restaurant = st.selectbox(
    "Select Restaurant:",
    options=restaurant_options,
    index=restaurant_options.index(st.session_state.selected_restaurant) if st.session_state.selected_restaurant in restaurant_options else 0,
    key="restaurant_selector"
)
    
    # Update session state and handle restaurant changes
if selected_restaurant != st.session_state.selected_restaurant:
    st.session_state.selected_restaurant = selected_restaurant
    
        # If switching to a pre-configured restaurant, load its menu
    if selected_restaurant != "Custom Restaurant":
        restaurant_name_only = selected_restaurant.split(" (")[0]
        selected_restaurant_data = next((r for r in restaurants_data['restaurants'] if r['name'] == restaurant_name_only), None)
        
        if selected_restaurant_data:
                # Clear current items and load pre-configured menu
            st.session_state.bill_items = []
            for menu_item in selected_restaurant_data['menu']:
                st.session_state.bill_items.append({
                    "name": menu_item['name'],
                    "category": menu_item['category'],
                    "cost": float(menu_item['price']),
                    "ordered_by": [],
                    "is_course_item": menu_item.get('is_course_item', False)
                })
            st.rerun()
    else:
            # Clear items when switching to custom restaurant
        st.session_state.bill_items = []
        st.rerun()

    # Restaurant name input (auto-populated or manual)
if selected_restaurant == "Custom Restaurant":
    restaurant_name = st.text_input("Restaurant Name", placeholder="Enter restaurant name...")
else:
    restaurant_name_only = selected_restaurant.split(" (")[0]
    restaurant_name = st.text_input("Restaurant Name", value=restaurant_name_only, disabled=True)
    
        # Show course pricing info for course-based restaurants
    restaurant_data = next((r for r in restaurants_data['restaurants'] if r['name'] == restaurant_name_only), None)
    if restaurant_data and restaurant_data.get('pricing_model') == 'course_based':
        st.info("📋 **Course-based pricing:**\n"
               f"• 1 course: {restaurant_data['course_pricing']['1_course']:.2f} kr\n"
               f"• 2 courses: {restaurant_data['course_pricing']['2_course']:.2f} kr\n"
               f"• 3 courses: {restaurant_data['course_pricing']['3_course']:.2f} kr\n\n"
               "*Some items may have additional surcharges*")

    # Menu item form (only for custom restaurants or adding to pre-configured)
if selected_restaurant == "Custom Restaurant":
    st.markdown("**Add Menu Items**")
else:
    st.markdown("**Add Extra Items** *(optional)*")

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
                "ordered_by": [],
                "is_course_item": False  # Custom added items are not course items
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

st.markdown("---")
st.subheader("👥 Add Friends")

# Initialize friend input value in session state if it doesn't exist
if 'friend_name_value' not in st.session_state:
    st.session_state.friend_name_value = ""

# Simple friend input - mobile-first, no columns
friend_name = st.text_input(
    "Friend Name", 
    value=st.session_state.friend_name_value,
    placeholder="e.g., John", 
    key="friend_name_input"
)

if st.button("Add Friend", type="primary"):
    if friend_name.strip():
        friend_name_clean = friend_name.strip()
        # Check for duplicates (case-insensitive)
        if friend_name_clean.lower() not in [f.lower() for f in st.session_state.bill_friends]:
            st.session_state.bill_friends.append(friend_name_clean)
            # Clear the input field by resetting the session state value
            st.session_state.friend_name_value = ""
            st.success(f"Added {friend_name_clean}")
            st.rerun()
        else:
            st.error("This friend is already added")
    else:
        st.error("Please enter a valid friend name")

# Sync the session state value with the current input
st.session_state.friend_name_value = friend_name

# Display current friends
if st.session_state.bill_friends:
    st.markdown("**Current Friends:**")
    for i, friend in enumerate(st.session_state.bill_friends):
        st.write(f"{i+1}. {friend}")

st.markdown("---")
st.subheader("🍽️ Friend Orders")

# Helper functions for assignment logic


def get_friend_item_quantities(friend, bill_items):
    """Get current quantities for each item for a friend"""
    quantities = {}
    for item in bill_items:
        quantities[item['name']] = item['ordered_by'].count(friend)
    return quantities

def update_item_assignments_with_quantities(friend, item_quantities, bill_items):
    """Update bill_items ordered_by lists based on friend's item quantities"""
    for item in bill_items:
        item_name = item['name']
        desired_quantity = item_quantities.get(item_name, 0)
        
        # Remove all existing entries for this friend
        item['ordered_by'] = [f for f in item['ordered_by'] if f != friend]
        
        # Add friend back for the specified quantity
        for _ in range(desired_quantity):
            item['ordered_by'].append(friend)

def calculate_friend_total(friend, bill_items, selected_restaurant, restaurants_data, category_order):
    """Calculate total cost for a friend based on restaurant pricing model"""
    # Build friend's items list with quantities
    friend_items_with_qty = {}
    for item in bill_items:
        base_item_name = item['name']
        friend_count = item['ordered_by'].count(friend)
        
        if friend_count > 0:
            friend_items_with_qty[base_item_name] = {
                'item': item,
                'quantity': friend_count
            }
    
    if not friend_items_with_qty:
        return 0.0, []
    
    # Sort items by category order
    sorted_items = sorted(friend_items_with_qty.items(), 
                         key=lambda x: (category_order.index(x[1]['item']['category']) 
                                      if x[1]['item']['category'] in category_order 
                                      else len(category_order), x[0]))
    
    # Check if this is a course-based restaurant
    selected_restaurant_name = selected_restaurant.split(" (")[0] if selected_restaurant != "Custom Restaurant" else None
    restaurant_data = next((r for r in restaurants_data['restaurants'] if r['name'] == selected_restaurant_name), None)
    
    friend_total = 0.0
    item_displays = []
    
    if restaurant_data and restaurant_data.get('pricing_model') == 'course_based':
        # Course-based pricing calculation
        course_categories = set()
        surcharge_total = 0.0
        non_course_total = 0.0
        
        for item_name, item_data in sorted_items:
            item = item_data['item']
            quantity = item_data['quantity']
            
            menu_item_data = next((m for m in restaurant_data['menu'] if m['name'] == item['name']), None)
            is_course_item = menu_item_data.get('is_course_item', False) if menu_item_data else False
            
            if is_course_item and item['category'] in ['Starter', 'Main', 'Dessert']:
                course_categories.add(item['category'])
                surcharge_total += item['cost'] * quantity
                if quantity > 1:
                    item_displays.append(f"• {item['name']} ({item['category']}) x{quantity} - Course item +${item['cost']:.2f} each = +${item['cost'] * quantity:.2f} surcharge")
                else:
                    item_displays.append(f"• {item['name']} ({item['category']}) - Course item +${item['cost']:.2f} surcharge")
            else:
                item_total = item['cost'] * quantity
                non_course_total += item_total
                if quantity > 1:
                    item_displays.append(f"• {item['name']} ({item['category']}) x{quantity} - ${item['cost']:.2f} each = ${item_total:.2f}")
                else:
                    item_displays.append(f"• {item['name']} ({item['category']}) - ${item['cost']:.2f}")
        
        # Calculate course base price
        course_count = len(course_categories)
        if course_count > 0:
            course_pricing = restaurant_data.get('course_pricing', {})
            if course_count == 1:
                base_course_price = course_pricing.get('1_course', 0)
            elif course_count == 2:
                base_course_price = course_pricing.get('2_course', 0)
            else:
                base_course_price = course_pricing.get('3_course', 0)
            
            item_displays.append("**Course Pricing Breakdown:**")
            item_displays.append(f"• {course_count}-course base price: ${base_course_price:.2f}")
            if surcharge_total > 0:
                item_displays.append(f"• Premium item surcharges: ${surcharge_total:.2f}")
            if non_course_total > 0:
                item_displays.append(f"• Additional items (drinks, etc.): ${non_course_total:.2f}")
            
            friend_total = base_course_price + surcharge_total + non_course_total
        else:
            friend_total = non_course_total
    else:
        # Regular item-based pricing
        for item_name, item_data in sorted_items:
            item = item_data['item']
            quantity = item_data['quantity']
            item_total = item['cost'] * quantity
            friend_total += item_total
            
            if quantity > 1:
                item_displays.append(f"• {item['name']} ({item['category']}) x{quantity} - ${item['cost']:.2f} each = ${item_total:.2f}")
            else:
                item_displays.append(f"• {item['name']} ({item['category']}) - ${item['cost']:.2f}")
    
    return friend_total, item_displays

# Category order for sorting
category_order = ["Starter", "Main", "Dessert", "Drink", "Other"]

# Check if we have both items and friends to assign
if st.session_state.bill_items and st.session_state.bill_friends:
    # Display each friend with their assignment options
    for friend_idx, friend in enumerate(st.session_state.bill_friends):
        with st.container():
            st.markdown(f"### 👤 {friend}")
            
            # Get current quantities for this friend
            current_quantities = get_friend_item_quantities(friend, st.session_state.bill_items)
            item_quantities = {}
            
            # Step 1: Item selection from available items
            available_items = []
            for item in st.session_state.bill_items:
                if current_quantities.get(item['name'], 0) == 0:  # Not yet selected
                    available_items.append(f"{item['name']} ({item['category']}) - ${item['cost']:.2f}")
            
            if available_items:
                st.markdown("**Add items:**")
                selected_new_item = st.selectbox(
                    "Select an item to add:",
                    options=[""] + available_items,
                    key=f"add_item_{friend}_{friend_idx}",
                    help="Choose an item to add to this friend's order"
                )
                
                if selected_new_item and st.button(f"Add Item", key=f"add_btn_{friend}_{friend_idx}"):
                    # Extract item name from the display string
                    item_name = selected_new_item.split(" (")[0]
                    # Find the item in bill_items
                    for item in st.session_state.bill_items:
                        if item['name'] == item_name:
                            # Add one quantity for this friend
                            item['ordered_by'].append(friend)
                            st.rerun()
                            break
            
            # Step 2: Show selected items with quantity controls
            selected_items = []
            for item in st.session_state.bill_items:
                current_qty = current_quantities.get(item['name'], 0)
                if current_qty > 0:
                    selected_items.append((item, current_qty))
            
            if selected_items:
                st.markdown("**Your items:**")
                
                for item, current_qty in selected_items:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"{item['name']} - ${item['cost']:.2f} each")
                    
                    with col2:
                        # Set max quantity based on category
                        if item['category'] in ['Starter', 'Main', 'Dessert']:
                            max_qty = 1
                        else:
                            max_qty = 10
                        
                        # Quantity input
                        new_qty = st.number_input(
                            "Qty",
                            min_value=0,
                            max_value=max_qty,
                            value=current_qty,
                            step=1,
                            key=f"qty_{friend}_{item['name']}_{friend_idx}",
                            label_visibility="collapsed"
                        )
                        item_quantities[item['name']] = new_qty
                    
                    with col3:
                        # Remove button - removes item entirely regardless of quantity
                        if st.button("❌", key=f"remove_{friend}_{item['name']}_{friend_idx}", help="Remove item"):
                            # Remove all instances of this friend from this item
                            for bill_item in st.session_state.bill_items:
                                if bill_item['name'] == item['name']:
                                    bill_item['ordered_by'] = [f for f in bill_item['ordered_by'] if f != friend]
                                    break
                            st.rerun()
            
            # Apply all quantity changes
            for item_name, qty in item_quantities.items():
                if qty != current_quantities.get(item_name, 0):
                    # Update the assignments
                    for item in st.session_state.bill_items:
                        if item['name'] == item_name:
                            # Remove all existing entries for this friend
                            item['ordered_by'] = [f for f in item['ordered_by'] if f != friend]
                            # Add friend back for the specified quantity
                            for _ in range(qty):
                                item['ordered_by'].append(friend)
                            break
            
            # Calculate and display total
            friend_total, item_displays = calculate_friend_total(
                friend, st.session_state.bill_items, selected_restaurant, 
                restaurants_data, category_order
            )
            
            if friend_total > 0:
                st.markdown(f"**Total: ${friend_total:.2f}**")
            else:
                st.write("*No items selected*")
            
            st.divider()

elif not st.session_state.bill_items:
    st.info("📝 Add some menu items first to assign them to friends")
    
elif not st.session_state.bill_friends:
    st.info("👥 Add some friends first to assign items to them")
    
else:
    st.info("🔄 Add items and friends to start assigning")

# Actions & Results Section
st.divider()
st.subheader("💰 Calculate & Export")

# TODO: Implement remaining features
st.info("🚧 **Coming Soon:**\n"
       "• Calculate Bill Split button\n"
       "• Results Display\n" 
       "• XLSX Export\n"
       "• Reset Session")
