# Project Outline: React Restaurant Bill Splitter Web App

## 1. Project Overview

**Project Title:** Restaurant Bill Splitter  
**Current Status:** Fully functional React application  
**Objective:** Single-page web application for restaurant bill splitting with party management and localStorage persistence  
**Core Technology:** React 18.2.0 with modern JavaScript (ES6+)  
**Target Audience:** Personal use with mobile-first design  
**Project Lead:** Human Developer

**Current Features:**
- ✅ Multi-party management with localStorage persistence
- ✅ Pre-configured restaurant system with automatic menu loading
- ✅ Custom restaurant creation with menu builder
- ✅ Friend-centric item assignment with quantity controls
- ✅ Real-time bill calculations with Danish Krone (DKK) currency
- ✅ Mobile-optimized responsive design without scroll boxes
- ✅ Complete workflow: Party → Friends → Menu → Orders → Calculate
- ✅ Category-based quantity restrictions (Drink/Other increments only)
- ✅ Email integration for bill summaries

This document reflects the current state of the fully functional React application.

---

## 2. Current Application State

**Development Status:** Complete React application with modern web architecture and full functionality.

**Application Architecture:**
- React 18.2.0 single-page application (SPA)
- Component-based architecture with functional components and hooks
- Mobile-first responsive design with CSS flexbox
- localStorage-based persistence with no server dependencies  
- Static deployment ready (can be served from any web server)
- Hot reloading development environment

**Core Technology Stack:**
- **Frontend:** React 18.2.0, modern JavaScript (ES6+)
- **Styling:** CSS-in-HTML with responsive design
- **State Management:** React useState and useEffect hooks
- **Persistence:** Browser localStorage API
- **Build System:** Create React App (react-scripts 5.0.1)
- **Development:** Hot reloading with webpack dev server
- **Deployment:** GitHub Pages ready with gh-pages integration

**File Structure:**
```
react-app/
├── public/
│   ├── index.html          # Main HTML template with embedded CSS
│   └── restaurants.json    # Restaurant data with Danish Krone pricing
├── src/
│   ├── App.js             # Main React component (700+ lines)
│   └── index.js           # React entry point
└── package.json           # Dependencies and scripts
```

---

## 3. Current Functional Capabilities

**✅ IMPLEMENTED FEATURES:**

* **F1: Party Management:** ✅ Create, name, and save multiple dining parties with UUID identifiers. Each party maintains independent session data.
* **F1B: Party Persistence:** ✅ All party data persists in browser localStorage across sessions, refreshes, and browser closures.
* **F1C: Party Loading:** ✅ Load existing parties from localStorage with complete state restoration.
* **F2: Restaurant Selection:** ✅ Choose from pre-configured restaurants (Frank's Kro, The Burger Joint, Sakura Sushi) or create custom restaurants.
* **F2B: Course-Based Pricing:** ✅ Full support for restaurants with course pricing models (Frank's Kro with course fees).
* **F2C: Custom Restaurant Creation:** ✅ Complete menu builder for custom restaurants with category classification.
* **F3: Add Menu Items:** ✅ Form to input item name, category, and cost. Items classified by category (Starter, Main, Dessert, Drink, Other).
* **F4: Add Friends:** ✅ Input field with validation, duplicate prevention, and real-time total display.
* **F5: Friend-Centric Assignment:** ✅ Dropdown-based item selection per friend with quantity controls.
* **F5B: Category-Based Quantities:** ✅ Drink and Other items allow multiple quantities; Starter/Main/Dessert are unique per person.
* **F5C: Real-Time Totals:** ✅ Live calculation and display of totals per friend in Danish Krone (DKK).
* **F6: Calculate Bill Split:** ✅ Each friend pays full cost for items they ordered (no cost sharing).
* **F7: Display Results:** ✅ Comprehensive bill calculation page with individual breakdowns and party totals.
* **F8: Mobile Optimization:** ✅ Responsive design without scroll boxes, mobile-friendly interface.
* **F9: Currency Localization:** ✅ Danish Krone (DKK) formatting throughout application ("75.00 kr" format).
* **F10: Email Integration:** ✅ Bill summary email functionality using mailto: scheme.

**🚀 ADVANTAGES OF REACT IMPLEMENTATION:**

* **Better User Experience:** No page refreshes, instant state updates, smooth interactions
* **Mobile Performance:** Optimized for mobile devices with responsive design
* **Deployment Flexibility:** Static files can be deployed anywhere (GitHub Pages, Netlify, etc.)
* **No Server Required:** Pure client-side application with localStorage persistence
* **Modern Development:** Hot reloading, component architecture, easier maintenance
* **Security:** No iframe constraints, direct localStorage access

---

## 4. Current Usage Instructions

**Starting the Development Server:**
```bash
cd "D:\GitProjects\restaurant-bill-splitter\react-app"
npm start
# Application runs at http://localhost:3000 (or PORT=3001 if 3000 is occupied)
```

**Production Build:**
```bash
cd "D:\GitProjects\restaurant-bill-splitter\react-app"
npm run build
# Creates optimized static files in build/ directory
```

**Deploy to GitHub Pages:**
```bash
cd "D:\GitProjects\restaurant-bill-splitter\react-app"
npm run deploy
# Builds and deploys to GitHub Pages
```

**Complete Workflow:**
1. **Start Page:** Choose to create new party or load existing party
2. **Party Setup:** Enter party name and select restaurant (built-in or custom)
3. **Friends Management:** Add friends to the party (names with real-time totals)
4. **Menu Creation:** If custom restaurant, add menu items with categories and prices
5. **Orders:** For each friend, select items from dropdown and manage quantities
6. **Bill Calculation:** View comprehensive bill breakdown with individual and total costs
7. **Email Summary:** Send bill details via email using default email client

**Key Features:**
- **Restaurant Types:**
  - **Built-in:** Frank's Kro (Danish), The Burger Joint (American), Sakura Sushi (Japanese)
  - **Custom:** Create your own restaurant with custom menu items
- **Smart Quantities:** Only Drink and Other items can have multiple quantities
- **Danish Currency:** All prices displayed as "X.XX kr" format
- **Party Persistence:** Save/load parties with complete state restoration
- **Mobile-First:** Optimized for mobile use without scroll boxes
- **Real-time Updates:** Totals and calculations update immediately
- **Email Bills:** Share calculated bills via email

---

## 5. Technical Architecture

* **Language:** JavaScript (ES6+)
* **Framework:** React 18.2.0. React provides superior user experience, mobile performance, and deployment flexibility compared to server-based solutions.
* **Primary Libraries:**
  * `react`: Core React library for component-based UI
  * `react-dom`: React DOM rendering
  * `react-scripts`: Create React App build tools and development server
  * `gh-pages`: GitHub Pages deployment tool
* **State Management:**
  * All application state managed using React hooks (`useState`, `useEffect`)
  * Party data persisted in browser localStorage with automatic saving
  * Real-time state synchronization across components
* **Data Structures:**
  * **Party Object:** Each party stored in localStorage with structure:
    ```javascript
    {
      "id": string,              // Unique party identifier (timestamp + random)
      "name": string,            // User-defined party name  
      "restaurant_name": string, // Selected restaurant name
      "selected_restaurant": string, // Restaurant selection key
      "custom_menu_items": array, // Custom menu items for custom restaurants
      "created": string,         // ISO datetime string
      "last_updated": string,    // ISO datetime string
      "friends": array,          // List of friend names
      "orders": object,          // Friend orders: {friendName: [items]}
      "total_cost": number       // Calculated total for quick display
    }
    ```
  * **Order Item Structure:**
    ```javascript
    {
      "id": string,           // Unique item identifier
      "name": string,         // Item name
      "cost": number,         // Item cost in DKK
      "quantity": number,     // Quantity ordered
      "category": string      // Starter, Main, Dessert, Drink, Other
    }
    ```
  * **localStorage Structure:**
    ```javascript
    {
      "restaurant_parties": [
        {...party_data_1...},
        {...party_data_2...}
      ]
    }
    ```
* **File Structure:**
  * `react-app/src/App.js`: Main React component containing all application logic (700+ lines)
  * `react-app/public/index.html`: HTML template with embedded responsive CSS
  * `react-app/public/restaurants.json`: Pre-configured restaurant menus with DKK pricing
  * `react-app/package.json`: Dependencies and build scripts
  * `docs/outline.md`: Comprehensive project documentation
  * `docs/roadmap.md`: Implementation progress tracking

---

## 6. UI/UX Flow (Mobile-First Design)

The React application provides a smooth, single-page experience with step-based navigation:

1. **Start Page:**
   * Welcome screen with app title
   * "Create New Party" button
   * List of saved parties with load options
   * Party summary information (name, restaurant, total, date)

2. **Party Setup:**
   * Party name input field
   * Restaurant selection dropdown (built-in or custom)
   * Automatic restaurant name population
   * Navigation to friends management

3. **Friends Management:**
   * Friend name input with add button
   * Friends list with individual totals and item counts
   * Remove friend functionality
   * Progress to menu creation or orders

4. **Menu Creation (Custom Restaurants):**
   * Item name, price, and category inputs
   * Add item functionality with validation
   * Current menu display with remove options
   * Progress to orders when ready

5. **Orders Management:**
   * Individual sections per friend
   * Item selection via dropdown menu
   * Quantity controls for Drink/Other categories
   * Real-time total calculations per friend
   * Remove items functionality

6. **Bill Calculation:**
   * Overall party metrics (total bill, friends count, items count)
   * Individual friend breakdowns with itemized lists
   * Quantity and pricing details
   * Danish Krone formatting throughout
   * Email summary functionality

7. **Navigation:**
   * Persistent navigation bar with step access
   * Save Party and Reset functionality
   * Mobile-optimized button layouts

---

## 7. Implementation History

**✅ COMPLETED PHASES:**

**Phase 1: Initial Planning**
* Project conceptualization and requirements gathering
* Technology evaluation (considered Python/Streamlit, chose React)
* Core functionality design

**Phase 2: React Implementation**
* Created React 18.2.0 application with Create React App
* Implemented component-based architecture
* Developed mobile-first responsive design

**Phase 3: Core Functionality**
* Multi-restaurant system with pre-configured menus
* Friend-centric ordering workflow
* Real-time calculations and state management
* localStorage integration for data persistence

**Phase 4: User Experience Refinements**
* Items-to-people assignment model
* Dropdown-based item selection
* Category-based quantity restrictions
* Mobile-first responsive design optimization

**Phase 5: Localization & Polish**
* Danish Krone currency formatting
* Removed all scroll boxes for mobile friendliness
* Optimized user workflow and navigation
* Email integration for bill sharing

**Phase 6: Deployment Preparation**
* GitHub Pages deployment configuration
* Build optimization and testing
* Production-ready codebase

**🎯 CURRENT STATUS:** Fully functional React application with complete feature set, optimized for mobile use and Danish market, ready for production deployment.

---

## 8. Future Enhancement Opportunities

**Potential Future Features:**
- XLSX export functionality for detailed bill reports
- Reset functionality for clearing party data
- Enhanced party management (rename, duplicate parties)
- Receipt scanning with OCR integration
- Tip calculator with automatic distribution
- Multi-language support beyond Danish
- Cloud synchronization for party sharing
- Progressive Web App (PWA) capabilities
- Analytics and dining history tracking

**Deployment Enhancements:**
- Custom domain configuration
- CDN integration for global performance
- Advanced caching strategies
- Mobile app wrapper (Cordova/PhoneGap)

The application represents a complete, production-ready solution for restaurant bill splitting with modern web technologies and optimal user experience.