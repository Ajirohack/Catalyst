import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  Search,
  MoreHorizontal,
  UserPlus,
  Shield,
  Download,
  Filter,
  Mail,
  Star,
  BadgeCheck,
  Ban,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../../components/ui/card";
import { Button } from "../../components/ui/button";

export default function Users() {
  const [searchTerm, setSearchTerm] = useState("");

  // Mock user data
  const users = [
    {
      id: 1,
      name: "John Doe",
      email: "john.doe@example.com",
      role: "user",
      status: "active",
      projects: 8,
      lastActive: "2 hours ago",
      joined: "Jan 15, 2024",
    },
    {
      id: 2,
      name: "Jane Smith",
      email: "jane.smith@example.com",
      role: "admin",
      status: "active",
      projects: 12,
      lastActive: "Just now",
      joined: "Nov 3, 2023",
    },
    {
      id: 3,
      name: "Robert Johnson",
      email: "robert.j@example.com",
      role: "user",
      status: "inactive",
      projects: 3,
      lastActive: "5 days ago",
      joined: "Mar 21, 2024",
    },
    {
      id: 4,
      name: "Emily Wilson",
      email: "emily.w@example.com",
      role: "moderator",
      status: "active",
      projects: 15,
      lastActive: "1 day ago",
      joined: "Dec 10, 2023",
    },
    {
      id: 5,
      name: "Michael Brown",
      email: "michael.b@example.com",
      role: "user",
      status: "blocked",
      projects: 0,
      lastActive: "3 months ago",
      joined: "Oct 5, 2023",
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.3,
      },
    },
  };

  const filteredUsers = users.filter(
    (user) =>
      user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getRoleColor = (role) => {
    switch (role) {
      case "admin":
        return "bg-red-500";
      case "moderator":
        return "bg-amber-500";
      case "user":
        return "bg-blue-500";
      default:
        return "bg-slate-500";
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "active":
        return "bg-green-500";
      case "inactive":
        return "bg-gray-500";
      case "blocked":
        return "bg-red-500";
      default:
        return "bg-slate-500";
    }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">User Management</h1>
          <p className="text-muted-foreground">
            Manage user accounts, permissions, and activity
          </p>
        </div>
        <Button className="flex items-center gap-2">
          <UserPlus className="h-4 w-4" />
          Add User
        </Button>
      </div>

      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
              <CardTitle>Users ({users.length})</CardTitle>
              <div className="flex w-full sm:w-auto gap-2">
                <div className="relative flex-1">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Search users..."
                    className="rounded-md border border-input pl-8 pr-3 py-2 text-sm bg-background w-full"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <Button variant="outline" size="icon">
                  <Filter className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="icon">
                  <Download className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border">
              <div className="relative w-full overflow-auto">
                <table className="w-full caption-bottom text-sm">
                  <thead>
                    <tr className="border-b transition-colors hover:bg-muted/50">
                      <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                        Name
                      </th>
                      <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                        Email
                      </th>
                      <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                        Role
                      </th>
                      <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                        Status
                      </th>
                      <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                        Projects
                      </th>
                      <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                        Joined
                      </th>
                      <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsers.map((user) => (
                      <motion.tr
                        key={user.id}
                        className="border-b transition-colors hover:bg-muted/50"
                        variants={itemVariants}
                      >
                        <td className="p-4 align-middle font-medium">
                          {user.name}
                          <div className="text-xs text-muted-foreground">
                            {user.lastActive}
                          </div>
                        </td>
                        <td className="p-4 align-middle">{user.email}</td>
                        <td className="p-4 align-middle">
                          <div className="flex items-center gap-2">
                            <div
                              className={`w-2 h-2 rounded-full ${getRoleColor(user.role)}`}
                            />
                            <span className="capitalize">{user.role}</span>
                            {user.role === "admin" && (
                              <BadgeCheck className="h-4 w-4 text-blue-500" />
                            )}
                          </div>
                        </td>
                        <td className="p-4 align-middle">
                          <div className="flex items-center gap-2">
                            <div
                              className={`w-2 h-2 rounded-full ${getStatusColor(user.status)}`}
                            />
                            <span className="capitalize">{user.status}</span>
                          </div>
                        </td>
                        <td className="p-4 align-middle">{user.projects}</td>
                        <td className="p-4 align-middle">{user.joined}</td>
                        <td className="p-4 align-middle">
                          <div className="flex items-center gap-2">
                            <button className="p-2 rounded-md hover:bg-muted transition-colors">
                              <Mail className="h-4 w-4" />
                            </button>
                            {user.role !== "admin" && (
                              <button className="p-2 rounded-md hover:bg-muted transition-colors text-amber-500">
                                <Shield className="h-4 w-4" />
                              </button>
                            )}
                            {user.status !== "blocked" ? (
                              <button className="p-2 rounded-md hover:bg-muted transition-colors text-red-500">
                                <Ban className="h-4 w-4" />
                              </button>
                            ) : (
                              <button className="p-2 rounded-md hover:bg-muted transition-colors text-green-500">
                                <Star className="h-4 w-4" />
                              </button>
                            )}
                            <button className="p-2 rounded-md hover:bg-muted transition-colors">
                              <MoreHorizontal className="h-4 w-4" />
                            </button>
                          </div>
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
