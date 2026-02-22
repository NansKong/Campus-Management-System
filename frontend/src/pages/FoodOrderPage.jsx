import React, { useCallback, useEffect, useMemo, useState } from 'react';
import MenuBrowse from '../components/Food/MenuBrowse';
import { useAuth } from '../context/AuthContext';
import aiService from '../services/aiService';
import authService from '../services/authService';
import foodService from '../services/foodService';
import { connectFoodRushSocket } from '../services/realtimeService';
import { getApiErrorMessage } from '../utils/errors';

const ORDER_TRANSITIONS = {
  pending: ['confirmed', 'cancelled'],
  confirmed: ['ready', 'cancelled'],
  ready: ['completed'],
  completed: [],
  cancelled: [],
};

const MENU_CATEGORIES = ['breakfast', 'lunch', 'snacks', 'beverages', 'other'];

function FoodOrderPage() {
  const { user } = useAuth();
  const role = user?.role;

  if (role === 'student') {
    return <StudentFoodFlow />;
  }

  if (role === 'vendor' || role === 'admin') {
    return <FoodCatalogManager role={role} />;
  }

  return <div className="p-6">You are not authorized to access food workflows.</div>;
}

function StudentFoodFlow() {
  const [cart, setCart] = useState([]);
  const [selectedSlot, setSelectedSlot] = useState('');
  const [slots, setSlots] = useState([]);
  const [myOrders, setMyOrders] = useState([]);
  const [rushPrediction, setRushPrediction] = useState(null);
  const [rushLiveTimestamp, setRushLiveTimestamp] = useState('');
  const [rushSocketState, setRushSocketState] = useState('connecting');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState({ type: '', message: '' });

  const rushBadge = useMemo(() => {
    if (!rushPrediction?.level) return { label: 'Unknown', color: 'text-gray-600' };
    if (rushPrediction.level === 'low') return { label: 'LOW RUSH', color: 'text-emerald-700', dot: '🟢' };
    if (rushPrediction.level === 'moderate') {
      return { label: 'MODERATE RUSH', color: 'text-yellow-700', dot: '🟡' };
    }
    return { label: 'HIGH RUSH', color: 'text-red-700', dot: '🔴' };
  }, [rushPrediction]);

  const loadStudentData = async () => {
    try {
      const [slotData, orderData, rushData] = await Promise.all([
        foodService.getSlots(),
        foodService.getMyOrders(),
        aiService.getFoodRush(),
      ]);
      setSlots(slotData);
      setMyOrders(orderData);
      setRushPrediction(rushData);
    } catch (error) {
      setStatus({
        type: 'error',
        message: getApiErrorMessage(error, 'Failed to load food data'),
      });
    }
  };

  useEffect(() => {
    loadStudentData();
    const timer = setInterval(loadStudentData, 45000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    let socket = null;
    let mounted = true;

    const connect = async () => {
      try {
        const token = await authService.getAuthToken();
        if (!mounted || !token) return;

        socket = connectFoodRushSocket({
          token,
          onMessage: (payload) => {
            if (!mounted || !payload || payload.error) return;
            setRushPrediction(payload);
            setRushLiveTimestamp(payload.timestamp || new Date().toISOString());
            setRushSocketState('live');
          },
          onError: () => {
            if (mounted) setRushSocketState('error');
          },
          onClose: () => {
            if (mounted) setRushSocketState('closed');
          },
        });
      } catch (error) {
        if (mounted) setRushSocketState('error');
      }
    };

    connect();

    return () => {
      mounted = false;
      if (socket && socket.readyState <= 1) {
        socket.close();
      }
    };
  }, []);

  const addToCart = (item) => {
    if (cart.length > 0 && cart[0].vendor_id !== item.vendor_id) {
      setStatus({
        type: 'error',
        message: 'Cart can contain items from a single vendor per order.',
      });
      return;
    }

    const existing = cart.find((entry) => entry.item_id === item.item_id);
    if (existing) {
      setCart(
        cart.map((entry) =>
          entry.item_id === item.item_id
            ? { ...entry, quantity: entry.quantity + 1 }
            : entry
        )
      );
    } else {
      setCart([...cart, { ...item, quantity: 1 }]);
    }
  };

  const updateQuantity = (itemId, quantity) => {
    if (quantity <= 0) {
      setCart(cart.filter((item) => item.item_id !== itemId));
      return;
    }
    setCart(
      cart.map((item) =>
        item.item_id === itemId ? { ...item, quantity } : item
      )
    );
  };

  const total = useMemo(
    () =>
      cart.reduce((sum, item) => sum + Number(item.price || 0) * item.quantity, 0),
    [cart]
  );

  const placeOrder = async () => {
    if (!cart.length) {
      setStatus({ type: 'error', message: 'Cart is empty.' });
      return;
    }
    if (!selectedSlot) {
      setStatus({ type: 'error', message: 'Select a break slot before placing order.' });
      return;
    }

    setLoading(true);
    try {
      await foodService.createOrder({
        vendor_id: cart[0].vendor_id,
        slot_id: selectedSlot,
        items: cart.map((item) => ({
          item_id: item.item_id,
          quantity: item.quantity,
        })),
      });
      setStatus({ type: 'success', message: 'Order placed successfully.' });
      setCart([]);
      setSelectedSlot('');
      await loadStudentData();
    } catch (error) {
      setStatus({
        type: 'error',
        message: getApiErrorMessage(error, 'Failed to place order'),
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
      <div className="xl:col-span-2">
        <MenuBrowse onAddToCart={addToCart} />
      </div>

      <div className="space-y-6">
        {rushPrediction && (
          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <h2 className="text-lg font-semibold">AI Rush Prediction</h2>
            <p className="mt-1 text-xs text-gray-500">
              Live feed: {rushSocketState}
              {rushLiveTimestamp ? ` | Updated ${new Date(rushLiveTimestamp).toLocaleTimeString()}` : ''}
            </p>
            <div className="mt-3 grid grid-cols-1 gap-3 text-sm">
              <div className="rounded-md border border-gray-200 p-3">
                Rush Level:{' '}
                <span className={`font-semibold ${rushBadge.color}`}>
                  {rushBadge.dot} {rushBadge.label}
                </span>
              </div>
              <div className="rounded-md border border-gray-200 p-3">
                Predicted wait: {rushPrediction.predicted_wait_minutes} minutes
              </div>
              <div className="rounded-md border border-gray-200 p-3">
                Recommended order time: {rushPrediction.recommended_order_time}
              </div>
              <div className="rounded-md border border-gray-200 p-3">
                Peak expected at: {rushPrediction.peak_expected_at}
              </div>
            </div>
          </div>
        )}

        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="text-xl font-semibold">Cart</h2>
          {status.message && (
            <div
              className={`mt-3 rounded-md px-3 py-2 text-sm ${
                status.type === 'error' ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'
              }`}
            >
              {status.message}
            </div>
          )}

          {cart.length === 0 ? (
            <p className="mt-3 text-sm text-gray-600">No items selected.</p>
          ) : (
            <div className="mt-4 space-y-3">
              {cart.map((item) => (
                <div key={item.item_id} className="rounded-md border border-gray-200 p-3">
                  <p className="font-medium">{item.item_name}</p>
                  <p className="text-sm text-gray-600">Price: {item.price}</p>
                  <div className="mt-2 flex items-center gap-2">
                    <button
                      type="button"
                      className="rounded border px-2 py-1"
                      onClick={() => updateQuantity(item.item_id, item.quantity - 1)}
                    >
                      -
                    </button>
                    <span className="text-sm">{item.quantity}</span>
                    <button
                      type="button"
                      className="rounded border px-2 py-1"
                      onClick={() => updateQuantity(item.item_id, item.quantity + 1)}
                    >
                      +
                    </button>
                  </div>
                </div>
              ))}

              <div className="rounded-md border border-gray-200 p-3">
                <label className="mb-2 block text-sm font-medium">Break Slot</label>
                <select
                  className="w-full rounded-md border px-3 py-2"
                  value={selectedSlot}
                  onChange={(event) => setSelectedSlot(event.target.value)}
                >
                  <option value="">Select slot</option>
                  {slots.map((slot) => (
                    <option key={slot.slot_id} value={slot.slot_id}>
                      {slot.slot_name || slot.slot_id} ({slot.start_time} - {slot.end_time})
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center justify-between text-sm font-semibold">
                <span>Total</span>
                <span>{total.toFixed(2)}</span>
              </div>

              <button
                type="button"
                className="w-full rounded-md bg-blue-600 px-4 py-2 text-sm text-white disabled:bg-blue-300"
                onClick={placeOrder}
                disabled={loading}
              >
                {loading ? 'Placing...' : 'Place Order'}
              </button>
            </div>
          )}
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="text-lg font-semibold">My Orders</h2>
          {myOrders.length === 0 ? (
            <p className="mt-3 text-sm text-gray-600">No orders yet.</p>
          ) : (
            <div className="mt-3 space-y-2 text-sm">
              {myOrders.map((order) => (
                <div key={order.order_id} className="rounded-md border border-gray-200 p-3">
                  <p className="font-medium">Order {order.order_id.slice(0, 8)}</p>
                  <p>Status: {order.status}</p>
                  <p>Pickup code: {order.pickup_code || '-'}</p>
                  <p>Total: {order.total_amount}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function FoodCatalogManager({ role }) {
  const isVendor = role === 'vendor';
  const [items, setItems] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [rushPrediction, setRushPrediction] = useState(null);
  const [rushLiveTimestamp, setRushLiveTimestamp] = useState('');
  const [rushSocketState, setRushSocketState] = useState('connecting');
  const [status, setStatus] = useState({ type: '', message: '' });
  const [form, setForm] = useState({
    vendor_id: '',
    item_name: '',
    description: '',
    price: '',
    category: 'lunch',
    preparation_time: '',
    is_available: true,
  });

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [catalogItems, vendorOrders] = await Promise.all([
        foodService.listCatalogItems({ include_unavailable: true }),
        isVendor ? foodService.getVendorOrders() : Promise.resolve([]),
      ]);
      setItems(catalogItems);
      setOrders(vendorOrders);
      if (isVendor) {
        try {
          const prediction = await aiService.getFoodRush();
          setRushPrediction(prediction);
        } catch (predictionError) {
          console.warn('Food rush prediction unavailable:', predictionError);
        }
      }
      setStatus({ type: '', message: '' });
    } catch (error) {
      setStatus({
        type: 'error',
        message: getApiErrorMessage(error, 'Failed to load food catalog'),
      });
    } finally {
      setLoading(false);
    }
  }, [isVendor]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    if (!isVendor) return () => {};

    let socket = null;
    let mounted = true;

    const connect = async () => {
      try {
        const token = await authService.getAuthToken();
        if (!mounted || !token) return;

        socket = connectFoodRushSocket({
          token,
          onMessage: (payload) => {
            if (!mounted || !payload || payload.error) return;
            setRushPrediction(payload);
            setRushLiveTimestamp(payload.timestamp || new Date().toISOString());
            setRushSocketState('live');
          },
          onError: () => {
            if (mounted) setRushSocketState('error');
          },
          onClose: () => {
            if (mounted) setRushSocketState('closed');
          },
        });
      } catch (error) {
        if (mounted) setRushSocketState('error');
      }
    };

    connect();

    return () => {
      mounted = false;
      if (socket && socket.readyState <= 1) {
        socket.close();
      }
    };
  }, [isVendor]);

  const handleFormChange = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const createItem = async (event) => {
    event.preventDefault();

    const payload = {
      item_name: form.item_name,
      description: form.description || null,
      price: Number(form.price),
      category: form.category,
      is_available: form.is_available,
      preparation_time: form.preparation_time ? Number(form.preparation_time) : null,
    };

    if (!isVendor) {
      payload.vendor_id = form.vendor_id;
    }

    try {
      await foodService.createCatalogItem(payload);
      setStatus({ type: 'success', message: 'Catalog item created.' });
      setForm({
        vendor_id: '',
        item_name: '',
        description: '',
        price: '',
        category: 'lunch',
        preparation_time: '',
        is_available: true,
      });
      await loadData();
    } catch (error) {
      setStatus({
        type: 'error',
        message: getApiErrorMessage(error, 'Failed to create catalog item'),
      });
    }
  };

  const toggleAvailability = async (item) => {
    try {
      await foodService.updateCatalogItem(item.item_id, {
        is_available: !item.is_available,
      });
      await loadData();
    } catch (error) {
      setStatus({
        type: 'error',
        message: getApiErrorMessage(error, 'Failed to update availability'),
      });
    }
  };

  const progressOrder = async (orderId, nextStatus) => {
    try {
      await foodService.updateOrderStatus(orderId, nextStatus);
      await loadData();
    } catch (error) {
      setStatus({
        type: 'error',
        message: getApiErrorMessage(error, 'Failed to update order status'),
      });
    }
  };

  return (
    <div className="space-y-6">
      {isVendor && rushPrediction && (
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="text-lg font-semibold">AI Demand Forecast</h2>
          <p className="mt-1 text-xs text-gray-500">
            Live feed: {rushSocketState}
            {rushLiveTimestamp ? ` | Updated ${new Date(rushLiveTimestamp).toLocaleTimeString()}` : ''}
          </p>
          <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-4 text-sm">
            <div className="rounded-md border border-gray-200 p-3">
              Predicted Next 1 Hour: {rushPrediction.next_hour_demand}
            </div>
            <div className="rounded-md border border-gray-200 p-3">
              Peak Window: {rushPrediction.expected_peak_window}
            </div>
            <div className="rounded-md border border-gray-200 p-3">
              Suggested Prep Qty: {rushPrediction.suggested_prep_quantity}
            </div>
            <div className="rounded-md border border-gray-200 p-3">
              Active Orders: {rushPrediction.active_orders}
            </div>
          </div>
          {Array.isArray(rushPrediction.order_load_graph) && rushPrediction.order_load_graph.length > 0 && (
            <div className="mt-4">
              <h3 className="mb-2 text-sm font-semibold text-gray-700">Order Load Graph</h3>
              <div className="space-y-2">
                {rushPrediction.order_load_graph.map((point) => (
                  <div key={point.hour} className="flex items-center gap-2 text-xs">
                    <span className="w-12">{point.hour}</span>
                    <div className="h-2 flex-1 rounded bg-gray-200">
                      <div
                        className="h-2 rounded bg-emerald-500"
                        style={{ width: `${Math.min(100, point.orders * 8)}%` }}
                      />
                    </div>
                    <span className="w-8 text-right">{point.orders}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <h1 className="text-2xl font-semibold">Food Catalog Management</h1>
        <p className="mt-1 text-sm text-gray-600">
          {isVendor
            ? 'Manage your menu and update live order statuses.'
            : 'Manage vendor catalog items across the campus food system.'}
        </p>
        {status.message && (
          <div
            className={`mt-3 rounded-md px-3 py-2 text-sm ${
              status.type === 'error' ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'
            }`}
          >
            {status.message}
          </div>
        )}
      </div>

      <form className="rounded-xl border border-gray-200 bg-white p-6" onSubmit={createItem}>
        <h2 className="text-lg font-semibold">Create Catalog Item</h2>
        <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
          {!isVendor && (
            <input
              className="rounded-md border px-3 py-2"
              placeholder="Vendor UUID"
              value={form.vendor_id}
              onChange={(event) => handleFormChange('vendor_id', event.target.value)}
              required
            />
          )}
          <input
            className="rounded-md border px-3 py-2"
            placeholder="Item name"
            value={form.item_name}
            onChange={(event) => handleFormChange('item_name', event.target.value)}
            required
          />
          <input
            className="rounded-md border px-3 py-2"
            placeholder="Description"
            value={form.description}
            onChange={(event) => handleFormChange('description', event.target.value)}
          />
          <input
            type="number"
            min="1"
            step="0.01"
            className="rounded-md border px-3 py-2"
            placeholder="Price"
            value={form.price}
            onChange={(event) => handleFormChange('price', event.target.value)}
            required
          />
          <select
            className="rounded-md border px-3 py-2"
            value={form.category}
            onChange={(event) => handleFormChange('category', event.target.value)}
          >
            {MENU_CATEGORIES.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
          <input
            type="number"
            min="1"
            max="180"
            className="rounded-md border px-3 py-2"
            placeholder="Preparation time (minutes)"
            value={form.preparation_time}
            onChange={(event) => handleFormChange('preparation_time', event.target.value)}
          />
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={form.is_available}
              onChange={(event) => handleFormChange('is_available', event.target.checked)}
            />
            Available
          </label>
        </div>
        <button
          type="submit"
          className="mt-4 rounded-md bg-blue-600 px-4 py-2 text-sm text-white"
        >
          Create Item
        </button>
      </form>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="text-lg font-semibold">Catalog Items</h2>
        {loading ? (
          <p className="mt-3 text-sm text-gray-600">Loading catalog...</p>
        ) : items.length === 0 ? (
          <p className="mt-3 text-sm text-gray-600">No items found.</p>
        ) : (
          <div className="mt-4 space-y-2">
            {items.map((item) => (
              <div key={item.item_id} className="rounded-md border border-gray-200 p-3">
                <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                  <div>
                    <p className="font-medium">{item.item_name}</p>
                    <p className="text-sm text-gray-600">
                      {item.category || 'uncategorized'} | Price {item.price}
                    </p>
                    <p className="text-sm text-gray-600">
                      Vendor {item.vendor_id} | {item.is_available ? 'Available' : 'Unavailable'}
                    </p>
                  </div>
                  <button
                    type="button"
                    className="rounded border px-3 py-1 text-sm"
                    onClick={() => toggleAvailability(item)}
                  >
                    {item.is_available ? 'Mark Unavailable' : 'Mark Available'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {isVendor && (
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="text-lg font-semibold">Vendor Orders</h2>
          {orders.length === 0 ? (
            <p className="mt-3 text-sm text-gray-600">No orders found.</p>
          ) : (
            <div className="mt-4 space-y-2">
              {orders.map((order) => (
                <div key={order.order_id} className="rounded-md border border-gray-200 p-3">
                  <p className="font-medium">Order {order.order_id.slice(0, 8)}</p>
                  <p className="text-sm text-gray-600">
                    Status {order.status} | Total {order.total_amount}
                  </p>
                  <p className="text-sm text-gray-600">Pickup code {order.pickup_code || '-'}</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {(ORDER_TRANSITIONS[order.status] || []).map((nextStatus) => (
                      <button
                        key={nextStatus}
                        type="button"
                        className="rounded border px-2 py-1 text-xs"
                        onClick={() => progressOrder(order.order_id, nextStatus)}
                      >
                        Mark {nextStatus}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default FoodOrderPage;
