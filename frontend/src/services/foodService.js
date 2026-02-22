import api from './api';

const foodService = {
  async getMenu(params = {}) {
    try {
      const response = await api.get('/food/menu', { params });
      return response.data;
    } catch (error) {
      console.error('Get menu error:', error.response?.data || error.message);
      throw error;
    }
  },

  async getSlots() {
    try {
      const response = await api.get('/food/slots');
      return response.data;
    } catch (error) {
      console.error('Get slots error:', error.response?.data || error.message);
      throw error;
    }
  },

  async listCatalogItems(params = {}) {
    try {
      const response = await api.get('/food/catalog/items', { params });
      return response.data;
    } catch (error) {
      console.error('List catalog items error:', error.response?.data || error.message);
      throw error;
    }
  },

  async createCatalogItem(payload) {
    try {
      const response = await api.post('/food/catalog/items', payload);
      return response.data;
    } catch (error) {
      console.error('Create catalog item error:', error.response?.data || error.message);
      throw error;
    }
  },

  async updateCatalogItem(itemId, payload) {
    try {
      const response = await api.put(`/food/catalog/items/${itemId}`, payload);
      return response.data;
    } catch (error) {
      console.error('Update catalog item error:', error.response?.data || error.message);
      throw error;
    }
  },

  async createOrder(orderData) {
    try {
      const response = await api.post('/food/orders', orderData);
      return response.data;
    } catch (error) {
      console.error('Create order error:', error.response?.data || error.message);
      throw error;
    }
  },

  async getMyOrders() {
    try {
      const response = await api.get('/food/orders/my-orders');
      return response.data;
    } catch (error) {
      console.error('Get student orders error:', error.response?.data || error.message);
      throw error;
    }
  },

  async getVendorOrders() {
    try {
      const response = await api.get('/food/orders/vendor');
      return response.data;
    } catch (error) {
      console.error('Get vendor orders error:', error.response?.data || error.message);
      throw error;
    }
  },

  async updateOrderStatus(orderId, status) {
    try {
      const response = await api.put(`/food/orders/${orderId}/status`, { status });
      return response.data;
    } catch (error) {
      console.error('Update order status error:', error.response?.data || error.message);
      throw error;
    }
  },
};

export default foodService;
