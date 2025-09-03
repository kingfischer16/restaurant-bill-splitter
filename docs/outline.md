# Project Outline: Streamlit Restaurant Bill Splitter Web App

## 1. Project Overview

**Project Title:** Restaurant Bill Splitter  
**Current Status:** Fully functional core application (982 lines)
**Objective:** Single-page web application for restaurant bill splitting with party management and localStorage persistence
**Core Technology:** Python with the Streamlit framework  
**Target Audience:** Personal use with mobile-first design
**Project Lead:** Human Developer

**Current Features:**
- ✅ Multi-party management with localStorage persistence
- ✅ Pre-configured restaurant system with course-based pricing
- ✅ Friend-centric item assignment with quantities
- ✅ Real-time bill calculations
- ✅ Formal "Calculate Bill Split" with comprehensive results display
- ✅ Mobile-optimized single-column responsive design
- ⚠️ Party loading temporarily disabled due to Streamlit iframe security constraints

This document reflects the current state of the fully functional application.

---

## 2. Current Application State

**Development Status:** Core application complete with 13 primary functions and comprehensive functionality.

**Application Architecture:**
- Single-file Streamlit application (`app.py` - 982 lines)
- Mobile-first responsive design with single-column layout
- localStorage-based persistence across browser sessions
- Component-based JavaScript integration for browser storage
- Session state management for real-time updates

**Core Functions Implemented:**
1. `load_restaurants()` - Load pre-configured restaurant data
2. `generate_party_id()` - Create unique party identifiers
3. `get_current_party_data()` - Extract party data from session state
4. `calculate_total_cost()` - Calculate total party cost
5. `save_current_party()` - Persist party to localStorage
6. `load_parties_interface()` - Party loading UI (temporarily disabled)
7. `load_party_from_url()` - URL parameter party loading
8. `show_parties_list()` - Display saved parties list
9. `create_new_party()` - Initialize new party session
10. `display_bill_results()` - Formal bill split results display
11. `get_friend_item_quantities()` - Calculate friend item quantities
12. `update_item_assignments_with_quantities()` - Update item assignments
13. `calculate_friend_total()` - Calculate individual friend totals

---

## 3. Current Functional Capabilities

**✅ IMPLEMENTED FEATURES:**

*   **F1: Party Management:** ✅ Create, name, and save multiple dining parties with UUID identifiers. Each party maintains independent session data.
*   **F1B: Party Persistence:** ✅ All party data persists in browser localStorage across sessions, refreshes, and browser closures.
*   **F1C: Party Actions:** ✅ Delete parties functionality. (Rename/duplicate pending)
*   **F2: Restaurant Selection:** ✅ Dropdown with pre-configured restaurants (Frank's Kro, Custom Restaurant) with automatic menu loading.
*   **F2B: Course-Based Pricing:** ✅ Full support for restaurants with course pricing models (base course + item surcharges).
*   **F3: Add Menu Items:** ✅ Form to input item name, category, and cost. Items classified by category (Starter, Main, Dessert, Drink, Other).
*   **F4: Add Friends:** ✅ Input field with auto-clear, duplicate prevention, and validation.
*   **F5: Friend-Centric Assignment:** ✅ Item selection per friend with quantity controls. Course items limited to qty 1, Drinks/Other unlimited.
*   **F5B: Real-Time Totals:** ✅ Live calculation and display of totals per friend including course-based pricing.
*   **F6: Calculate Bill Split:** ✅ Each friend pays full cost for items they ordered (no cost sharing).
*   **F7: Display Results:** ✅ Real-time display with category ordering + formal "Calculate Bill Split" button with comprehensive results.

**⏳ PENDING FEATURES:**

*   **F8: Export to XLSX:** ⏳ Download functionality for detailed bill breakdown (Step 5).
*   **F9A: Party Loading:** ⚠️ Temporarily disabled due to Streamlit iframe security constraints.
*   **F9B: Party Rename/Duplicate:** ⏳ Advanced party management features.

---

## 4. Current Usage Instructions

**Starting the Application:**
```bash
cd "D:\GitProjects\restaurant-bill-splitter"
streamlit run app.py
```

**Basic Workflow:**
1. **Create Party:** Enter party name and click "Create Party"
2. **Select Restaurant:** Choose from dropdown (Frank's Kro or Custom Restaurant)
3. **Add Items:** Use the form to add menu items with categories and costs
4. **Add Friends:** Enter friend names (auto-clears, prevents duplicates)
5. **Assign Items:** For each friend, select items and set quantities
6. **Calculate Bill:** Click "🧮 Calculate Bill Split" for comprehensive results
7. **Save Party:** Click "💾 Save Party" to persist data to localStorage

**Key Features:**
- **Real-time Calculations:** Totals update automatically as you assign items
- **Course-based Pricing:** Frank's Kro includes course fees (125 DKK base + item costs)
- **Category Ordering:** Items display in meal progression (Starter→Main→Dessert→Drink→Other)
- **Quantity Controls:** Course items max 1, Drinks/Other unlimited
- **Mobile Optimized:** Single-column layout works well on phones
- **Data Persistence:** All data saved to browser localStorage

**Known Issues:**
- **Party Loading:** Temporarily disabled due to Streamlit iframe security constraints
- **Workaround:** Use "🔍 Debug: Check localStorage" to inspect saved party data

---

## 5. Technical Architecture

*   **Language:** Python 3.9+
*   **Framework:** Streamlit. This is the required framework to ensure the entire application can be built within a single Python script without separate frontend code.
*   **Primary Libraries:**
    *   `streamlit`: For the web framework and all UI components.
    *   `pandas`: To structure the data for clean and easy export to XLSX.
    *   `openpyxl`: The engine for Pandas to write `.xlsx` files.
    *   `json`: For loading pre-configured restaurant data.
*   **State Management:**
    *   All application state managed using Streamlit's `st.session_state` object with `current_party_id` determining active party.
    *   Party data persisted in browser localStorage with automatic saving on state changes.
*   **Data Structures:**
    *   **Party Object:** Each party stored in localStorage with structure:
        ```python
        {
            "id": str,              # Unique party identifier (UUID)
            "name": str,            # User-defined party name
            "restaurant_name": str, # Selected restaurant
            "selected_restaurant": str, # Restaurant selection key
            "created": str,         # ISO datetime string
            "last_updated": str,    # ISO datetime string  
            "friends": list[str],   # List of friend names
            "items": list[dict],    # Menu items (same structure as before)
            "total_cost": float     # Calculated total for quick display
        }
        ```
    *   **Items List:** Within each party, items follow existing structure:
        ```python
        {
            "name": str,
            "category": str,  # Starter, Main, Dessert, Drink, Other
            "cost": float,
            "ordered_by": list[str], # Friend names (duplicates for quantities)
            "is_course_item": bool   # For course-based pricing
        }
        ```
    *   **localStorage Structure:**
        ```javascript
        {
            "restaurant_bill_splitter_parties": {
                "party_uuid_1": {...party_data...},
                "party_uuid_2": {...party_data...}
            },
            "restaurant_bill_splitter_current_party": "party_uuid_1"
        }
        ```
*   **File Structure:**
    *   `app.py`: The single Python file containing all application logic and UI definitions (982 lines).
    *   `restaurants.json`: Pre-configured restaurant menus with course pricing data.
    *   `requirements.txt`: A file listing all library dependencies.
    *   `dev-requirements.txt`: Development dependencies.
    *   `docs/outline.md`: Comprehensive project documentation.
    *   `docs/roadmap.md`: Implementation progress tracking.
    *   `.claude/CLAUDE.md`: Development guidance for Claude Code.

---

## 5. UI/UX Flow (Mobile-First Single Column)

The application interface is organized in a logical, mobile-optimized single-column flow:

1.  **Header:** Title of the app with party name and navigation.
2.  **Party Management Section:**
    *   Party selector dropdown (shows all saved parties)
    *   "New Party" button to create fresh party
    *   Current party info (name, date, participants count)
    *   Party actions (rename, delete, duplicate)
3.  **Restaurant Setup Section:**
    *   Restaurant selection dropdown (pre-configured or custom)
    *   Restaurant name input (auto-populated or manual)
    *   Course pricing display for course-based restaurants
    *   Add menu items form (item name, category, cost)
    *   Current menu display
4.  **Add Friends Section:**
    *   Simple friend name input field with auto-clear functionality
    *   Current friends list display
5.  **Friend Orders Section:**
    *   Individual sections for each friend
    *   Item selection dropdown (showing unselected items)
    *   Selected items with quantity controls and remove buttons
    *   Real-time total calculation per friend
6.  **Actions & Results Section:**
    *   Calculate Bill Split button
    *   XLSX Export functionality
    *   Party management actions

---

## 6. Implementation Plan

**Step 0: Environment Setup** ✅ **COMPLETED**
*   Created `requirements.txt` with streamlit, pandas, and openpyxl dependencies.

**Step 1: Application Skeleton and State Initialization** ✅ **COMPLETED** 
*   Set up page configuration with mobile-first single-column layout.
*   Initialize session state with `bill_items`, `bill_friends`, and `selected_restaurant`.
*   Implemented mobile-optimized UI flow with clear section separations.

**Step 2: Restaurant Selection and Input Forms** ✅ **COMPLETED**
*   Implemented restaurant selection dropdown with pre-configured restaurants from `restaurants.json`.
*   Added course-based pricing support with automatic menu loading.
*   Created menu item form with category classification and validation.
*   Implemented friend input with auto-clearing functionality and duplicate prevention.

**Step 3: Friend-Centric Assignment UI** ✅ **COMPLETED** 
*   **REDESIGNED:** Changed from item-centric to friend-centric assignment model.
*   Implemented quantity-based selection (course items max 1, drinks/other unlimited).
*   Added real-time total calculation per friend with course-based pricing support.
*   Created mobile-friendly item management with add/remove/quantity controls.

**Step 4: Party Management System & Bill Calculation** ✅ **COMPLETED**
*   **IMPLEMENTED:** Complete multi-party system with localStorage persistence.
*   ✅ Party creation, naming, and selection functionality.
*   ✅ Party list interface with summary information.
*   ✅ Party switching without data loss.
*   ✅ Party management actions (delete functionality).
*   ✅ **Bill Calculation:** Formal "Calculate Bill Split" button with comprehensive results display.

**Step 5: XLSX Export Functionality** ⏳ **PENDING**
*   Create export function for detailed bill breakdown with categories and quantities.
*   Include course pricing breakdown and party information in export data.
*   Add party name and date to exported files.

**Step 6: Reset Functionality** ⏳ **PENDING**
*   Implement complete session reset functionality.
*   Clear party data, localStorage, and return to initial state.

**Step 7: Party Enhancement Features** ⏳ **PENDING**
*   Party renaming and duplication functionality.
*   Party history view with cost summaries.
*   Party search and filtering capabilities.
