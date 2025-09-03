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
*   **F2: Input Restaurant Name:** A text input field to enter the name of the restaurant.
*   **F3: Add Menu Items:** A form to input an item's name (text) and its cost (numeric). Added items must appear in a list. The cost must be greater than zero.
*   **F4: Add Friends:** A form to input a friend's name (text). Empty names should not be added. Duplicate names should be handled gracefully.
*   **F5: Display & Assign Items:** The list of added items must be displayed clearly. Each item must have an interactive element (a multi-select dropdown) allowing the user to select one or more friends who shared that item.
*   **F6: Calculate Bill Split:** A button that calculates the total amount owed by each friend. An item's cost is to be divided equally among all friends assigned to it.
*   **F7: Display Results:** After calculation, the app must clearly display each friend's name and the total amount they owe.
*   **F8: Export to XLSX:** A button to download the item list (name, cost, and who ordered it) as an `.xlsx` file.
*   **F9: Reset Session:** A button to clear all entered data and start over.

---

## 4. Technical Architecture

*   **Language:** Python 3.9+
*   **Framework:** Streamlit. This is the required framework to ensure the entire application can be built within a single Python script without separate frontend code.
*   **Primary Libraries:**
    *   `streamlit`: For the web framework and all UI components.
    *   `pandas`: To structure the data for clean and easy export to XLSX.
    *   `openpyxl`: The engine for Pandas to write `.xlsx` files.
*   **State Management:**
    *   All application state (list of items, friends, etc.) will be managed using Streamlit's `st.session_state` object. This object will serve as the in-memory cache for the user's session, fulfilling requirement **F1**.
*   **Data Structures:**
    *   **Items List:** A `list` of `dict` objects stored in `st.session_state.items`. Each dictionary must adhere to this structure:
        ```python
        {
            "name": str,
            "cost": float,
            "ordered_by": list[str] # A list of friend names
        }
        ```
    *   **Friends List:** A simple `list` of `str` objects stored in `st.session_state.friends`.
*   **File Structure:**
    *   `app.py`: The single Python file containing all application logic and UI definitions.
    *   `requirements.txt`: A file listing all library dependencies.

---

## 5. Proposed UI/UX Flow

The application interface should be organized into a logical, top-to-bottom flow:

1.  **Header:** Title of the app and a brief instructional subtitle.
2.  **Inputs Section:** Use `st.columns` to create a two-column layout.
    *   **Left Column:** Restaurant name input, a `st.form` to add menu items, and a `st.form` to add friends.
    *   **Right Column:** A header for "Assign Items". This area will display the list of added items and their corresponding assignment widgets.
3.  **Actions & Results Section:**
    *   A primary button styled with `type="primary"` to "Calculate Bill Split".
    *   A display area for the results, using `st.metric` for each friend to show their total owed.
    *   A `st.download_button` for the XLSX export.
    *   A final, secondary button to "Clear All Data".

---

## 6. Implementation Plan

**Step 0: Environment Setup**
*   Propose the contents for `requirements.txt`. The file should pin the major versions of the libraries (e.g., `streamlit~=1.0`, `pandas~=2.0`).

**Step 1: Application Skeleton and State Initialization**
*   Set up the page configuration using `st.set_page_config` (title, layout).
*   Write the initialization block that checks for `items` and `friends` in `st.session_state` and creates them as empty lists if they don't exist.
*   Define the main title and the two-column layout structure.

**Step 2: Implement Input Forms**
*   In the left column, create the `st.text_input` for the restaurant name.
*   Create a `st.form` for adding menu items. Include validation to ensure the item name is not empty and the cost is a positive number. On valid submission, append the new item dictionary to `st.session_state.items`.
*   Create a separate `st.form` for adding friends. Include validation to prevent adding empty or duplicate names.

**Step 3: Implement Item Display and Assignment UI**
*   In the right column, iterate through `st.session_state.items`.
*   For each item, display its name and cost.
*   Next to each item, implement a `st.multiselect` widget.
    *   `options`: `st.session_state.friends`.
    *   `default`: The item's existing `ordered_by` list, to preserve selections on reruns.
    *   `key`: A unique key must be generated for each widget (e.g., `f"ms_{i}"` where `i` is the loop index) to prevent state conflicts.
    *   The return value of the multiselect should update the `ordered_by` list in the corresponding item's dictionary.

**Step 4: Implement Bill Calculation Logic**
*   Add the "Calculate Bill Split" button.
*   When clicked, the button's logic should execute the following:
    1.  Initialize a dictionary with friend names as keys and `0.0` as values.
    2.  Iterate through `st.session_state.items`.
    3.  For each item, check if the `ordered_by` list is not empty. If it is, calculate the `split_cost` (`item_cost / len(ordered_by)`).
    4.  Add the `split_cost` to the total for each friend in the `ordered_by` list.
    5.  After the loop, display the results for each friend using `st.metric`.

**Step 5: Implement XLSX Export Functionality**
*   Define a separate helper function, `generate_xlsx()`. This function will:
    1.  Create a pandas DataFrame from `st.session_state.items`.
    2.  Use `io.BytesIO` to create an in-memory binary buffer.
    3.  Write the DataFrame to the buffer in Excel format using `df.to_excel()`.
    4.  Return the buffer's content.
*   Add a `st.download_button` to the UI. The `data` argument for this button must call the `generate_xlsx()` function.

**Step 6: Implement Reset Functionality**
*   Add a final button, "Clear All Data".
*   The on-click logic for this button should re-initialize all relevant keys in `st.session_state` (`items`, `friends`, etc.) to their empty default states and then trigger a `st.rerun()` to refresh the UI.
