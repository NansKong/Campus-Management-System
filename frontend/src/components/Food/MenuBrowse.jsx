import React, { useState, useEffect } from 'react';
import foodService from '../../services/foodService';

function MenuBrowse({ onAddToCart }) {
  const [menuItems, setMenuItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    loadMenu();
  }, []);

  const loadMenu = async () => {
    try {
      const items = await foodService.getMenu();
      setMenuItems(items);
    } catch (err) {
      setError('Failed to load menu');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const categories = ['all', 'breakfast', 'lunch', 'snacks', 'beverages'];

  const filteredItems =
    selectedCategory === 'all'
      ? menuItems
      : menuItems.filter((item) => item.category === selectedCategory);

  if (loading) {
    return <div className="text-center py-8">Loading menu...</div>;
  }

  if (error) {
    return <div className="text-red-500 text-center py-8">{error}</div>;
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Menu</h2>

      {/* Category Filter */}
      <div className="flex space-x-4 mb-6 overflow-x-auto">
        {categories.map((category) => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`px-4 py-2 rounded-lg whitespace-nowrap ${
              selectedCategory === category
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {category.charAt(0).toUpperCase() + category.slice(1)}
          </button>
        ))}
      </div>

      {/* Menu Items Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredItems.map((item) => (
          <div
            key={item.item_id}
            className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition"
          >
            <div className="aspect-w-16 aspect-h-9 bg-gray-200 rounded-lg mb-4">
              {/* Placeholder for image */}
              <div className="flex items-center justify-center h-40 bg-gradient-to-br from-blue-100 to-blue-200 rounded-lg">
                <span className="text-4xl">🍽️</span>
              </div>
            </div>

            <h3 className="text-lg font-semibold mb-2">{item.item_name}</h3>
            <p className="text-gray-600 text-sm mb-3">{item.description}</p>

            <div className="flex items-center justify-between">
              <span className="text-xl font-bold text-green-600">
                ₹{item.price}
              </span>
              <button
                onClick={() => onAddToCart(item)}
                className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
              >
                Add to Cart
              </button>
            </div>

            <div className="mt-3 text-xs text-gray-500">
              <span className="capitalize">{item.category}</span>
              {item.preparation_time && (
                <span className="ml-2">• {item.preparation_time} mins</span>
              )}
            </div>
          </div>
        ))}
      </div>

      {filteredItems.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No items found in this category
        </div>
      )}
    </div>
  );
}

export default MenuBrowse;