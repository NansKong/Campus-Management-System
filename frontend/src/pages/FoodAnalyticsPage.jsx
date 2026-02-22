import React, { useState, useEffect } from 'react';

function FoodAnalyticsPage() {
  const [analytics, setAnalytics] = useState({
    todayOrders: 52,
    totalRevenue: 4250,
    peakHour: '13:00 - 14:00',
    popularItems: [
      { name: 'Sandwich', orders: 45, revenue: 2250 },
      { name: 'Pasta', orders: 28, revenue: 2240 },
      { name: 'Coffee', orders: 67, revenue: 1340 },
    ],
  });

  const [hourlyData, setHourlyData] = useState([
    { hour: '10:00', orders: 15 },
    { hour: '11:00', orders: 8 },
    { hour: '12:00', orders: 12 },
    { hour: '13:00', orders: 45 },
    { hour: '14:00', orders: 22 },
    { hour: '15:00', orders: 10 },
    { hour: '16:00', orders: 18 },
  ]);

  const [prediction, setPrediction] = useState(null);

  const predictRushHours = () => {
    // Simulate AI prediction
    const predicted = {
      date: 'Tomorrow',
      rushHours: ['13:00 - 14:00', '16:00 - 16:30'],
      expectedOrders: 58,
      recommendation: 'Prepare extra stock for lunch break. Expected 30% increase.',
    };
    setPrediction(predicted);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold mb-8">📊 Food Stall Analytics</h1>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-2">Today's Orders</p>
            <p className="text-3xl font-bold text-blue-600">{analytics.todayOrders}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-2">Total Revenue</p>
            <p className="text-3xl font-bold text-green-600">₹{analytics.totalRevenue}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-2">Peak Hour</p>
            <p className="text-xl font-bold text-purple-600">{analytics.peakHour}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-2">Avg Order Value</p>
            <p className="text-3xl font-bold text-orange-600">
              ₹{(analytics.totalRevenue / analytics.todayOrders).toFixed(0)}
            </p>
          </div>
        </div>

        {/* Hourly Demand Chart */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">⏰ Hourly Demand Tracking</h2>
          <div className="space-y-3">
            {hourlyData.map((data) => (
              <div key={data.hour} className="flex items-center">
                <span className="w-24 text-sm font-semibold">{data.hour}</span>
                <div className="flex-1 bg-gray-200 rounded-full h-8 relative">
                  <div
                    className="bg-blue-500 h-8 rounded-full flex items-center justify-end pr-3 text-white font-semibold"
                    style={{ width: `${(data.orders / 50) * 100}%` }}
                  >
                    {data.orders}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* AI Prediction Section */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">🤖 AI-Based Rush Prediction</h2>
          <p className="text-gray-600 mb-4">
            Predict peak hours and demand for better preparation
          </p>

          <button
            onClick={predictRushHours}
            className="bg-purple-500 text-white px-6 py-3 rounded-lg hover:bg-purple-600 font-semibold"
          >
            🔮 Generate Prediction
          </button>

          {prediction && (
            <div className="mt-6 bg-purple-50 border-2 border-purple-300 rounded-lg p-6">
              <h3 className="font-bold text-purple-800 mb-4">
                📈 Prediction for {prediction.date}
              </h3>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600">Expected Rush Hours:</p>
                  <p className="font-semibold text-lg">
                    {prediction.rushHours.join(', ')}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Expected Orders:</p>
                  <p className="font-semibold text-lg">{prediction.expectedOrders}</p>
                </div>
                <div className="bg-yellow-50 border border-yellow-300 rounded p-3">
                  <p className="text-sm font-semibold text-yellow-800">
                    💡 Recommendation:
                  </p>
                  <p className="text-yellow-700">{prediction.recommendation}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Popular Items */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4">🏆 Popular Items</h2>
          <div className="space-y-4">
            {analytics.popularItems.map((item, index) => (
              <div
                key={item.name}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-4">
                  <span className="text-2xl font-bold text-gray-400">#{index + 1}</span>
                  <div>
                    <p className="font-semibold">{item.name}</p>
                    <p className="text-sm text-gray-600">{item.orders} orders</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-green-600">₹{item.revenue}</p>
                  <p className="text-sm text-gray-600">Revenue</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default FoodAnalyticsPage;