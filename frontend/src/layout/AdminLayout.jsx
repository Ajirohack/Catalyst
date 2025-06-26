import React from "react";
import { Outlet, Link, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  Users,
  Cpu,
  Plug,
  FileText,
  LogOut,
  Brain,
  Database,
} from "lucide-react";
import { cn } from "../lib/utils";

export default function AdminLayout() {
  const location = useLocation();

  const menuItems = [
    {
      path: "/admin",
      label: "Dashboard",
      icon: <LayoutDashboard className="h-5 w-5" />,
    },
    {
      path: "/admin/users",
      label: "Users",
      icon: <Users className="h-5 w-5" />,
    },
    {
      path: "/admin/models",
      label: "Models",
      icon: <Cpu className="h-5 w-5" />,
    },
    {
      path: "/admin/ai-providers",
      label: "AI Providers",
      icon: <Brain className="h-5 w-5" />,
    },
    {
      path: "/admin/integrations",
      label: "Integrations",
      icon: <Plug className="h-5 w-5" />,
    },
    {
      path: "/admin/logs",
      label: "Logs",
      icon: <FileText className="h-5 w-5" />,
    },
    {
      path: "/admin/knowledge-base",
      label: "Knowledge Base",
      icon: <Database className="h-5 w-5" />,
    },
  ];

  return (
    <div className="flex h-screen bg-background">
      <motion.aside
        initial={{ x: -20, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.3 }}
        className="w-64 border-r border-border bg-card shadow-sm flex flex-col"
      >
        <div className="p-4 border-b border-border">
          <h1 className="text-xl font-bold">Catalyst Admin</h1>
          <p className="text-sm text-muted-foreground">System Management</p>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
                location.pathname === item.path
                  ? "bg-primary text-primary-foreground"
                  : "hover:bg-accent hover:text-accent-foreground"
              )}
            >
              {item.icon}
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="p-4 border-t border-border">
          <button className="flex items-center gap-3 px-3 py-2 w-full rounded-md text-sm text-destructive hover:bg-destructive/10 transition-colors">
            <LogOut className="h-5 w-5" />
            Logout
          </button>
        </div>
      </motion.aside>

      <main className="flex-1 overflow-auto">
        <div className="container mx-auto p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
