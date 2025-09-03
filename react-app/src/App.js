import React, { useState, useEffect } from 'react';

function App() {
  const [restaurants, setRestaurants] = useState([]);
  const [currentPartyId, setCurrentPartyId] = useState('');
  const [partyName, setPartyName] = useState('');
  const [selectedRestaurant, setSelectedRestaurant] = useState('Custom Restaurant');
  const [restaurantName, setRestaurantName] = useState('');
  const [customMenuItems, setCustomMenuItems] = useState([]); // For custom restaurants
  const [friends, setFriends] = useState([]);
  const [orders, setOrders] = useState({}); // {friendName: [{id, name, cost, quantity, category}, ...]}
  const [newFriendName, setNewFriendName] = useState('');
  const [showAlert, setShowAlert] = useState('');
  const [alertType, setAlertType] = useState('');
  const [currentStep, setCurrentStep] = useState('start');
  const [newItemName, setNewItemName] = useState('');
  const [newItemPrice, setNewItemPrice] = useState('');
  const [newItemCategory, setNewItemCategory] = useState('Other');

  useEffect(() => {
    loadRestaurants();
    generatePartyId();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const loadRestaurants = async () => {
    try {
      const response = await fetch('./restaurants.json');
      const data = await response.json();
      setRestaurants(data.restaurants || []);
    } catch (error) {
      showMessage('Error loading restaurants data', 'danger');
    }
  };

  const generatePartyId = () => {
    const id = Date.now().toString(36) + Math.random().toString(36).substr(2);
    setCurrentPartyId(id);
  };

  const showMessage = (message, type = 'info') => {
    setShowAlert(message);
    setAlertType(type);
    setTimeout(() => setShowAlert(''), 3000);
  };

  const saveCurrentParty = () => {
    if (!currentPartyId || !partyName.trim()) {
      showMessage('Party name is required to save', 'warning');
      return;
    }

    const partyData = {
      id: currentPartyId,
      name: partyName,
      restaurant_name: restaurantName,
      selected_restaurant: selectedRestaurant,
      custom_menu_items: customMenuItems,
      created: new Date().toISOString(),
      last_updated: new Date().toISOString(),
      friends: friends,
      orders: orders,
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
      return savedParties;
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
    setFriends(partyData.friends || []);
    setOrders(partyData.orders || {});
    setCurrentStep('orders');
    showMessage('Party loaded successfully!', 'success');
  };

  const startNewParty = () => {
    setCurrentStep('party');
  };

  const addFriend = () => {
    if (!newFriendName.trim()) {
      showMessage('Please enter a friend name', 'warning');
      return;
    }
    if (friends.includes(newFriendName.trim())) {
      showMessage('Friend already exists', 'warning');
      return;
    }
    setFriends([...friends, newFriendName.trim()]);
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
    if (!newItemName.trim()) {
      showMessage('Please enter item name', 'warning');
      return;
    }
    const price = parseFloat(newItemPrice);
    if (isNaN(price) || price <= 0) {
      showMessage('Please enter a valid price', 'warning');
      return;
    }

    const newItem = {
      name: newItemName.trim(),
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

  const addItemToFriendOrder = (friendName, menuItem) => {
    const newOrders = { ...orders };
    if (!newOrders[friendName]) {
      newOrders[friendName] = [];
    }

    // Check if friend already has this item
    const existingOrderItem = newOrders[friendName].find(item => 
      item.name === menuItem.name
    );

    if (existingOrderItem) {
      // Increment quantity
      existingOrderItem.quantity += 1;
    } else {
      // Add new item
      const orderItem = {
        id: Date.now().toString() + Math.random().toString(36).substr(2),
        name: menuItem.name,
        cost: menuItem.price,
        quantity: 1,
        category: menuItem.category
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

  const calculateTotalCost = () => {
    return Object.values(orders).flat().reduce((total, item) => 
      total + (item.cost * item.quantity), 0
    );
  };

  const calculateFriendTotal = (friendName) => {
    const friendOrders = orders[friendName] || [];
    return friendOrders.reduce((total, item) => total + (item.cost * item.quantity), 0);
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
      setFriends([]);
      setOrders({});
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
      return restaurantData.menu;
    } else if (selectedRestaurant === 'Custom Restaurant') {
      return customMenuItems;
    }
    return [];
  };

  const canAddQuantity = (category) => {
    return category === 'Drink' || category === 'Other';
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
                      ${party.total_cost.toFixed(2)} - 
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
          onChange={(e) => setPartyName(e.target.value)}
          placeholder="Enter party name"
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
            onChange={(e) => setRestaurantName(e.target.value)}
            placeholder="Enter restaurant name"
          />
        </div>
      )}

      {partyName.trim() && (restaurantName.trim() || selectedRestaurant !== 'Custom Restaurant') && (
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
            onChange={(e) => setNewFriendName(e.target.value)}
            placeholder="Enter friend name"
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
                  Total: ${calculateFriendTotal(friend).toFixed(2)} 
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
        <button className="btn" onClick={() => {
          if (selectedRestaurant === 'Custom Restaurant') {
            setCurrentStep('menu');
          } else {
            setCurrentStep('orders');
          }
        }}>
          {selectedRestaurant === 'Custom Restaurant' ? 'Continue to Create Menu' : 'Continue to Orders'}
        </button>
      )}
    </div>
  );

  const renderMenuSection = () => (
    <div className="card">
      <h2>📋 Create Menu for {restaurantName}</h2>
      
      <div className="form-group">
        <h3>Add Menu Item</h3>
        <div className="row">
          <div className="col">
            <input
              type="text"
              className="form-control"
              value={newItemName}
              onChange={(e) => setNewItemName(e.target.value)}
              placeholder="Item name"
            />
          </div>
          <div className="col">
            <input
              type="number"
              step="0.01"
              min="0"
              className="form-control"
              value={newItemPrice}
              onChange={(e) => setNewItemPrice(e.target.value)}
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
            </select>
          </div>
          <div className="col">
            <button className="btn" onClick={addCustomMenuItem}>Add Item</button>
          </div>
        </div>
      </div>

      {customMenuItems.length > 0 && (
        <div>
          <h3>Menu Items ({customMenuItems.length})</h3>
          <div className="item-list">
            {customMenuItems.map((item, index) => (
              <div key={index} className="item">
                <div>
                  <strong>{item.name}</strong> - ${item.price.toFixed(2)}
                  <div style={{fontSize: '14px', color: '#666'}}>{item.category}</div>
                </div>
                <button 
                  className="btn btn-secondary"
                  onClick={() => removeCustomMenuItem(index)}
                  style={{float: 'right', fontSize: '12px', padding: '5px 8px'}}
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {customMenuItems.length > 0 && (
        <button className="btn" onClick={() => setCurrentStep('orders')}>
          Continue to Orders
        </button>
      )}
    </div>
  );

  const renderOrdersSection = () => {
    const menuItems = getAllMenuItems();
    
    return (
      <div className="card">
        <h2>🍽️ Order Management</h2>
        <h3>{restaurantName || selectedRestaurant}</h3>
        
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
                <h4>{friend} - ${calculateFriendTotal(friend).toFixed(2)}</h4>
                
                <div style={{marginBottom: '15px'}}>
                  <label>Add Item:</label>
                  <select
                    onChange={(e) => {
                      if (e.target.value) {
                        const selectedItem = menuItems.find(item => item.name === e.target.value);
                        if (selectedItem) {
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
                        {item.name} - ${item.price.toFixed(2)} ({item.category})
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
                            <strong>{orderItem.name}</strong> - ${orderItem.cost.toFixed(2)} each
                            <div style={{fontSize: '14px', color: '#666'}}>
                              {orderItem.category} • Total: ${(orderItem.cost * orderItem.quantity).toFixed(2)}
                            </div>
                          </div>
                          <div style={{float: 'right', display: 'flex', alignItems: 'center', gap: '5px'}}>
                            {canAddQuantity(orderItem.category) && (
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
            <div className="metric-value">${calculateTotalCost().toFixed(2)}</div>
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
          <h3>Individual Bills</h3>
          {friends.map(friend => {
            const friendTotal = calculateFriendTotal(friend);
            const friendItems = orders[friend] || [];
            
            return (
              <div key={friend} className="friend-section">
                <h4>{friend} - ${friendTotal.toFixed(2)}</h4>
                {friendItems.length > 0 ? (
                  <ul>
                    {friendItems.map((item) => (
                      <li key={item.id}>
                        {item.name} {item.quantity > 1 ? `× ${item.quantity}` : ''} - ${(item.cost * item.quantity).toFixed(2)}
                        {item.quantity > 1 && <span style={{color: '#666'}}> (${item.cost.toFixed(2)} each)</span>}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p style={{color: '#666', fontStyle: 'italic'}}>No items ordered</p>
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
          {selectedRestaurant === 'Custom Restaurant' && customMenuItems.length > 0 && (
            <button className="btn" onClick={() => setCurrentStep('menu')}>Menu</button>
          )}
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