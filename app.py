import streamlit as st
import json
import os
import uuid
from datetime import datetime
import streamlit.components.v1 as components

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

# Party management functions
def generate_party_id():
    """Generate a unique party ID"""
    return str(uuid.uuid4())

def get_current_party_data():
    """Get current party data from session state"""
    if not st.session_state.get('current_party_id'):
        return None
    
    party_data = {
        'id': st.session_state.current_party_id,
        'name': st.session_state.get('party_name', 'Untitled Party'),
        'restaurant_name': st.session_state.get('restaurant_name', ''),
        'selected_restaurant': st.session_state.get('selected_restaurant', 'Custom Restaurant'),
        'created': st.session_state.get('party_created', datetime.now().isoformat()),
        'last_updated': datetime.now().isoformat(),
        'friends': st.session_state.get('bill_friends', []),
        'items': st.session_state.get('bill_items', []),
        'total_cost': calculate_total_cost()
    }
    return party_data

def calculate_total_cost():
    """Calculate total cost for current party"""
    total = 0.0
    for item in st.session_state.get('bill_items', []):
        total += item['cost'] * len(item.get('ordered_by', []))
    return total

def save_current_party():
    """Save current party to localStorage"""
    if not st.session_state.get('current_party_id'):
        st.error("No party ID found - cannot save")
        return
    
    party_data = get_current_party_data()
    if not party_data:
        st.error("No party data found - cannot save")
        return
    
    party_id = party_data['id']
    party_name = party_data['name']
    
    # Debug: Show what we're trying to save
    st.write(f"🔍 **Debug Info:**")
    st.write(f"- Party ID: {party_id}")
    st.write(f"- Party Name: {party_name}")
    st.write(f"- Friends: {len(party_data.get('friends', []))}")
    st.write(f"- Items: {len(party_data.get('items', []))}")
    st.write(f"- Total Cost: ${party_data.get('total_cost', 0.0):.2f}")
    
    # Use base64 encoding to avoid JavaScript string escaping issues
    import base64
    import json
    
    json_data = json.dumps(party_data)
    encoded_data = base64.b64encode(json_data.encode('utf-8')).decode('ascii')
    
    components.html(f"""
    <script>
        try {{
            // Decode the base64 data
            const encodedData = '{encoded_data}';
            const jsonData = atob(encodedData);
            const partyData = JSON.parse(jsonData);
            
            // Get existing parties
            let parties = JSON.parse(localStorage.getItem('restaurant_bill_splitter_parties') || '{{}}');
            
            // Log before save
            console.log('Saving party:', partyData.name);
            console.log('Current parties count:', Object.keys(parties).length);
            
            // Update this party
            parties['{party_id}'] = partyData;
            
            // Save back to localStorage
            localStorage.setItem('restaurant_bill_splitter_parties', JSON.stringify(parties));
            localStorage.setItem('restaurant_bill_splitter_current_party', '{party_id}');
            
            // Log after save
            console.log('Updated parties count:', Object.keys(parties).length);
            console.log('Successfully saved party:', partyData.name);
            
            // Show success alert
            alert('Party "' + partyData.name + '" saved successfully!');
            
        }} catch(e) {{
            console.error('Failed to save party to localStorage:', e);
            console.error('Encoded data was:', '{encoded_data}');
            alert('Save failed: ' + e.message);
        }}
    </script>
    """, height=0)

def load_parties_interface():
    """Simple party loading interface"""
    
    if st.button("📋 Load Saved Party", type="secondary"):
        st.session_state.loading_parties = True
        st.rerun()
    
    # Show party loading and selection if requested
    if st.session_state.get('loading_parties', False):
        st.info("🔍 Checking localStorage for saved parties...")
        
        st.info("⚠️ **Party Loading Feature Temporarily Disabled**")
        st.markdown("""
        The party loading feature is currently experiencing technical issues with Streamlit's iframe security model.
        
        **Current Workaround:**
        1. Use the '🔍 Debug: Check localStorage' button below to see your saved parties
        2. Manually copy party data if needed
        3. This will be fixed in a future update
        
        **What works:**
        - ✅ Creating new parties
        - ✅ Saving parties (localStorage)  
        - ✅ All bill calculation features
        - ✅ Party data persists across browser sessions
        """)


def load_party_from_url():
    """Load party data from URL parameter"""
    query_params = st.query_params
    
    # Handle simple message display
    if 'message' in query_params:
        message = query_params['message']
        st.session_state.loading_parties = False  # Clear loading state
        
        if message == 'no_parties':
            st.warning("❌ No saved parties found")
        elif message == 'error':
            st.error("❌ Error loading saved parties")
        
        st.query_params.clear()
        st.rerun()
    
    # Handle new simplified party loading
    elif 'load_parties' in query_params:
        try:
            import urllib.parse
            encoded_data = query_params['load_parties']
            json_data = urllib.parse.unquote(encoded_data)
            parties_data = json.loads(json_data)
            
            # Store parties in session state
            st.session_state.available_parties = parties_data
            st.session_state.loading_parties = False     # Clear loading state
            st.session_state.show_parties_list = True    # Show the party list
            
            # Clear the query parameter
            st.query_params.clear()
            st.rerun()
            
        except Exception as e:
            st.error(f"Failed to load parties list: {e}")
            st.session_state.loading_parties = False
            st.query_params.clear()
            st.rerun()
    
    # Handle party list loading (legacy)
    elif 'parties_list' in query_params:
        try:
            import urllib.parse
            encoded_data = query_params['parties_list']
            json_data = urllib.parse.unquote(encoded_data)
            parties_data = json.loads(json_data)
            
            # Store parties in session state
            st.session_state.available_parties = parties_data
            st.session_state.loading_parties = False     # Clear loading state
            st.session_state.show_parties_list = True    # Show the party list
            
            # Clear the query parameter
            st.query_params.clear()
            st.rerun()
            
        except Exception as e:
            st.error(f"Failed to load parties list: {e}")
            st.session_state.loading_parties = False
            st.query_params.clear()
            st.rerun()
    
    # Handle empty parties status
    elif 'parties_status' in query_params:
        status = query_params['parties_status']
        st.session_state.loading_parties = False  # Clear loading state
        
        if status == 'empty':
            st.warning("❌ No saved parties found")
        elif status == 'error':
            st.error("❌ Error loading saved parties")
        
        st.query_params.clear()
        st.rerun()
    
    # Handle individual party loading
    elif 'load_party' in query_params:
        try:
            import urllib.parse
            encoded_data = query_params['load_party']
            json_data = urllib.parse.unquote(encoded_data)
            party_data = json.loads(json_data)
            
            # Load party data into session state
            st.session_state.current_party_id = party_data['id']
            st.session_state.party_name = party_data['name']
            st.session_state.restaurant_name = party_data.get('restaurant_name', '')
            st.session_state.selected_restaurant = party_data.get('selected_restaurant', 'Custom Restaurant')
            st.session_state.party_created = party_data.get('created', datetime.now().isoformat())
            st.session_state.bill_friends = party_data.get('friends', [])
            st.session_state.bill_items = party_data.get('items', [])
            
            # Clear party selection state
            st.session_state.show_parties_list = False
            st.session_state.available_parties = {}
            
            # Clear the query parameter
            st.query_params.clear()
            st.rerun()
            
        except Exception as e:
            st.error(f"Failed to load party: {e}")
            st.query_params.clear()
            st.rerun()

def show_parties_list():
    """Show native Streamlit party selection interface"""
    if not st.session_state.get('show_parties_list', False):
        return
    
    st.markdown("---")
    st.subheader("📋 Select a Party to Load")
    
    parties = st.session_state.get('available_parties', {})
    
    for party_id, party in parties.items():
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{party.get('name', 'Untitled Party')}**")
                
                # Party details
                try:
                    created_date = datetime.fromisoformat(party.get('created', '')).strftime('%Y-%m-%d')
                except:
                    created_date = 'Unknown date'
                
                friend_count = len(party.get('friends', []))
                total_cost = party.get('total_cost', 0.0)
                restaurant = party.get('restaurant_name', 'Custom Restaurant')
                
                st.write(f"📅 {created_date} | 👥 {friend_count} friends | 💰 ${total_cost:.2f}")
                st.write(f"🏪 {restaurant}")
            
            with col2:
                if st.button("Load", key=f"load_{party_id}", type="primary"):
                    # Load this party directly into session state
                    st.session_state.current_party_id = party['id']
                    st.session_state.party_name = party.get('name', 'Untitled Party')
                    st.session_state.restaurant_name = party.get('restaurant_name', '')
                    st.session_state.selected_restaurant = party.get('selected_restaurant', 'Custom Restaurant')
                    st.session_state.party_created = party.get('created', datetime.now().isoformat())
                    st.session_state.bill_friends = party.get('friends', [])
                    st.session_state.bill_items = party.get('items', [])
                    
                    # Hide party selector
                    st.session_state.show_parties_list = False
                    st.session_state.available_parties = {}
                    
                    st.success(f"Loaded party: {party.get('name', 'Untitled Party')}")
                    st.rerun()
            
            with col3:
                if st.button("Delete", key=f"delete_{party_id}", type="secondary"):
                    # Use JavaScript to delete from localStorage
                    components.html(f"""
                    <script>
                        if (confirm('Are you sure you want to delete "{party.get('name', 'Untitled Party')}"?')) {{
                            try {{
                                let parties = JSON.parse(localStorage.getItem('restaurant_bill_splitter_parties') || '{{}}');
                                delete parties['{party_id}'];
                                localStorage.setItem('restaurant_bill_splitter_parties', JSON.stringify(parties));
                                
                                const currentParty = localStorage.getItem('restaurant_bill_splitter_current_party');
                                if (currentParty === '{party_id}') {{
                                    localStorage.removeItem('restaurant_bill_splitter_current_party');
                                }}
                                
                                alert('Party deleted successfully');
                                window.parent.location.reload();
                            }} catch(e) {{
                                alert('Failed to delete party: ' + e.message);
                            }}
                        }}
                    </script>
                    """, height=0)
            
            st.divider()
    
    # Cancel button
    if st.button("❌ Cancel", type="secondary"):
        st.session_state.show_parties_list = False
        st.session_state.available_parties = {}
        st.rerun()

def create_new_party(party_name):
    """Create a new party and set it as current"""
    party_id = generate_party_id()
    
    # Initialize new party session state
    st.session_state.current_party_id = party_id
    st.session_state.party_name = party_name
    st.session_state.restaurant_name = ''
    st.session_state.selected_restaurant = 'Custom Restaurant'
    st.session_state.party_created = datetime.now().isoformat()
    st.session_state.bill_friends = []
    st.session_state.bill_items = []
    
    # Note: Don't auto-save here - let user manually save when ready
    # This avoids issues with incomplete session state during initialization
    
    return party_id

def display_bill_results():
    """Display comprehensive bill split results for all friends"""
    if not st.session_state.get('show_bill_results', False):
        return
    
    st.markdown("---")
    st.subheader("🧾 Bill Split Results")
    
    if not st.session_state.bill_friends or not st.session_state.bill_items:
        st.warning("⚠️ Add friends and items first to calculate the bill split")
        return
    
    # Category ordering
    category_order = ['Starter', 'Main', 'Dessert', 'Drink', 'Other']
    selected_restaurant = st.session_state.get('selected_restaurant', 'Custom Restaurant')
    grand_total = 0.0
    
    # Calculate results for each friend
    friend_results = []
    for friend in st.session_state.bill_friends:
        friend_total, item_displays = calculate_friend_total(
            friend, st.session_state.bill_items, selected_restaurant, 
            restaurants_data, category_order
        )
        grand_total += friend_total
        friend_results.append({
            'name': friend,
            'total': friend_total,
            'items': item_displays
        })
    
    # Sort friends by total (descending)
    friend_results.sort(key=lambda x: x['total'], reverse=True)
    
    # Summary section
    st.markdown("### 💰 Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Friends", len(st.session_state.bill_friends))
    with col2:
        st.metric("Total Items", len(st.session_state.bill_items))
    with col3:
        st.metric("Grand Total", f"${grand_total:.2f}")
    
    # Detailed breakdown per friend
    st.markdown("### 👥 Individual Breakdown")
    
    for friend_data in friend_results:
        friend = friend_data['name']
        total = friend_data['total']
        items = friend_data['items']
        
        with st.expander(f"**{friend}** - ${total:.2f}", expanded=True):
            if items:
                for category_name, category_items in items:
                    if category_items:
                        st.markdown(f"**{category_name}:**")
                        for item_info in category_items:
                            st.markdown(f"• {item_info}")
                        st.markdown("")  # Add spacing
            else:
                st.write("*No items ordered*")
    
    # Close results button
    if st.button("❌ Close Results", type="secondary"):
        st.session_state.show_bill_results = False
        st.rerun()

# Initialize session state
if 'bill_items' not in st.session_state or not isinstance(st.session_state.bill_items, list):
    st.session_state.bill_items = []
if 'bill_friends' not in st.session_state or not isinstance(st.session_state.bill_friends, list):
    st.session_state.bill_friends = []
if 'selected_restaurant' not in st.session_state:
    st.session_state.selected_restaurant = "Custom Restaurant"

# Party-specific session state
if 'current_party_id' not in st.session_state:
    st.session_state.current_party_id = None
if 'party_name' not in st.session_state:
    st.session_state.party_name = ''


# Try to load party from URL parameter
load_party_from_url()

# Main title
st.title("🧾 Restaurant Bill Splitter")

# Party Management Section
st.markdown("---")
st.subheader("🎉 Party Management")

# Current party info or party creation
if st.session_state.current_party_id:
    # Show current party info
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"**Current Party:** {st.session_state.party_name}")
        party_created = st.session_state.get('party_created', '')
        if party_created:
            try:
                created_date = datetime.fromisoformat(party_created).strftime("%Y-%m-%d")
                st.markdown(f"*Created: {created_date}*")
            except:
                pass
    
    with col2:
        friend_count = len(st.session_state.bill_friends)
        item_count = len(st.session_state.bill_items)
        st.metric("Friends", friend_count)
    
    with col3:
        total_cost = calculate_total_cost()
        st.metric("Total", f"${total_cost:.2f}")
        
    # Party actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾 Save Party", type="primary"):
            save_current_party()
            st.success("Party saved!")
            
    with col2:
        if st.button("📋 Load Different Party", type="secondary"):
            st.session_state.show_party_selector = True
            st.rerun()
    
    with col3:
        if st.button("🆕 New Party", type="secondary"):
            st.session_state.show_new_party_form = True
            st.rerun()
            
    # Show party selector if requested
    if st.session_state.get('show_party_selector', False):
        st.markdown("---")
        load_parties_interface()

else:
    # No current party - show creation form and load options
    st.markdown("**Create a new party or load an existing one:**")
    
    # New party form
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_party_name = st.text_input(
            "Party Name", 
            placeholder="e.g., Friday Night Dinner, John's Birthday...",
            key="new_party_name"
        )
    
    with col2:
        if st.button("Create Party", type="primary", disabled=not new_party_name.strip()):
            if new_party_name.strip():
                create_new_party(new_party_name.strip())
                st.success(f"✅ Created party: {new_party_name}")
                st.info("💡 Remember to click '💾 Save Party' to persist your data!")
                st.rerun()
    
    # Load existing parties
    st.markdown("**Or load an existing party:**")
    load_parties_interface()
    
    # Debug localStorage contents
    if st.button("🔍 Debug: Check localStorage", type="secondary"):
        components.html("""
        <script>
            try {
                const parties = localStorage.getItem('restaurant_bill_splitter_parties');
                const currentParty = localStorage.getItem('restaurant_bill_splitter_current_party');
                
                let debugInfo = 'localStorage Contents:\\n\\n';
                debugInfo += 'Parties raw data: ' + (parties || 'null') + '\\n\\n';
                debugInfo += 'Current party ID: ' + (currentParty || 'null') + '\\n\\n';
                
                if (parties) {
                    try {
                        const parsed = JSON.parse(parties);
                        debugInfo += 'Parsed parties count: ' + Object.keys(parsed).length + '\\n';
                        debugInfo += 'Party IDs: ' + Object.keys(parsed).join(', ') + '\\n\\n';
                        
                        for (const [id, party] of Object.entries(parsed)) {
                            debugInfo += 'Party "' + party.name + '": \\n';
                            debugInfo += '  - Friends: ' + (party.friends ? party.friends.length : 0) + '\\n';
                            debugInfo += '  - Items: ' + (party.items ? party.items.length : 0) + '\\n';
                            debugInfo += '  - Total: $' + (party.total_cost || 0).toFixed(2) + '\\n\\n';
                        }
                    } catch(e) {
                        debugInfo += 'Error parsing parties: ' + e.message + '\\n';
                    }
                } else {
                    debugInfo += 'No parties data found in localStorage\\n';
                }
                
                alert(debugInfo);
            } catch(e) {
                alert('Debug error: ' + e.message);
            }
        </script>
        """, height=0)

# Show new party form if requested
if st.session_state.get('show_new_party_form', False):
    st.markdown("---")
    st.subheader("🆕 Create New Party")
    
    new_party_name = st.text_input(
        "Party Name", 
        placeholder="e.g., Saturday Brunch, Team Dinner...",
        key="new_party_form_name"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Create New Party", type="primary", disabled=not new_party_name.strip()):
            if new_party_name.strip():
                create_new_party(new_party_name.strip())
                st.session_state.show_new_party_form = False
                st.success(f"✅ Created party: {new_party_name}")
                st.info("💡 Remember to click '💾 Save Party' to persist your data!")
                st.rerun()
    
    with col2:
        if st.button("Cancel", type="secondary"):
            st.session_state.show_new_party_form = False
            st.rerun()

# Show parties list if available
show_parties_list()

# Only show the rest of the app if we have an active party
if not st.session_state.current_party_id:
    # Don't show the info message if we're showing the parties list
    if not st.session_state.get('show_parties_list', False):
        st.info("👆 Create or select a party to start splitting bills!")
    st.stop()

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
    if restaurant_name != st.session_state.get('restaurant_name', ''):
        st.session_state.restaurant_name = restaurant_name
else:
    restaurant_name_only = selected_restaurant.split(" (")[0]
    restaurant_name = st.text_input("Restaurant Name", value=restaurant_name_only, disabled=True)
    if restaurant_name_only != st.session_state.get('restaurant_name', ''):
        st.session_state.restaurant_name = restaurant_name_only
    
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
            st.success(f"Added {item_name} (${item_cost:.2f}) - Don't forget to save!")
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
            st.success(f"Added {friend_name_clean} - Don't forget to save!")
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
            changes_made = False
            for item_name, qty in item_quantities.items():
                if qty != current_quantities.get(item_name, 0):
                    changes_made = True
                    # Update the assignments
                    for item in st.session_state.bill_items:
                        if item['name'] == item_name:
                            # Remove all existing entries for this friend
                            item['ordered_by'] = [f for f in item['ordered_by'] if f != friend]
                            # Add friend back for the specified quantity
                            for _ in range(qty):
                                item['ordered_by'].append(friend)
                            break
            
            # Changes will be saved when user clicks Save Party button
            
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

# Party Actions
col1, col2 = st.columns(2)

with col1:
    if st.button("🗑️ Delete Current Party", type="secondary", help="Delete this party permanently"):
        if st.session_state.current_party_id:
            # Show confirmation in JavaScript and handle deletion
            components.html(f"""
            <script>
                if (confirm('Are you sure you want to delete the party "{st.session_state.party_name}"?')) {{
                    try {{
                        let parties = JSON.parse(localStorage.getItem('restaurant_bill_splitter_parties') || '{{}}');
                        delete parties['{st.session_state.current_party_id}'];
                        localStorage.setItem('restaurant_bill_splitter_parties', JSON.stringify(parties));
                        localStorage.removeItem('restaurant_bill_splitter_current_party');
                        window.location.href = window.location.origin + window.location.pathname;
                    }} catch(e) {{
                        alert('Failed to delete party: ' + e.message);
                    }}
                }}
            </script>
            """, height=0)

with col2:
    if st.button("🧮 Calculate Bill Split", type="primary", help="Show detailed bill breakdown for all friends"):
        st.session_state.show_bill_results = True
        st.rerun()

# Display bill results if requested
display_bill_results()
