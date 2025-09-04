import React, { useState, useEffect, useRef } from 'react';

function App() {
  const [restaurants, setRestaurants] = useState([]);
  const [currentPartyId, setCurrentPartyId] = useState('');
  const [partyName, setPartyName] = useState('');
  const [selectedRestaurant, setSelectedRestaurant] = useState('Custom Restaurant');
  const [restaurantName, setRestaurantName] = useState('');
  const [customMenuItems, setCustomMenuItems] = useState([]); // For custom restaurants
  const [restaurantCustomItems, setRestaurantCustomItems] = useState({}); // Custom items per restaurant {restaurantName: [items]}
  const [editingItem, setEditingItem] = useState(null); // Item being edited
  const [friends, setFriends] = useState([]);
  const [orders, setOrders] = useState({}); // {friendName: [{id, name, cost, quantity, category}, ...]}
  const [tableOrders, setTableOrders] = useState([]); // [{id, name, cost, quantity, category}, ...] for table items
  const [newFriendName, setNewFriendName] = useState('');
  const [showAlert, setShowAlert] = useState('');
  const [alertType, setAlertType] = useState('');
  const [currentStep, setCurrentStep] = useState('start');
  const [newItemName, setNewItemName] = useState('');
  const [newItemPrice, setNewItemPrice] = useState('');
  const [newItemCategory, setNewItemCategory] = useState('Other');
  const [isEditMode, setIsEditMode] = useState(false);
  const alertTimeoutRef = useRef(null);

  useEffect(() => {
    loadRestaurants();
    generatePartyId();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (alertTimeoutRef.current) {
        clearTimeout(alertTimeoutRef.current);
      }
    };
  }, []);

  const loadRestaurants = async () => {
    try {
      const response = await fetch('/restaurant-bill-splitter/restaurants.json');
      const data = await response.json();
      setRestaurants(data.restaurants || []);
    } catch (error) {
      showMessage('Error loading restaurants data', 'danger');
    }
  };

  const generatePartyId = () => {
    const id = Date.now().toString(36) + Math.random().toString(36).substring(2);
    setCurrentPartyId(id);
  };

  // Input validation utilities
  const sanitizeTextInput = (input) => {
    if (typeof input !== 'string') return '';
    // Normalize Unicode, remove control characters, limit length, trim whitespace
    // eslint-disable-next-line no-control-regex
    const normalized = input.normalize('NFC').replace(/[\x00-\x1F\x7F-\x9F]/g, '');
    return normalized.substring(0, 100).trim();
  };

  const normalizeForComparison = (str) => {
    if (typeof str !== 'string') return '';
    return sanitizeTextInput(str).toLowerCase().normalize('NFC');
  };

  const validatePrice = (priceString, allowZero = false) => {
    if (typeof priceString !== 'string' && typeof priceString !== 'number') return null;
    const price = parseFloat(priceString);
    if (isNaN(price) || !isFinite(price)) return null;
    if (price < 0) return null;
    if (!allowZero && price === 0) return null;
    // Limit to reasonable price range (0-99999.99)
    if (price > 99999.99) return null;
    return Math.round(price * 100) / 100; // Round to 2 decimal places
  };

  const showMessage = (message, type = 'info') => {
    // Clear existing timeout to prevent multiple alerts
    if (alertTimeoutRef.current) {
      clearTimeout(alertTimeoutRef.current);
    }
    
    setShowAlert(message);
    setAlertType(type);
    alertTimeoutRef.current = setTimeout(() => {
      setShowAlert('');
      alertTimeoutRef.current = null;
    }, 3000);
  };

  const saveCurrentParty = () => {
    const sanitizedPartyName = sanitizeTextInput(partyName);
    if (!currentPartyId || !sanitizedPartyName) {
      showMessage('Party name is required to save', 'warning');
      return;
    }

    const partyData = {
      id: currentPartyId,
      name: partyName,
      restaurant_name: restaurantName,
      selected_restaurant: selectedRestaurant,
      custom_menu_items: customMenuItems,
      restaurant_custom_items: restaurantCustomItems,
      created: new Date().toISOString(),
      last_updated: new Date().toISOString(),
      friends: friends,
      orders: orders,
      table_orders: tableOrders,
      total_cost: calculateTotalCost()
    };

    try {
      const existingParties = JSON.parse(localStorage.getItem('restaurant_parties') || '[]');
      const partyIndex = existingParties.findIndex(p => p.id === currentPartyId);
      
      if (partyIndex >= 0) {
        existingParties[partyIndex] = partyData;
      } else {
        existingParties.push(partyData);
      }
      
      localStorage.setItem('restaurant_parties', JSON.stringify(existingParties));
      showMessage('Party saved successfully!', 'success');
    } catch (error) {
      showMessage('Error saving party', 'danger');
    }
  };

  const loadSavedParties = () => {
    try {
      const savedParties = JSON.parse(localStorage.getItem('restaurant_parties') || '[]');
      // Validate and sanitize loaded data
      if (!Array.isArray(savedParties)) return [];
      return savedParties.filter(party => 
        party && typeof party === 'object' && 
        party.id && party.name && 
        Array.isArray(party.friends) &&
        (typeof party.orders === 'object' || !party.orders)
      ).map(party => ({
        ...party,
        name: sanitizeTextInput(party.name || ''),
        restaurant_name: sanitizeTextInput(party.restaurant_name || ''),
        friends: (party.friends || []).map(friend => sanitizeTextInput(friend || '')).filter(f => f)
      }));
    } catch (error) {
      showMessage('Error loading saved parties', 'danger');
      return [];
    }
  };

  const loadParty = (partyData) => {
    setCurrentPartyId(partyData.id);
    setPartyName(partyData.name);
    setRestaurantName(partyData.restaurant_name || '');
    setSelectedRestaurant(partyData.selected_restaurant || 'Custom Restaurant');
    setCustomMenuItems(partyData.custom_menu_items || []);
    setRestaurantCustomItems(partyData.restaurant_custom_items || {});
    setFriends(partyData.friends || []);
    setOrders(partyData.orders || {});
    setTableOrders(partyData.table_orders || []);
    setCurrentStep('orders');
    showMessage('Party loaded successfully!', 'success');
  };

  const startNewParty = () => {
    setCurrentStep('party');
  };

  const addFriend = () => {
    const sanitizedName = sanitizeTextInput(newFriendName);
    if (!sanitizedName) {
      showMessage('Please enter a valid friend name', 'warning');
      return;
    }
    if (friends.some(friend => normalizeForComparison(friend) === normalizeForComparison(sanitizedName))) {
      showMessage('Friend already exists', 'warning');
      return;
    }
    setFriends([...friends, sanitizedName]);
    setNewFriendName('');
    showMessage('Friend added successfully!', 'success');
  };

  const removeFriend = (friendToRemove) => {
    setFriends(friends.filter(friend => friend !== friendToRemove));
    const newOrders = { ...orders };
    delete newOrders[friendToRemove];
    setOrders(newOrders);
    showMessage('Friend removed', 'info');
  };

  const addCustomMenuItem = () => {
    const sanitizedName = sanitizeTextInput(newItemName);
    if (!sanitizedName) {
      showMessage('Please enter a valid item name', 'warning');
      return;
    }
    const price = validatePrice(newItemPrice, true); // Allow zero for custom items
    if (price === null) {
      showMessage('Please enter a valid price (0.00 or higher)', 'warning');
      return;
    }

    const newItem = {
      name: sanitizedName,
      price: price,
      category: newItemCategory
    };

    setCustomMenuItems([...customMenuItems, newItem]);
    setNewItemName('');
    setNewItemPrice('');
    setNewItemCategory('Other');
    showMessage(`Added ${newItem.name} to menu`, 'success');
  };

  const removeCustomMenuItem = (itemIndex) => {
    const newItems = customMenuItems.filter((_, index) => index !== itemIndex);
    setCustomMenuItems(newItems);
    showMessage('Menu item removed', 'info');
  };

  // Functions for managing custom items on existing restaurants
  const addCustomItemToRestaurant = () => {
    const sanitizedName = sanitizeTextInput(newItemName);
    if (!sanitizedName) {
      showMessage('Please enter a valid item name', 'warning');
      return;
    }

    const restaurantData = getSelectedRestaurantData();
    if (!restaurantData) {
      showMessage('Please select a valid restaurant', 'warning');
      return;
    }

    // For course-based restaurants, allow zero prices for course items
    const isCourseItem = restaurantData.pricing_model === 'course_based' && 
                        ['Starter', 'Main', 'Dessert'].includes(newItemCategory);
    const price = validatePrice(newItemPrice, isCourseItem);
    if (price === null) {
      const minPrice = isCourseItem ? '0.00' : '0.01';
      showMessage(`Please enter a valid price (${minPrice} or higher)`, 'warning');
      return;
    }

    // Check for duplicate names in both built-in and custom items
    const allMenuItems = getAllMenuItems();
    if (allMenuItems.some(item => normalizeForComparison(item.name) === normalizeForComparison(sanitizedName))) {
      showMessage('An item with this name already exists', 'warning');
      return;
    }

    const newItem = {
      id: Date.now().toString(), // Add unique ID for custom items
      name: sanitizedName,
      price: price,
      category: newItemCategory,
      is_course_item: isCourseItem,
      custom: true // Mark as custom item
    };

    const currentCustomItems = restaurantCustomItems[selectedRestaurant] || [];
    const updatedCustomItems = {
      ...restaurantCustomItems,
      [selectedRestaurant]: [...currentCustomItems, newItem]
    };
    
    setRestaurantCustomItems(updatedCustomItems);
    setNewItemName('');
    setNewItemPrice('');
    setNewItemCategory('Other');
    showMessage(`Added ${sanitizedName} to ${selectedRestaurant} menu`, 'success');
  };

  const editCustomItem = (item) => {
    setEditingItem(item);
    setNewItemName(item.name);
    setNewItemPrice(item.price.toString());
    setNewItemCategory(item.category);
    setIsEditMode(true);
  };

  const saveEditedItem = () => {
    const sanitizedName = sanitizeTextInput(newItemName);
    if (!sanitizedName) {
      showMessage('Please enter a valid item name', 'warning');
      return;
    }

    const restaurantData = getSelectedRestaurantData();
    if (!restaurantData) {
      showMessage('Please select a valid restaurant', 'warning');
      return;
    }

    // For course-based restaurants, allow zero prices for course items
    const isCourseItem = restaurantData.pricing_model === 'course_based' && 
                        ['Starter', 'Main', 'Dessert'].includes(newItemCategory);
    const price = validatePrice(newItemPrice, isCourseItem);
    if (price === null) {
      const minPrice = isCourseItem ? '0.00' : '0.01';
      showMessage(`Please enter a valid price (${minPrice} or higher)`, 'warning');
      return;
    }

    // Check for duplicate names (excluding the item being edited)
    const allMenuItems = getAllMenuItems();
    if (allMenuItems.some(item => 
      normalizeForComparison(item.name) === normalizeForComparison(sanitizedName) && 
      item.id !== editingItem.id)) {
      showMessage('An item with this name already exists', 'warning');
      return;
    }

    const currentCustomItems = restaurantCustomItems[selectedRestaurant] || [];
    const updatedItems = currentCustomItems.map(item => {
      if (item.id === editingItem.id) {
        return {
          ...item,
          name: sanitizedName,
          price: price,
          category: newItemCategory,
          is_course_item: isCourseItem
        };
      }
      return item;
    });

    const updatedCustomItems = {
      ...restaurantCustomItems,
      [selectedRestaurant]: updatedItems
    };
    
    setRestaurantCustomItems(updatedCustomItems);
    cancelEdit();
    showMessage(`Updated ${sanitizedName} in ${selectedRestaurant} menu`, 'success');
  };

  const cancelEdit = () => {
    setEditingItem(null);
    setNewItemName('');
    setNewItemPrice('');
    setNewItemCategory('Other');
    setIsEditMode(false);
  };

  const removeCustomItemFromRestaurant = (itemId) => {
    const currentCustomItems = restaurantCustomItems[selectedRestaurant] || [];
    const itemToRemove = currentCustomItems.find(item => item.id === itemId);
    
    if (!itemToRemove) return;

    if (window.confirm(`Are you sure you want to remove "${itemToRemove.name}" from the menu?`)) {
      const updatedItems = currentCustomItems.filter(item => item.id !== itemId);
      const updatedCustomItems = {
        ...restaurantCustomItems,
        [selectedRestaurant]: updatedItems
      };
      
      setRestaurantCustomItems(updatedCustomItems);
      showMessage(`Removed ${itemToRemove.name} from menu`, 'info');
      
      // Remove the item from any existing orders
      const updatedOrders = { ...orders };
      Object.keys(updatedOrders).forEach(friendName => {
        updatedOrders[friendName] = updatedOrders[friendName].filter(orderItem => 
          !(orderItem.name === itemToRemove.name && orderItem.custom)
        );
      });
      setOrders(updatedOrders);
    }
  };

  // Functions for managing table orders (shared items)
  const addItemToTableOrders = (menuItem) => {
    // Check if item already exists in table orders
    const existingTableItem = tableOrders.find(item => item.name === menuItem.name);
    
    if (existingTableItem) {
      // Increment quantity
      const updatedTableOrders = tableOrders.map(item => 
        item.name === menuItem.name 
          ? { ...item, quantity: item.quantity + 1 }
          : item
      );
      setTableOrders(updatedTableOrders);
    } else {
      // Add new table item
      const tableOrderItem = {
        id: Date.now().toString() + Math.random().toString(36).substring(2),
        name: menuItem.name,
        cost: menuItem.price,
        quantity: 1,
        category: menuItem.category,
        is_course_item: menuItem.is_course_item || false,
        custom: menuItem.custom || false
      };
      setTableOrders([...tableOrders, tableOrderItem]);
    }
    
    showMessage(`Added ${menuItem.name} to table orders`, 'success');
  };

  const updateTableItemQuantity = (orderItemId, newQuantity) => {
    if (newQuantity <= 0) {
      removeTableItem(orderItemId);
      return;
    }

    const updatedTableOrders = tableOrders.map(item => 
      item.id === orderItemId 
        ? { ...item, quantity: newQuantity }
        : item
    );
    setTableOrders(updatedTableOrders);
  };

  const removeTableItem = (orderItemId) => {
    const updatedTableOrders = tableOrders.filter(item => item.id !== orderItemId);
    setTableOrders(updatedTableOrders);
    showMessage('Table item removed', 'info');
  };

  const addItemToFriendOrder = (friendName, menuItem) => {
    const newOrders = { ...orders };
    if (!newOrders[friendName]) {
      newOrders[friendName] = [];
    }

    const restaurantData = getSelectedRestaurantData();
    const isCourseBasedRestaurant = restaurantData && restaurantData.pricing_model === 'course_based';
    const isCourseItem = menuItem.is_course_item;
    
    // Check if friend already has this item
    const existingOrderItem = newOrders[friendName].find(item => 
      item.name === menuItem.name
    );

    if (existingOrderItem) {
      // For course-based restaurants, course items (Starter/Main/Dessert) can only have quantity 1
      if (isCourseBasedRestaurant && isCourseItem && 
          (menuItem.category === 'Starter' || menuItem.category === 'Main' || menuItem.category === 'Dessert')) {
        showMessage(`${menuItem.name} is a course item and can only be ordered once`, 'warning');
        return;
      }
      // Increment quantity for non-course items or items that allow multiples
      existingOrderItem.quantity += 1;
    } else {
      // Add new item
      const orderItem = {
        id: Date.now().toString() + Math.random().toString(36).substring(2),
        name: menuItem.name,
        cost: menuItem.price,
        quantity: 1,
        category: menuItem.category,
        is_course_item: menuItem.is_course_item || false,
        custom: menuItem.custom || false
      };
      newOrders[friendName].push(orderItem);
    }

    setOrders(newOrders);
    showMessage(`Added ${menuItem.name} to ${friendName}'s order`, 'success');
  };

  const updateItemQuantity = (friendName, orderItemId, newQuantity) => {
    if (newQuantity <= 0) {
      removeItemFromFriendOrder(friendName, orderItemId);
      return;
    }

    const newOrders = { ...orders };
    if (newOrders[friendName]) {
      const item = newOrders[friendName].find(item => item.id === orderItemId);
      if (item) {
        item.quantity = newQuantity;
      }
    }
    setOrders(newOrders);
  };

  const removeItemFromFriendOrder = (friendName, orderItemId) => {
    const newOrders = { ...orders };
    if (newOrders[friendName]) {
      newOrders[friendName] = newOrders[friendName].filter(item => item.id !== orderItemId);
      if (newOrders[friendName].length === 0) {
        delete newOrders[friendName];
      }
    }
    setOrders(newOrders);
    showMessage('Item removed from order', 'info');
  };

  const calculateTableCostPerFriend = () => {
    if (friends.length === 0) return 0;
    const totalTableCost = tableOrders.reduce((total, item) => total + (item.cost * item.quantity), 0);
    return totalTableCost / friends.length;
  };

  const calculateFriendTotal = (friendName) => {
    const friendOrders = orders[friendName] || [];
    const restaurantData = getSelectedRestaurantData();
    
    let individualTotal = 0;
    
    // Check if this is a course-based restaurant
    if (restaurantData && restaurantData.pricing_model === 'course_based') {
      individualTotal = calculateCoursePricingForFriend(friendName, restaurantData);
    } else {
      // Regular pricing: sum all item costs
      individualTotal = friendOrders.reduce((total, item) => total + (item.cost * item.quantity), 0);
    }
    
    // Add their share of table costs
    const tableShare = calculateTableCostPerFriend();
    return individualTotal + tableShare;
  };

  const calculateCoursePricingForFriend = (friendName, restaurantData) => {
    const friendOrders = orders[friendName] || [];
    let total = 0;
    
    // Separate course items from non-course items (drinks, etc.)
    const courseItems = [];
    const nonCourseItems = [];
    
    friendOrders.forEach(orderItem => {
      const menuItem = restaurantData?.menu?.find(m => m.name === orderItem.name);
      if (menuItem && menuItem.is_course_item) {
        // For course items, only count unique courses (ignore quantity > 1 for course items)
        if (!courseItems.some(ci => ci.category === menuItem.category)) {
          courseItems.push({
            category: menuItem.category,
            surcharge: menuItem.price || 0
          });
        }
      } else {
        // Non-course items (drinks, etc.) are charged normally
        nonCourseItems.push(orderItem);
      }
    });
    
    // Calculate course base price
    const courseCount = courseItems.length;
    if (courseCount > 0) {
      const coursePricing = restaurantData.course_pricing;
      let basePrice = 0;
      
      if (courseCount === 1) {
        basePrice = coursePricing['1_course'] || 0;
      } else if (courseCount === 2) {
        basePrice = coursePricing['2_course'] || 0;
      } else if (courseCount >= 3) {
        basePrice = coursePricing['3_course'] || 0;
      }
      
      // Add surcharges for course items
      const surcharges = courseItems.reduce((sum, item) => sum + item.surcharge, 0);
      total += basePrice + surcharges;
    }
    
    // Add non-course items (drinks, etc.)
    total += nonCourseItems.reduce((sum, item) => sum + (item.cost * item.quantity), 0);
    
    return total;
  };

  const calculateTotalCost = () => {
    return friends.reduce((total, friend) => total + calculateFriendTotal(friend), 0);
  };

  const getTotalItems = () => {
    return Object.values(orders).flat().reduce((total, item) => total + item.quantity, 0);
  };

  const resetParty = () => {
    if (window.confirm('Are you sure you want to reset everything? This will clear all current data.')) {
      setPartyName('');
      setSelectedRestaurant('Custom Restaurant');
      setRestaurantName('');
      setCustomMenuItems([]);
      setRestaurantCustomItems({});
      setFriends([]);
      setOrders({});
      setTableOrders([]);
      generatePartyId();
      setCurrentStep('start');
      showMessage('Party reset successfully', 'info');
    }
  };

  const getSelectedRestaurantData = () => {
    return restaurants.find(r => r.name === selectedRestaurant);
  };

  const getAllMenuItems = () => {
    const restaurantData = getSelectedRestaurantData();
    if (restaurantData) {
      // Combine built-in restaurant menu with custom additions
      const builtInItems = restaurantData?.menu || [];
      const customAdditions = restaurantCustomItems[selectedRestaurant] || [];
      return [...builtInItems, ...customAdditions];
    } else if (selectedRestaurant === 'Custom Restaurant') {
      return customMenuItems;
    }
    return [];
  };

  const canAddQuantity = (category, isCourseItem = false) => {
    // For course-based restaurants, course items (Starter/Main/Dessert) cannot have quantity > 1
    // Non-course items (Drink/Other) or non-course-based restaurants allow quantity adjustments
    const restaurantData = getSelectedRestaurantData();
    const isCourseBasedRestaurant = restaurantData && restaurantData.pricing_model === 'course_based';
    
    if (isCourseBasedRestaurant && isCourseItem) {
      // Course items in course-based restaurants: only Drink allows quantity > 1
      return category === 'Drink';
    } else {
      // Regular restaurants or non-course items: Drink and Other allow quantities
      return category === 'Drink' || category === 'Other';
    }
  };

  const getFriendCoursePricingBreakdown = (friendName) => {
    const friendOrders = orders[friendName] || [];
    const restaurantData = getSelectedRestaurantData();
    
    if (!restaurantData || restaurantData.pricing_model !== 'course_based') {
      return null;
    }
    
    const courseItems = [];
    const nonCourseItems = [];
    
    friendOrders.forEach(orderItem => {
      const menuItem = restaurantData?.menu?.find(m => m.name === orderItem.name);
      if (menuItem && menuItem.is_course_item) {
        if (!courseItems.some(ci => ci.category === menuItem.category)) {
          courseItems.push({
            name: menuItem.name,
            category: menuItem.category,
            surcharge: menuItem.price || 0
          });
        }
      } else {
        nonCourseItems.push({
          name: orderItem.name,
          cost: orderItem.cost,
          quantity: orderItem.quantity
        });
      }
    });
    
    const courseCount = courseItems.length;
    let basePrice = 0;
    
    if (courseCount === 1) {
      basePrice = restaurantData.course_pricing['1_course'] || 0;
    } else if (courseCount === 2) {
      basePrice = restaurantData.course_pricing['2_course'] || 0;
    } else if (courseCount >= 3) {
      basePrice = restaurantData.course_pricing['3_course'] || 0;
    }
    
    const surcharges = courseItems.reduce((sum, item) => sum + item.surcharge, 0);
    
    return {
      courseCount,
      basePrice,
      surcharges,
      courseItems,
      nonCourseItems
    };
  };

  const generateEmailBillSummary = () => {
    const totalCost = calculateTotalCost();
    const currentRestaurantName = sanitizeTextInput(restaurantName || selectedRestaurant);
    const currentDate = new Date().toLocaleDateString('da-DK');
    
    let emailBody = `Restaurant Bill Split - ${sanitizeTextInput(partyName || currentRestaurantName)}\n`;
    emailBody += `Date: ${currentDate}\n`;
    emailBody += `Restaurant: ${currentRestaurantName}\n\n`;
    
    // Add individual totals
    friends.forEach(friend => {
      const friendTotal = calculateFriendTotal(friend);
      if (friendTotal > 0) {
        emailBody += `${sanitizeTextInput(friend)} - ${friendTotal.toFixed(2)} kr\n`;
      }
    });
    
    emailBody += `\nTotal: ${totalCost.toFixed(2)} kr\n`;
    
    return emailBody;
  };

  const handleEmailBills = () => {
    const emailBody = generateEmailBillSummary();
    const subject = `Restaurant Bill Split - ${sanitizeTextInput(partyName || restaurantName || selectedRestaurant)}`;
    
    const mailtoUrl = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(emailBody)}`;
    window.open(mailtoUrl);
  };

  const renderStartPage = () => {
    const savedParties = loadSavedParties();
    
    return (
      <div className="card">
        <h2>🧾 Restaurant Bill Splitter</h2>
        <p>Choose an option to get started:</p>
        
        <div style={{marginBottom: '20px'}}>
          <button className="btn btn-success" onClick={startNewParty} style={{marginRight: '10px'}}>
            Create New Party
          </button>
        </div>

        {savedParties.length > 0 && (
          <div>
            <h3>Load Existing Party</h3>
            <div className="item-list">
              {savedParties.map(party => (
                <div key={party.id} className="item">
                  <div>
                    <strong>{party.name}</strong>
                    <div style={{fontSize: '14px', color: '#666'}}>
                      {party.restaurant_name || party.selected_restaurant} - 
                      {party.total_cost.toFixed(2)} kr - 
                      {new Date(party.last_updated).toLocaleDateString()}
                    </div>
                  </div>
                  <button 
                    className="btn btn-success"
                    onClick={() => loadParty(party)}
                    style={{float: 'right'}}
                  >
                    Load Party
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderPartySetup = () => (
    <div className="card">
      <h2>🎉 Create New Party</h2>
      <div className="form-group">
        <label>Party Name:</label>
        <input
          type="text"
          className="form-control"
          value={partyName}
          onChange={(e) => setPartyName(sanitizeTextInput(e.target.value))}
          placeholder="Enter party name"
          maxLength="100"
        />
      </div>
      
      <div className="form-group">
        <label>Select Restaurant:</label>
        <select
          value={selectedRestaurant}
          onChange={(e) => {
            setSelectedRestaurant(e.target.value);
            if (e.target.value !== 'Custom Restaurant') {
              setRestaurantName(e.target.value);
            }
            setCustomMenuItems([]);
            setOrders({});
            // Clear any editing state when changing restaurants
            cancelEdit();
          }}
        >
          <option value="Custom Restaurant">Create Custom Restaurant</option>
          {restaurants.map(restaurant => (
            <option key={restaurant.name} value={restaurant.name}>
              {restaurant.name} - {restaurant.cuisine}
            </option>
          ))}
        </select>
      </div>

      {selectedRestaurant === 'Custom Restaurant' && (
        <div className="form-group">
          <label>Restaurant Name:</label>
          <input
            type="text"
            className="form-control"
            value={restaurantName}
            onChange={(e) => setRestaurantName(sanitizeTextInput(e.target.value))}
            placeholder="Enter restaurant name"
            maxLength="100"
          />
        </div>
      )}

      {partyName && (restaurantName || selectedRestaurant !== 'Custom Restaurant') && (
        <button className="btn" onClick={() => setCurrentStep('friends')}>
          Continue to Add Friends
        </button>
      )}
    </div>
  );

  const renderFriendsSection = () => (
    <div className="card">
      <h2>👥 Add Friends</h2>
      <div className="row">
        <div className="col">
          <input
            type="text"
            className="form-control"
            value={newFriendName}
            onChange={(e) => setNewFriendName(sanitizeTextInput(e.target.value))}
            placeholder="Enter friend name"
            maxLength="100"
            onKeyPress={(e) => e.key === 'Enter' && addFriend()}
          />
        </div>
        <div className="col">
          <button className="btn" onClick={addFriend}>Add Friend</button>
        </div>
      </div>

      {friends.length > 0 && (
        <div className="item-list">
          {friends.map((friend, index) => (
            <div key={index} className="item">
              <div>
                <strong>{friend}</strong>
                <div style={{fontSize: '14px', color: '#666'}}>
                  Total: {calculateFriendTotal(friend).toFixed(2)} kr 
                  ({(orders[friend] || []).reduce((sum, item) => sum + item.quantity, 0)} items)
                </div>
              </div>
              <button 
                className="btn btn-secondary" 
                onClick={() => removeFriend(friend)}
                style={{float: 'right'}}
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}

      {friends.length > 0 && (
        <>
          <button className="btn" onClick={() => setCurrentStep('menu')}>
            {selectedRestaurant === 'Custom Restaurant' ? 'Continue to Create Menu' : 'Continue to Manage Menu'}
          </button>
          {selectedRestaurant !== 'Custom Restaurant' && (
            <button className="btn btn-secondary" onClick={() => setCurrentStep('orders')}>
              Skip to Orders
            </button>
          )}
        </>
      )}
    </div>
  );

  const renderMenuSection = () => {
    const restaurantData = getSelectedRestaurantData();
    const isCustomRestaurant = selectedRestaurant === 'Custom Restaurant';
    const builtInItems = restaurantData ? restaurantData.menu || [] : [];
    const customItems = isCustomRestaurant ? customMenuItems : (restaurantCustomItems[selectedRestaurant] || []);
    const allMenuItems = isCustomRestaurant ? customItems : [...builtInItems, ...customItems];
    
    return (
      <div className="card">
        <h2>📋 {isCustomRestaurant ? 'Create Menu for' : 'Manage Menu for'} {restaurantName}</h2>
        
        {!isCustomRestaurant && builtInItems.length > 0 && (
          <div style={{marginBottom: '20px'}}>
            <h3>Built-in Menu Items ({builtInItems.length})</h3>
            <div className="item-list">
              {builtInItems.map((item, index) => (
                <div key={`builtin-${index}`} className="item">
                  <div>
                    <strong>{item.name}</strong> - {item.price.toFixed(2)} kr
                    <div style={{fontSize: '14px', color: '#666'}}>
                      {item.category}
                      {item.is_course_item && ' (Course Item)'}
                    </div>
                  </div>
                  <div style={{float: 'right', fontSize: '12px', color: '#888', padding: '5px 8px'}}>
                    Built-in
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        <div className="form-group">
          <h3>{isEditMode ? 'Edit Menu Item' : `Add ${isCustomRestaurant ? '' : 'Custom'} Menu Item`}</h3>
          <div className="row">
            <div className="col">
              <input
                type="text"
                className="form-control"
                value={newItemName}
                onChange={(e) => setNewItemName(sanitizeTextInput(e.target.value))}
                placeholder="Item name"
                maxLength="100"
              />
            </div>
            <div className="col">
              <input
                type="number"
                step="0.01"
                min="0"
                max="99999.99"
                className="form-control"
                value={newItemPrice}
                onChange={(e) => {
                  const val = e.target.value;
                  // Only allow valid number input
                  if (val === '' || /^\d*\.?\d{0,2}$/.test(val)) {
                    setNewItemPrice(val);
                  }
                }}
                placeholder="Price"
              />
            </div>
            <div className="col">
              <select
                value={newItemCategory}
                onChange={(e) => setNewItemCategory(e.target.value)}
                className="form-control"
              >
                <option value="Starter">Starter</option>
                <option value="Main">Main</option>
                <option value="Dessert">Dessert</option>
                <option value="Drink">Drink</option>
                <option value="Other">Other</option>
                <option value="Table">Table (Shared)</option>
              </select>
            </div>
            <div className="col">
              {isEditMode ? (
                <>
                  <button className="btn btn-success" onClick={saveEditedItem} style={{marginRight: '5px'}}>
                    Save
                  </button>
                  <button className="btn btn-secondary" onClick={cancelEdit}>
                    Cancel
                  </button>
                </>
              ) : (
                <button 
                  className="btn" 
                  onClick={isCustomRestaurant ? addCustomMenuItem : addCustomItemToRestaurant}
                >
                  Add Item
                </button>
              )}
            </div>
          </div>
        </div>

        {customItems.length > 0 && (
          <div>
            <h3>{isCustomRestaurant ? 'Menu Items' : 'Custom Menu Items'} ({customItems.length})</h3>
            <div className="item-list">
              {customItems.map((item, index) => (
                <div key={isCustomRestaurant ? `custom-${index}` : `restaurant-custom-${item.id}`} className="item">
                  <div>
                    <strong>{item.name}</strong> - {item.price.toFixed(2)} kr
                    <div style={{fontSize: '14px', color: '#666'}}>
                      {item.category}
                      {item.is_course_item && ' (Course Item)'}
                      {!isCustomRestaurant && ' (Custom)'}
                    </div>
                  </div>
                  <div style={{float: 'right'}}>
                    {!isCustomRestaurant && (
                      <button 
                        className="btn btn-primary"
                        onClick={() => editCustomItem(item)}
                        style={{fontSize: '12px', padding: '2px 6px', marginRight: '5px'}}
                      >
                        Edit
                      </button>
                    )}
                    <button 
                      className="btn btn-secondary"
                      onClick={() => isCustomRestaurant ? removeCustomMenuItem(index) : removeCustomItemFromRestaurant(item.id)}
                      style={{fontSize: '12px', padding: '2px 6px'}}
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {allMenuItems.length > 0 && (
          <button className="btn" onClick={() => setCurrentStep('orders')}>
            Continue to Orders
          </button>
        )}
      </div>
    );
  };

  const renderOrdersSection = () => {
    const allItems = getAllMenuItems();
    const menuItems = allItems.filter(item => item.category !== 'Table'); // Filter out Table items for individual orders
    const tableItems = allItems.filter(item => item.category === 'Table'); // Table items only
    const restaurantData = getSelectedRestaurantData();
    const isCourseBasedRestaurant = restaurantData && restaurantData.pricing_model === 'course_based';
    
    return (
      <div className="card">
        <h2>🍽️ Order Management</h2>
        <h3>{restaurantName || selectedRestaurant}</h3>
        
        {isCourseBasedRestaurant && (
          <div className="alert alert-info">
            <strong>Course Pricing:</strong> 1 course: {restaurantData.course_pricing['1_course']} kr, 
            2 courses: {restaurantData.course_pricing['2_course']} kr, 
            3 courses: {restaurantData.course_pricing['3_course']} kr 
            (+ any surcharges). Drinks charged separately.
          </div>
        )}
        
        {friends.length === 0 && (
          <div className="alert alert-warning">
            Please add friends first before creating orders.
          </div>
        )}

        {menuItems.length === 0 && selectedRestaurant === 'Custom Restaurant' && (
          <div className="alert alert-warning">
            Please add menu items first before creating orders.
          </div>
        )}

        {friends.length > 0 && menuItems.length > 0 && (
          <div>
            {friends.map(friend => (
              <div key={friend} className="friend-section">
                <h4>{friend} - {calculateFriendTotal(friend).toFixed(2)} kr</h4>
                
                <div style={{marginBottom: '15px'}}>
                  <label>Add Item:</label>
                  <select
                    onChange={(e) => {
                      const selectedValue = e.target.value;
                      if (selectedValue) {
                        const selectedItem = menuItems.find(item => item.name === selectedValue);
                        if (selectedItem && selectedValue === selectedItem.name) {
                          addItemToFriendOrder(friend, selectedItem);
                        }
                        e.target.value = '';
                      }
                    }}
                    className="form-control"
                    defaultValue=""
                  >
                    <option value="">Select an item...</option>
                    {menuItems.map((item, index) => (
                      <option key={index} value={item.name}>
                        {item.name} - {item.price.toFixed(2)} kr ({item.category})
                      </option>
                    ))}
                  </select>
                </div>

                {orders[friend] && orders[friend].length > 0 && (
                  <div>
                    <h5>Current Order:</h5>
                    <div className="item-list">
                      {orders[friend].map((orderItem) => (
                        <div key={orderItem.id} className="item">
                          <div>
                            <strong>{orderItem.name}</strong> - {orderItem.cost.toFixed(2)} kr each
                            <div style={{fontSize: '14px', color: '#666'}}>
                              {orderItem.category} • Total: {(orderItem.cost * orderItem.quantity).toFixed(2)} kr
                            </div>
                          </div>
                          <div style={{float: 'right', display: 'flex', alignItems: 'center', gap: '5px'}}>
                            {canAddQuantity(orderItem.category, orderItem.is_course_item) && (
                              <div className="quantity-control">
                                <button 
                                  className="quantity-btn"
                                  onClick={() => updateItemQuantity(friend, orderItem.id, orderItem.quantity - 1)}
                                >
                                  -
                                </button>
                                <span className="quantity-display">{orderItem.quantity}</span>
                                <button 
                                  className="quantity-btn"
                                  onClick={() => updateItemQuantity(friend, orderItem.id, orderItem.quantity + 1)}
                                >
                                  +
                                </button>
                              </div>
                            )}
                            <button 
                              className="btn btn-secondary"
                              onClick={() => removeItemFromFriendOrder(friend, orderItem.id)}
                              style={{fontSize: '12px', padding: '2px 6px'}}
                            >
                              Remove
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {(!orders[friend] || orders[friend].length === 0) && (
                  <p style={{color: '#666', fontStyle: 'italic'}}>No items ordered yet</p>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Table Orders Section */}
        {tableItems.length > 0 && (
          <div style={{marginTop: '30px', marginBottom: '20px'}}>
            <h3>🍻 Table Orders (Shared Items)</h3>
            <p style={{color: '#666', fontSize: '14px', marginBottom: '15px'}}>
              These items will be split equally among all party members.
            </p>
            
            <div style={{marginBottom: '15px'}}>
              <label>Add Table Item:</label>
              <select
                onChange={(e) => {
                  const selectedValue = e.target.value;
                  if (selectedValue) {
                    const selectedItem = tableItems.find(item => item.name === selectedValue);
                    if (selectedItem && selectedValue === selectedItem.name) {
                      addItemToTableOrders(selectedItem);
                    }
                    e.target.value = '';
                  }
                }}
                className="form-control"
                defaultValue=""
              >
                <option value="">Select a table item...</option>
                {tableItems.map((item, index) => (
                  <option key={index} value={item.name}>
                    {item.name} - {item.price.toFixed(2)} kr ({item.category})
                  </option>
                ))}
              </select>
            </div>

            {tableOrders.length > 0 && (
              <div>
                <h5>Current Table Orders:</h5>
                <div className="item-list">
                  {tableOrders.map((orderItem) => (
                    <div key={orderItem.id} className="item">
                      <div>
                        <strong>{orderItem.name}</strong> - {orderItem.cost.toFixed(2)} kr each
                        <div style={{fontSize: '14px', color: '#666'}}>
                          {orderItem.category} • Total: {(orderItem.cost * orderItem.quantity).toFixed(2)} kr 
                          • Split: {friends.length > 0 ? ((orderItem.cost * orderItem.quantity) / friends.length).toFixed(2) : '0.00'} kr per person
                        </div>
                      </div>
                      <div style={{float: 'right', display: 'flex', alignItems: 'center', gap: '5px'}}>
                        <div className="quantity-control">
                          <button 
                            className="quantity-btn"
                            onClick={() => updateTableItemQuantity(orderItem.id, orderItem.quantity - 1)}
                          >
                            -
                          </button>
                          <span className="quantity-display">{orderItem.quantity}</span>
                          <button 
                            className="quantity-btn"
                            onClick={() => updateTableItemQuantity(orderItem.id, orderItem.quantity + 1)}
                          >
                            +
                          </button>
                        </div>
                        <button 
                          className="btn btn-secondary"
                          onClick={() => removeTableItem(orderItem.id)}
                          style={{fontSize: '12px', padding: '2px 6px'}}
                        >
                          Remove
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {tableOrders.length === 0 && (
              <p style={{color: '#666', fontStyle: 'italic'}}>No table items ordered yet</p>
            )}
          </div>
        )}

        <button className="btn" onClick={() => setCurrentStep('calculation')}>
          Calculate Bills
        </button>
      </div>
    );
  };

  const renderCalculation = () => (
    <div className="card">
      <h2>💰 Bill Calculation</h2>
      
      <div className="row" style={{marginBottom: '20px'}}>
        <div className="col">
          <div className="metric">
            <div className="metric-value">{calculateTotalCost().toFixed(2)} kr</div>
            <div className="metric-label">Total Bill</div>
          </div>
        </div>
        <div className="col">
          <div className="metric">
            <div className="metric-value">{friends.length}</div>
            <div className="metric-label">Friends</div>
          </div>
        </div>
        <div className="col">
          <div className="metric">
            <div className="metric-value">{getTotalItems()}</div>
            <div className="metric-label">Items</div>
          </div>
        </div>
      </div>

      {friends.length > 0 && (
        <div>
          <h3>Quick Summary</h3>
          <div style={{marginBottom: '20px'}}>
            {friends.map(friend => {
              const friendTotal = calculateFriendTotal(friend);
              return friendTotal > 0 ? (
                <div key={friend} style={{display: 'flex', justifyContent: 'space-between', padding: '5px 0', borderBottom: '1px solid #eee'}}>
                  <span><strong>{friend}</strong></span>
                  <span><strong>{friendTotal.toFixed(2)} kr</strong></span>
                </div>
              ) : null;
            })}
          </div>

          {friends.length > 0 && calculateTotalCost() > 0 && (
            <div style={{marginBottom: '30px', textAlign: 'center'}}>
              <button className="btn btn-success" onClick={handleEmailBills}>
                📧 Email Bills
              </button>
            </div>
          )}

          <h3>Detailed Breakdown</h3>
          {friends.map(friend => {
            const friendTotal = calculateFriendTotal(friend);
            const friendItems = orders[friend] || [];
            const coursePricing = getFriendCoursePricingBreakdown(friend);
            
            return (
              <div key={friend} className="friend-section">
                <h4>{friend} - {friendTotal.toFixed(2)} kr</h4>
                {friendItems.length > 0 ? (
                  <div>
                    {coursePricing ? (
                      <div>
                        {coursePricing.courseCount > 0 && (
                          <div style={{marginBottom: '10px'}}>
                            <strong>Course Menu ({coursePricing.courseCount} course{coursePricing.courseCount > 1 ? 's' : ''}): {coursePricing.basePrice.toFixed(2)} kr</strong>
                            <div>
                              {coursePricing.courseItems.map((item, index) => (
                                <div key={index} style={{paddingLeft: '20px', marginBottom: '5px'}}>
                                  {item.name} ({item.category})
                                  {item.surcharge > 0 && <span> + {item.surcharge.toFixed(2)} kr surcharge</span>}
                                </div>
                              ))}
                            </div>
                            {coursePricing.surcharges > 0 && (
                              <div><strong>Total surcharges: {coursePricing.surcharges.toFixed(2)} kr</strong></div>
                            )}
                          </div>
                        )}
                        {coursePricing.nonCourseItems.length > 0 && (
                          <div>
                            <strong>Additional Items:</strong>
                            <div>
                              {coursePricing.nonCourseItems.map((item, index) => (
                                <div key={index} style={{paddingLeft: '20px', marginBottom: '5px'}}>
                                  {item.name} {item.quantity > 1 ? `× ${item.quantity}` : ''} - {(item.cost * item.quantity).toFixed(2)} kr
                                  {item.quantity > 1 && <span style={{color: '#666'}}> ({item.cost.toFixed(2)} kr each)</span>}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div>
                        {friendItems.map((item) => (
                          <div key={item.id} style={{paddingLeft: '20px', marginBottom: '5px'}}>
                            {item.name} {item.quantity > 1 ? `× ${item.quantity}` : ''} - {(item.cost * item.quantity).toFixed(2)} kr
                            {item.quantity > 1 && <span style={{color: '#666'}}> ({item.cost.toFixed(2)} kr each)</span>}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  <p style={{color: '#666', fontStyle: 'italic'}}>No items ordered</p>
                )}
                
                {/* Show table share for each friend */}
                {tableOrders.length > 0 && (
                  <div style={{marginTop: '10px'}}>
                    <strong>Table Items Share: {calculateTableCostPerFriend().toFixed(2)} kr</strong>
                    <div style={{fontSize: '14px', color: '#666', paddingLeft: '20px'}}>
                      {tableOrders.map((item) => (
                        <div key={item.id} style={{marginBottom: '2px'}}>
                          {item.name} {item.quantity > 1 ? `× ${item.quantity}` : ''} - {friends.length > 0 ? ((item.cost * item.quantity) / friends.length).toFixed(2) : '0.00'} kr
                          <span style={{color: '#888'}}> (shared)</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );

  return (
    <div className="container">
      <h1>🧾 Restaurant Bill Splitter</h1>
      
      {showAlert && (
        <div className={`alert alert-${alertType}`}>
          {showAlert}
        </div>
      )}

      {currentStep !== 'start' && (
        <div style={{marginBottom: '20px'}}>
          <button className="btn" onClick={() => setCurrentStep('start')}>Home</button>
          {partyName && <button className="btn" onClick={() => setCurrentStep('party')}>Party Setup</button>}
          {friends.length > 0 && <button className="btn" onClick={() => setCurrentStep('friends')}>Friends</button>}
          <button className="btn" onClick={() => setCurrentStep('menu')}>Menu</button>
          {((selectedRestaurant !== 'Custom Restaurant') || customMenuItems.length > 0) && friends.length > 0 && (
            <button className="btn" onClick={() => setCurrentStep('orders')}>Orders</button>
          )}
          <button className="btn" onClick={() => setCurrentStep('calculation')}>Calculate</button>
          <button className="btn btn-success" onClick={saveCurrentParty}>Save Party</button>
          <button className="btn btn-secondary" onClick={resetParty}>Reset All</button>
        </div>
      )}

      {currentStep === 'start' && renderStartPage()}
      {currentStep === 'party' && renderPartySetup()}
      {currentStep === 'friends' && renderFriendsSection()}
      {currentStep === 'menu' && renderMenuSection()}
      {currentStep === 'orders' && renderOrdersSection()}
      {currentStep === 'calculation' && renderCalculation()}
    </div>
  );
}

export default App;