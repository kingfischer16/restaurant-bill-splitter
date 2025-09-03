# Project Outline: Streamlit Restaurant Bill Splitter Web App

## 1. Project Overview

**Project Title:** Restaurant Bill Splitter
**Objective:** Develop a simple, single-page web application for personal use that allows a user to input restaurant items, assign them to friends, and calculate a split bill.
**Core Technology:** Python with the Streamlit framework.
**Target Audience (Developer):** Claude Code (AI Developer)
**Project Lead:** Human Developer (for guidance, code review, and final decisions)

This document outlines the architecture, features, and development plan for the Bill Splitter app. It is the single source of truth and should be referenced throughout the development lifecycle.

---

## 2. Development Process and Collaboration Model

**To Claude Code:** Your role is to be the primary developer, executing the plan outlined below. This is a collaborative project that requires a strict iterative process. You **must not** generate the entire application in a single response.

The development process will be as follows for each step in the **Implementation Plan** (Section 6):
1.  **Acknowledge and Plan:** State the step you are beginning. Outline your proposed approach, including function signatures and logic flow, before writing the full implementation.
2.  **Await Approval:** Wait for the human project lead to review and approve your plan.
3.  **Execute:** Write the Python code for the approved step **only**. Ensure the code is clean, commented where necessary, and adheres to PEP 8 standards.
4.  **Submit for Review:** Present the completed code for the current step.
5.  **Proceed:** After review and approval, move to the next step.

This **Plan -> Review -> Execute -> Review** cycle is mandatory.

---

## 3. Core Functional Requirements

The application must provide the following functionalities:

*   **F1: Session Persistence:** The app must retain all user-entered data (items, friends, assignments) for the duration of a user's browser session.
*   **F2: Restaurant Selection:** Dropdown to select from pre-configured restaurants or choose "Custom Restaurant" for manual entry.
*   **F2B: Course-Based Pricing:** Support for restaurants with course pricing models (base course price + individual item surcharges).
*   **F3: Add Menu Items:** A form to input an item's name, category, and cost. Items include category classification (Starter, Main, Dessert, Drink, Other). Added items must appear in a list.
*   **F4: Add Friends:** Simple input field to add friend names. Empty names and duplicates are prevented. Input field clears automatically after adding.
*   **F5: Friend-Centric Assignment:** For each friend, allow selection of menu items with quantity controls. Course items (Starter/Main/Dessert) limited to quantity 1, Drinks/Other unlimited.
*   **F5B: Real-Time Totals:** Display running totals for each friend as items are assigned, including course-based pricing calculations.
*   **F6: Calculate Bill Split:** Each friend pays full cost for items they ordered (no cost sharing between friends).
*   **F7: Display Results:** Real-time display of each friend's items and total amount owed with category ordering (Starter→Main→Dessert→Drink→Other).
*   **F8: Export to XLSX:** A button to download the item list (name, category, cost, and who ordered it) as an `.xlsx` file.
*   **F9: Reset Session:** A button to clear all entered data and start over.

---

## 4. Technical Architecture

*   **Language:** Python 3.9+
*   **Framework:** Streamlit. This is the required framework to ensure the entire application can be built within a single Python script without separate frontend code.
*   **Primary Libraries:**
    *   `streamlit`: For the web framework and all UI components.
    *   `pandas`: To structure the data for clean and easy export to XLSX.
    *   `openpyxl`: The engine for Pandas to write `.xlsx` files.
    *   `json`: For loading pre-configured restaurant data.
*   **State Management:**
    *   All application state (list of items, friends, etc.) will be managed using Streamlit's `st.session_state` object. Session state keys use `bill_` prefix to avoid naming conflicts.
*   **Data Structures:**
    *   **Items List:** A `list` of `dict` objects stored in `st.session_state.bill_items`. Each dictionary structure:
        ```python
        {
            "name": str,
            "category": str,  # Starter, Main, Dessert, Drink, Other
            "cost": float,
            "ordered_by": list[str], # Friend names (duplicates for quantities)
            "is_course_item": bool   # For course-based pricing
        }
        ```
    *   **Friends List:** A simple `list` of `str` objects stored in `st.session_state.bill_friends`.
    *   **Restaurant Data:** Loaded from `restaurants.json` with course pricing and menu information.
*   **File Structure:**
    *   `app.py`: The single Python file containing all application logic and UI definitions.
    *   `restaurants.json`: Pre-configured restaurant menus with course pricing data.
    *   `requirements.txt`: A file listing all library dependencies.

---

## 5. UI/UX Flow (Mobile-First Single Column)

The application interface is organized in a logical, mobile-optimized single-column flow:

1.  **Header:** Title of the app and a brief instructional subtitle.
2.  **Restaurant Setup Section:**
    *   Restaurant selection dropdown (pre-configured or custom)
    *   Restaurant name input (auto-populated or manual)
    *   Course pricing display for course-based restaurants
    *   Add menu items form (item name, category, cost)
    *   Current menu display
3.  **Add Friends Section:**
    *   Simple friend name input field with auto-clear functionality
    *   Current friends list display
4.  **Friend Orders Section:**
    *   Individual sections for each friend
    *   Item selection dropdown (showing unselected items)
    *   Selected items with quantity controls and remove buttons
    *   Real-time total calculation per friend
5.  **Actions & Results Section:**
    *   Calculate Bill Split button (placeholder)
    *   XLSX Export functionality (placeholder)  
    *   Reset Session functionality (placeholder)

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

**Step 4: Enhanced Bill Calculation Logic** ✅ **PARTIALLY COMPLETED**
*   **REDESIGNED:** Each friend pays full cost for items they ordered (no cost sharing).
*   Implemented real-time calculation with course-based pricing formulas.
*   Added category-ordered item display (Starter→Main→Dessert→Drink→Other).
*   **PENDING:** Formal "Calculate Bill Split" button and summary display.

**Step 5: XLSX Export Functionality** ⏳ **PENDING**
*   Create export function for detailed bill breakdown with categories and quantities.
*   Include course pricing breakdown in export data.

**Step 6: Reset Functionality** ⏳ **PENDING**
*   Implement complete session reset with confirmation dialog.
*   Clear all restaurant data, friends, and assignments.
