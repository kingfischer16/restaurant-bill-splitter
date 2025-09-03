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

# Two-column layout
col1, col2 = st.columns([1, 1])

# Left Column: Input Section
with col1:
    st.subheader("📝 Input Details")
    
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
                   f"• 1 course: ${restaurant_data['course_pricing']['1_course']:.2f}\n"
                   f"• 2 courses: ${restaurant_data['course_pricing']['2_course']:.2f}\n"
                   f"• 3 courses: ${restaurant_data['course_pricing']['3_course']:.2f}\n\n"
                   "*Some items may have additional surcharges*")
    
    # Menu item form (only for custom restaurants or adding to pre-configured)
    if selected_restaurant == "Custom Restaurant":
        st.markdown("**Add Menu Items**")
        form_disabled = False
    else:
        st.markdown("**Add Extra Items** *(optional)*")
        form_disabled = False
    
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
    
    # Category order for sorting
    category_order = ["Starter", "Main", "Dessert", "Drink", "Other"]
    
    # Check if we have both items and friends to assign
    if st.session_state.bill_items and st.session_state.bill_friends:
        st.markdown("*Select items for each friend*")
        
        # Display each friend with their assignment options
        for friend_idx, friend in enumerate(st.session_state.bill_friends):
            with st.container():
                st.markdown(f"### 👤 {friend}")
                
                # Get current items assigned to this friend (including duplicates)
                current_items = []
                for item in st.session_state.bill_items:
                    base_item_name = item['name']
                    friend_count = item['ordered_by'].count(friend)
                    
                    # Add items based on how many times friend ordered them
                    for i in range(friend_count):
                        if i == 0:
                            current_items.append(base_item_name)
                        else:
                            # Add with ordinal suffix for duplicates
                            ordinal_num = i + 1
                            if 10 <= ordinal_num % 100 <= 20:
                                suffix = 'th'
                            else:
                                suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(ordinal_num % 10, 'th')
                            current_items.append(f"{base_item_name} ({ordinal_num}{suffix})")
                
                # Helper function for ordinal numbers
                def ordinal(n):
                    if 10 <= n % 100 <= 20:
                        suffix = 'th'
                    else:
                        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
                    return f"{n}{suffix}"
                
                # Build options list with duplicates for drinks and other items
                options_list = []
                for item in st.session_state.bill_items:
                    base_name = item['name']
                    category = item['category']
                    
                    # Always add the base item
                    options_list.append(base_name)
                    
                    # Add duplicate options for Drink and Other categories only
                    if category in ['Drink', 'Other']:
                        # Add up to 5 additional copies (could be made configurable)
                        for i in range(2, 7):  # 2nd, 3rd, 4th, 5th, 6th
                            duplicate_name = f"{base_name} ({ordinal(i)})"
                            options_list.append(duplicate_name)
                
                # Multiselect for this friend's items
                selected_items = st.multiselect(
                    f"Items for {friend}:",
                    options=options_list,
                    default=current_items,
                    key=f"friend_items_{friend_idx}",
                    help=f"Select all items that {friend} ordered. Drinks/Other items can be selected multiple times."
                )
                
                # Helper function to extract base item name from possibly duplicated name
                def get_base_item_name(selected_name):
                    # Check if it's a duplicate (contains " (2nd)", " (3rd)", etc.)
                    if " (" in selected_name and selected_name.endswith(")"):
                        # Extract base name before the ordinal suffix
                        return selected_name.split(" (")[0]
                    return selected_name
                
                # Update the bill_items ordered_by lists based on friend's selections
                for item in st.session_state.bill_items:
                    base_item_name = item['name']
                    
                    # Count how many times this friend selected this item (including duplicates)
                    friend_selections = [s for s in selected_items if get_base_item_name(s) == base_item_name]
                    
                    if friend_selections:
                        # Add friend to this item's ordered_by list for each selection
                        # Clear existing entries for this friend first
                        item['ordered_by'] = [f for f in item['ordered_by'] if f != friend]
                        
                        # Add friend once for each selection
                        for _ in friend_selections:
                            item['ordered_by'].append(friend)
                    else:
                        # Remove friend from this item if they didn't select it
                        item['ordered_by'] = [f for f in item['ordered_by'] if f != friend]
                
                # Build friend's items list with quantities
                friend_items_with_qty = {}
                for item in st.session_state.bill_items:
                    base_item_name = item['name']
                    friend_count = item['ordered_by'].count(friend)
                    
                    if friend_count > 0:
                        friend_items_with_qty[base_item_name] = {
                            'item': item,
                            'quantity': friend_count
                        }
                
                # Sort items by category order, then by name
                sorted_items = sorted(friend_items_with_qty.items(), 
                                    key=lambda x: (category_order.index(x[1]['item']['category']) 
                                                 if x[1]['item']['category'] in category_order 
                                                 else len(category_order), x[0]))
                
                # Calculate total based on restaurant pricing model
                friend_total = 0.0
                if friend_items_with_qty:
                    st.markdown("**Items ordered:**")
                    
                    # Check if this is a course-based restaurant
                    selected_restaurant_name = selected_restaurant.split(" (")[0] if selected_restaurant != "Custom Restaurant" else None
                    restaurant_data = next((r for r in restaurants_data['restaurants'] if r['name'] == selected_restaurant_name), None)
                    
                    if restaurant_data and restaurant_data.get('pricing_model') == 'course_based':
                        # Course-based pricing calculation
                        course_count = 0
                        surcharge_total = 0.0
                        non_course_total = 0.0
                        
                        course_categories = set()
                        
                        for item_name, item_data in sorted_items:
                            item = item_data['item']
                            quantity = item_data['quantity']
                            
                            # Check if item is a course item
                            menu_item_data = next((m for m in restaurant_data['menu'] if m['name'] == item['name']), None)
                            is_course_item = menu_item_data.get('is_course_item', False) if menu_item_data else False
                            
                            if is_course_item and item['category'] in ['Starter', 'Main', 'Dessert']:
                                # Count unique course categories (only once per category)
                                course_categories.add(item['category'])
                                # Add surcharge (multiplied by quantity)
                                surcharge_total += item['cost'] * quantity
                                if quantity > 1:
                                    st.write(f"• {item['name']} ({item['category']}) x{quantity} - Course item +${item['cost']:.2f} each = +${item['cost'] * quantity:.2f} surcharge")
                                else:
                                    st.write(f"• {item['name']} ({item['category']}) - Course item +${item['cost']:.2f} surcharge")
                            else:
                                # Non-course item - full price multiplied by quantity
                                item_total = item['cost'] * quantity
                                non_course_total += item_total
                                if quantity > 1:
                                    st.write(f"• {item['name']} ({item['category']}) x{quantity} - ${item['cost']:.2f} each = ${item_total:.2f}")
                                else:
                                    st.write(f"• {item['name']} ({item['category']}) - ${item['cost']:.2f}")
                        
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
                            
                            st.markdown(f"**Course Pricing Breakdown:**")
                            st.write(f"• {course_count}-course base price: ${base_course_price:.2f}")
                            if surcharge_total > 0:
                                st.write(f"• Premium item surcharges: ${surcharge_total:.2f}")
                            if non_course_total > 0:
                                st.write(f"• Additional items (drinks, etc.): ${non_course_total:.2f}")
                            
                            friend_total = base_course_price + surcharge_total + non_course_total
                        else:
                            # Only non-course items
                            friend_total = non_course_total
                    else:
                        # Regular item-based pricing
                        for item_name, item_data in sorted_items:
                            item = item_data['item']
                            quantity = item_data['quantity']
                            item_total = item['cost'] * quantity
                            friend_total += item_total
                            
                            if quantity > 1:
                                st.write(f"• {item['name']} ({item['category']}) x{quantity} - ${item['cost']:.2f} each = ${item_total:.2f}")
                            else:
                                st.write(f"• {item['name']} ({item['category']}) - ${item['cost']:.2f}")
                    
                    # Show total
                    st.markdown(f"**Total: ${friend_total:.2f}**")
                else:
                    st.write("*No items assigned yet*")
                
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