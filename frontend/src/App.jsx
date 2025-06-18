import React, { lazy, Suspense } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { Loader } from "lucide-react";
import UserLayout from "./layout/UserLayout";
import AdminLayout from "./layout/AdminLayout";
import { getUserRole } from "./context/auth";
import LazyLoader from "./components/LazyLoader";

// Loading fallback component
const LoadingFallback = () => (
  <div className="flex flex-col items-center justify-center min-h-screen">
    <Loader className="h-12 w-12 animate-spin text-primary" />
    <p className="mt-4 text-lg text-muted-foreground">Loading...</p>
  </div>
);

// Lazy-loaded components for better performance
// User pages
const Dashboard = lazy(() => import("./pages/Dashboard"));
const NewProject = lazy(() => import("./pages/NewProject"));
const Continue = lazy(() => import("./pages/ContinueProject"));
const ProjectDetail = lazy(() => import("./pages/ProjectDetails"));
const Settings = lazy(() => import("./pages/Settings"));
const Onboarding = lazy(() => import("./pages/user/Onboarding"));
const AnalysisDetail = lazy(() => import("./pages/user/AnalysisDetail"));
const AnalysisProgress = lazy(() => import("./pages/user/AnalysisProgress"));

// Admin pages
const AdminDashboard = lazy(() => import("./pages/admin/AdminDashboard"));
const UserManagement = lazy(() => import("./pages/admin/UserManagement"));
const Models = lazy(() => import("./pages/admin/Models"));
const Integrations = lazy(() => import("./pages/admin/Integrations"));
const Logs = lazy(() => import("./pages/admin/Logs"));
const SystemMonitoring = lazy(() => import("./pages/admin/SystemMonitoring"));
const AnalyticsDashboard = lazy(
  () => import("./pages/admin/AnalyticsDashboard")
);

// Auth pages
const Login = lazy(() => import("./pages/auth/Login"));
const Register = lazy(() => import("./pages/auth/Register"));
const ForgotPassword = lazy(() => import("./pages/auth/ForgotPassword"));
const ResetPassword = lazy(() => import("./pages/auth/ResetPassword"));
const MfaSetup = lazy(() => import("./pages/auth/MfaSetup"));

export default function App() {
  const role = getUserRole(); // 'admin' or 'user'

  return (
    <>
      <Suspense fallback={<LoadingFallback />}>
        <Routes>
          {/* Auth Routes */}
          <Route path="/login" element={<LazyLoader><Login /></LazyLoader>} />
          <Route path="/register" element={<LazyLoader><Register /></LazyLoader>} />
          <Route path="/forgot-password" element={<LazyLoader><ForgotPassword /></LazyLoader>} />
          <Route path="/reset-password" element={<LazyLoader><ResetPassword /></LazyLoader>} />
          <Route path="/mfa-setup" element={<LazyLoader><MfaSetup /></LazyLoader>} />
          <Route path="/onboarding" element={<LazyLoader><Onboarding /></LazyLoader>} />

          {/* User Routes */}
          {role === "user" && (
            <Route element={<UserLayout />}>
              <Route path="/" element={<Navigate to="/dashboard" />} />
              <Route path="/dashboard" element={<LazyLoader><Dashboard /></LazyLoader>} />
              <Route path="/new-project" element={<LazyLoader><NewProject /></LazyLoader>} />
              <Route path="/continue" element={<LazyLoader><Continue /></LazyLoader>} />
              <Route path="/project/:id" element={<LazyLoader><ProjectDetail /></LazyLoader>} />
              <Route path="/analysis/:id" element={<LazyLoader><AnalysisDetail /></LazyLoader>} />
              <Route path="/analysis/progress/:id" element={<LazyLoader><AnalysisProgress /></LazyLoader>} />
              <Route path="/settings" element={<LazyLoader><Settings /></LazyLoader>} />
            </Route>
          )}

          {/* Admin Routes */}
          {role === "admin" && (
            <Route element={<AdminLayout />}>
              <Route path="/" element={<Navigate to="/admin" />} />
              <Route path="/admin" element={<LazyLoader><AdminDashboard /></LazyLoader>} />
              <Route path="/admin/users" element={<LazyLoader><UserManagement /></LazyLoader>} />
              <Route path="/admin/models" element={<LazyLoader><Models /></LazyLoader>} />
              <Route path="/admin/integrations" element={<LazyLoader><Integrations /></LazyLoader>} />
              <Route path="/admin/logs" element={<LazyLoader><Logs /></LazyLoader>} />
              <Route path="/admin/system" element={<LazyLoader><SystemMonitoring /></LazyLoader>} />
              <Route path="/admin/analytics" element={<LazyLoader><AnalyticsDashboard /></LazyLoader>} />
            </Route>
          )}

          {/* Fallback route */}
          <Route path="*" element={<Navigate to={role === "admin" ? "/admin" : "/dashboard"} />} />
        </Routes>
      </Suspense>
      <Toaster position="top-right" />
    </>
  );
}
          {role === "admin" && (
            <Route path="/admin" element={<AdminLayout />}>
              <Route index element={<AdminDashboard />} />
              <Route path="users" element={<UserManagement />} />
              <Route path="models" element={<Models />} />
              <Route path="integrations" element={<Integrations />} />
              <Route path="logs" element={<Logs />} />
              <Route path="monitoring" element={<SystemMonitoring />} />
              <Route path="analytics" element={<AnalyticsDashboard />} />
            </Route>
          )}
        </Routes>
      </Suspense>

      <Toaster
        position="top-right"
        toastOptions={{
          duration: 5000,
          style: {
            background: "#363636",
            color: "#fff",
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: "#10B981",
              secondary: "white",
            },
          },
          error: {
            duration: 4000,
            iconTheme: {
              primary: "#EF4444",
              secondary: "white",
            },
          },
        }}
      />
    </>
  );
}
