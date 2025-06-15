import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import UserLayout from './layout/UserLayout';
import AdminLayout from './layout/AdminLayout';
import Dashboard from './pages/Dashboard';
import NewProject from './pages/NewProject';
import Continue from './pages/ContinueProject';
import ProjectDetail from './pages/ProjectDetails';
import Settings from './pages/Settings';
import AdminDashboard from './pages/admin/AdminDashboard';
import Users from './pages/admin/Users';
import Models from './pages/admin/Models';
import Integrations from './pages/admin/Integrations';
import Logs from './pages/admin/Logs';
import { getUserRole } from './context/auth';

export default function App() {
  const role = getUserRole(); // 'admin' or 'user'

  return (
    <Routes>
      {role === 'user' && (
        <Route element={<UserLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/new-project" element={<NewProject />} />
          <Route path="/continue" element={<Continue />} />
          <Route path="/project/:id" element={<ProjectDetail />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      )}
      {role === 'admin' && (
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<AdminDashboard />} />
          <Route path="users" element={<Users />} />
          <Route path="models" element={<Models />} />
          <Route path="integrations" element={<Integrations />} />
          <Route path="logs" element={<Logs />} />
        </Route>
      )}
    </Routes>
  );
}