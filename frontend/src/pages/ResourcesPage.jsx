import React, { useState, useEffect } from 'react';

function ResourcesPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [resources, setResources] = useState({
    blocks: [],
    classrooms: [],
    courses: [],
    faculty: [],
    students: [],
  });

  const [utilization, setUtilization] = useState({
    classroomUtilization: 68.5,
    facultyWorkload: 75.2,
    averageClassSize: 45,
  });

  useEffect(() => {
    loadResources();
  }, []);

  const loadResources = () => {
    // Mock data
    const mockData = {
      blocks: [
        { id: '1', name: 'Academic Block 1', code: 'AB1', floors: 5, classrooms: 25 },
        { id: '2', name: 'Academic Block 2', code: 'AB2', floors: 4, classrooms: 20 },
        { id: '3', name: 'Lab Block', code: 'LB1', floors: 3, classrooms: 15 },
      ],
      classrooms: [
        {
          id: '1',
          block: 'AB1',
          room: '101',
          capacity: 60,
          type: 'Lecture Hall',
          utilization: 85,
        },
        {
          id: '2',
          block: 'AB1',
          room: '102',
          capacity: 40,
          type: 'Seminar Room',
          utilization: 60,
        },
        {
          id: '3',
          block: 'AB1',
          room: '201',
          capacity: 50,
          type: 'Lecture Hall',
          utilization: 70,
        },
        { id: '4', block: 'LB1', room: 'L01', capacity: 30, type: 'Lab', utilization: 90 },
        { id: '5', block: 'AB2', room: '101', capacity: 55, type: 'Lecture Hall', utilization: 45 },
      ],
      courses: [
        {
          id: '1',
          code: 'CSE301',
          name: 'Database Management Systems',
          credits: 4,
          sections: 3,
          students: 180,
        },
        {
          id: '2',
          code: 'CSE302',
          name: 'Data Structures',
          credits: 4,
          sections: 2,
          students: 120,
        },
        {
          id: '3',
          code: 'CSE303',
          name: 'Operating Systems',
          credits: 3,
          sections: 2,
          students: 100,
        },
      ],
      faculty: [
        {
          id: '1',
          name: 'Dr. John Doe',
          department: 'CSE',
          sections: 3,
          contactHours: 18,
          students: 150,
        },
        {
          id: '2',
          name: 'Dr. Jane Smith',
          department: 'CSE',
          sections: 2,
          contactHours: 12,
          students: 100,
        },
        {
          id: '3',
          name: 'Prof. Robert Brown',
          department: 'CSE',
          sections: 4,
          contactHours: 24,
          students: 200,
        },
      ],
      students: [
        { program: 'B.Tech CSE', semester: 5, count: 450 },
        { program: 'B.Tech CSE', semester: 3, count: 480 },
        { program: 'B.Tech ECE', semester: 5, count: 320 },
      ],
    };

    setResources(mockData);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold mb-8">🏫 Campus Resource Management</h1>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-lg mb-8">
          <div className="flex border-b">
            {[
              { id: 'overview', label: '📊 Overview', icon: '📊' },
              { id: 'blocks', label: '🏢 Blocks', icon: '🏢' },
              { id: 'classrooms', label: '🚪 Classrooms', icon: '🚪' },
              { id: 'courses', label: '📚 Courses', icon: '📚' },
              { id: 'faculty', label: '👨‍🏫 Faculty', icon: '👨‍🏫' },
              { id: 'analytics', label: '📈 Analytics', icon: '📈' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 px-4 py-3 text-sm font-semibold ${
                  activeTab === tab.id
                    ? 'border-b-2 border-blue-500 text-blue-600'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div>
          {activeTab === 'overview' && <OverviewTab utilization={utilization} resources={resources} />}
          {activeTab === 'blocks' && <BlocksTab blocks={resources.blocks} />}
          {activeTab === 'classrooms' && <ClassroomsTab classrooms={resources.classrooms} />}
          {activeTab === 'courses' && <CoursesTab courses={resources.courses} />}
          {activeTab === 'faculty' && <FacultyTab faculty={resources.faculty} />}
          {activeTab === 'analytics' && <AnalyticsTab utilization={utilization} resources={resources} />}
        </div>
      </div>
    </div>
  );
}

// Overview Tab
function OverviewTab({ utilization, resources }) {
  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard
          title="Classroom Utilization"
          value={`${utilization.classroomUtilization}%`}
          color="blue"
          icon="🚪"
        />
        <MetricCard
          title="Faculty Workload"
          value={`${utilization.facultyWorkload}%`}
          color="green"
          icon="👨‍🏫"
        />
        <MetricCard
          title="Avg Class Size"
          value={utilization.averageClassSize}
          color="purple"
          icon="👥"
        />
      </div>

      {/* Quick Stats */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold mb-4">Quick Statistics</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatBox label="Total Blocks" value={resources.blocks.length} />
          <StatBox label="Total Classrooms" value={resources.classrooms.length} />
          <StatBox label="Active Courses" value={resources.courses.length} />
          <StatBox label="Faculty Members" value={resources.faculty.length} />
        </div>
      </div>
    </div>
  );
}

// Blocks Tab
function BlocksTab({ blocks }) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold mb-6">Campus Blocks</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {blocks.map((block) => (
          <div key={block.id} className="border-2 border-gray-200 rounded-lg p-6 hover:border-blue-300">
            <h3 className="text-lg font-bold mb-2">{block.name}</h3>
            <p className="text-gray-600 mb-4">Code: {block.code}</p>
            <div className="space-y-2 text-sm">
              <p>
                <span className="font-semibold">Floors:</span> {block.floors}
              </p>
              <p>
                <span className="font-semibold">Classrooms:</span> {block.classrooms}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Classrooms Tab
function ClassroomsTab({ classrooms }) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold mb-6">Classrooms & Utilization</h2>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-4 py-3 text-left">Block</th>
              <th className="px-4 py-3 text-left">Room</th>
              <th className="px-4 py-3 text-left">Type</th>
              <th className="px-4 py-3 text-center">Capacity</th>
              <th className="px-4 py-3 text-center">Utilization</th>
            </tr>
          </thead>
          <tbody>
            {classrooms.map((room, index) => (
              <tr key={room.id} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="px-4 py-3 font-semibold">{room.block}</td>
                <td className="px-4 py-3">{room.room}</td>
                <td className="px-4 py-3">{room.type}</td>
                <td className="px-4 py-3 text-center">{room.capacity}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center">
                    <div className="flex-1 bg-gray-200 rounded-full h-6 mr-2">
                      <div
                        className={`h-6 rounded-full flex items-center justify-center text-white text-xs font-semibold ${
                          room.utilization >= 80
                            ? 'bg-green-500'
                            : room.utilization >= 60
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                        }`}
                        style={{ width: `${room.utilization}%` }}
                      >
                        {room.utilization}%
                      </div>
                    </div>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Courses Tab
function CoursesTab({ courses }) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold mb-6">Course Distribution</h2>
      <div className="space-y-4">
        {courses.map((course) => (
          <div key={course.id} className="border-2 border-gray-200 rounded-lg p-4">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-bold text-lg">{course.code}</h3>
                <p className="text-gray-700">{course.name}</p>
                <p className="text-sm text-gray-500 mt-1">Credits: {course.credits}</p>
              </div>
              <div className="text-right">
                <div className="bg-blue-100 px-3 py-1 rounded-full text-blue-800 font-semibold mb-2">
                  {course.sections} Sections
                </div>
                <p className="text-sm text-gray-600">{course.students} Students</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Faculty Tab
function FacultyTab({ faculty }) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold mb-6">Faculty Workload Distribution</h2>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-4 py-3 text-left">Name</th>
              <th className="px-4 py-3 text-left">Department</th>
              <th className="px-4 py-3 text-center">Sections</th>
              <th className="px-4 py-3 text-center">Contact Hours/Week</th>
              <th className="px-4 py-3 text-center">Total Students</th>
            </tr>
          </thead>
          <tbody>
            {faculty.map((f, index) => (
              <tr key={f.id} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="px-4 py-3 font-semibold">{f.name}</td>
                <td className="px-4 py-3">{f.department}</td>
                <td className="px-4 py-3 text-center">
                  <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full font-semibold">
                    {f.sections}
                  </span>
                </td>
                <td className="px-4 py-3 text-center font-semibold">{f.contactHours}</td>
                <td className="px-4 py-3 text-center">{f.students}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Analytics Tab
function AnalyticsTab({ utilization, resources }) {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold mb-6">📊 Capacity Utilization Analysis</h2>

        {/* Classroom Utilization */}
        <div className="mb-8">
          <h3 className="font-semibold mb-4">Classroom Utilization Rate</h3>
          <div className="flex items-center">
            <div className="flex-1 bg-gray-200 rounded-full h-10 mr-4">
              <div
                className="bg-gradient-to-r from-blue-500 to-blue-600 h-10 rounded-full flex items-center justify-center text-white font-bold"
                style={{ width: `${utilization.classroomUtilization}%` }}
              >
                {utilization.classroomUtilization}%
              </div>
            </div>
          </div>
          <p className="text-sm text-gray-600 mt-2">
            Average utilization across all classrooms (hours scheduled / total available hours)
          </p>
        </div>

        {/* Faculty Workload */}
        <div className="mb-8">
          <h3 className="font-semibold mb-4">Faculty Workload Distribution</h3>
          <div className="flex items-center">
            <div className="flex-1 bg-gray-200 rounded-full h-10 mr-4">
              <div
                className="bg-gradient-to-r from-green-500 to-green-600 h-10 rounded-full flex items-center justify-center text-white font-bold"
                style={{ width: `${utilization.facultyWorkload}%` }}
              >
                {utilization.facultyWorkload}%
              </div>
            </div>
          </div>
          <p className="text-sm text-gray-600 mt-2">
            Average faculty utilization based on contact hours and student load
          </p>
        </div>

        {/* Recommendations */}
        <div className="bg-yellow-50 border border-yellow-300 rounded-lg p-4">
          <h3 className="font-semibold text-yellow-800 mb-2">💡 Optimization Recommendations</h3>
          <ul className="space-y-2 text-sm text-yellow-700">
            <li>• AB2-101 has low utilization (45%) - consider consolidating classes</li>
            <li>• Prof. Robert Brown has high workload (24 hrs/week) - consider redistribution</li>
            <li>• Lab Block L01 is over-utilized (90%) - may need additional lab space</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

// Helper Components
function MetricCard({ title, value, color, icon }) {
  const colors = {
    blue: 'bg-blue-50 text-blue-800 border-blue-200',
    green: 'bg-green-50 text-green-800 border-green-200',
    purple: 'bg-purple-50 text-purple-800 border-purple-200',
  };

  return (
    <div className={`${colors[color]} border-2 rounded-lg p-6`}>
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm">{title}</p>
        <span className="text-2xl">{icon}</span>
      </div>
      <p className="text-3xl font-bold">{value}</p>
    </div>
  );
}

function StatBox({ label, value }) {
  return (
    <div className="bg-gray-50 p-4 rounded-lg text-center">
      <p className="text-3xl font-bold text-blue-600">{value}</p>
      <p className="text-sm text-gray-600 mt-1">{label}</p>
    </div>
  );
}

export default ResourcesPage;