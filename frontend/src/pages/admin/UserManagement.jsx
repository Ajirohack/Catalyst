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
  X,
  Check,
  Trash2,
  Edit,
  User,
  Lock,
  Eye,
  EyeOff,
  ChevronDown,
  AlertTriangle,
  Plus,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
  CardFooter,
} from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Switch } from "../../components/ui/switch";
import {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
} from "../../components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../../components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../../components/ui/select";
import { toast } from "react-hot-toast";

export default function Users() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedUser, setSelectedUser] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showAddUserDialog, setShowAddUserDialog] = useState(false);
  const [showEditUserDialog, setShowEditUserDialog] = useState(false);
  const [selectedRoleFilter, setSelectedRoleFilter] = useState("all");
  const [selectedStatusFilter, setSelectedStatusFilter] = useState("all");
  const [roleDropdownOpen, setRoleDropdownOpen] = useState(false);
  const [statusDropdownOpen, setStatusDropdownOpen] = useState(false);

  // Form states for new user
  const [newUser, setNewUser] = useState({
    name: "",
    email: "",
    role: "user",
    password: "",
    status: "active",
  });

  // Form states for editing user
  const [editUser, setEditUser] = useState({
    id: null,
    name: "",
    email: "",
    role: "",
    status: "",
  });

  // States for bulk user management
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [showBulkActionDialog, setShowBulkActionDialog] = useState(false);
  const [bulkAction, setBulkAction] = useState(null);
  const [bulkActionDetails, setBulkActionDetails] = useState({
    role: "",
    status: "",
    reason: "",
  });

  // State for security settings
  const [securitySettings, setSecuritySettings] = useState({
    requireMfa: false,
    passwordExpiryDays: 90,
    maxLoginAttempts: 5,
    sessionTimeoutMinutes: 30,
    enforcePasswordHistory: 3,
  });

  // State for permissions management
  const [customRoles, setCustomRoles] = useState([
    {
      id: "custom-1",
      name: "Support Agent",
      description: "Customer support with limited access",
      baseRole: "user",
      customPermissions: {
        projects: { view: true, create: false, edit: true, delete: false },
        analytics: { view: true, export: false },
      },
    },
  ]);

  // State for activity logs
  const [userActivityLogs, setUserActivityLogs] = useState([
    {
      userId: 1,
      action: "login",
      timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
      ipAddress: "192.168.1.1",
      userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
      status: "success",
    },
    {
      userId: 2,
      action: "password_changed",
      timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
      ipAddress: "192.168.1.2",
      userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
      status: "success",
    },
    {
      userId: 3,
      action: "login",
      timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
      ipAddress: "192.168.1.3",
      userAgent: "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0)",
      status: "failed",
    },
  ]);

  // Mock user data
  const [users, setUsers] = useState([
    {
      id: 1,
      name: "John Doe",
      email: "john.doe@example.com",
      role: "user",
      status: "active",
      projects: 8,
      lastActive: "2 hours ago",
      joined: "Jan 15, 2024",
      avatar: "https://randomuser.me/api/portraits/men/44.jpg",
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
      avatar: "https://randomuser.me/api/portraits/women/68.jpg",
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
      avatar: "https://randomuser.me/api/portraits/men/32.jpg",
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
      avatar: "https://randomuser.me/api/portraits/women/17.jpg",
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
      avatar: "https://randomuser.me/api/portraits/men/22.jpg",
    },
    {
      id: 6,
      name: "Sara Johnson",
      email: "sara.j@example.com",
      role: "analyst",
      status: "active",
      projects: 7,
      lastActive: "4 hours ago",
      joined: "Apr 12, 2024",
      avatar: "https://randomuser.me/api/portraits/women/22.jpg",
    },
    {
      id: 7,
      name: "David Williams",
      email: "david.w@example.com",
      role: "user",
      status: "active",
      projects: 4,
      lastActive: "Yesterday",
      joined: "Feb 8, 2024",
      avatar: "https://randomuser.me/api/portraits/men/75.jpg",
    },
  ]);

  // Animation variants
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

  // Filter users based on search term and role/status filters
  const filteredUsers = users.filter((user) => {
    const matchesSearch =
      user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesRole =
      selectedRoleFilter === "all" || user.role === selectedRoleFilter;
    const matchesStatus =
      selectedStatusFilter === "all" || user.status === selectedStatusFilter;

    return matchesSearch && matchesRole && matchesStatus;
  });

  // Get color based on role
  const getRoleColor = (role) => {
    switch (role) {
      case "admin":
        return "bg-red-500";
      case "moderator":
        return "bg-amber-500";
      case "user":
        return "bg-blue-500";
      case "analyst":
        return "bg-purple-500";
      default:
        return "bg-slate-500";
    }
  };

  // Get color based on status
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

  // Handle adding a new user
  const handleAddUser = () => {
    // Form validation
    if (!newUser.name || !newUser.email || !newUser.password) {
      toast.error("Please fill in all required fields");
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(newUser.email)) {
      toast.error("Please enter a valid email address");
      return;
    }

    // Create new user object
    const newId = Math.max(...users.map((user) => user.id)) + 1;
    const userToAdd = {
      id: newId,
      name: newUser.name,
      email: newUser.email,
      role: newUser.role,
      status: newUser.status,
      projects: 0,
      lastActive: "Never",
      joined: new Date().toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      }),
      avatar: `https://randomuser.me/api/portraits/${Math.random() > 0.5 ? "men" : "women"}/${Math.floor(Math.random() * 100)}.jpg`,
    };

    // Add user to the list
    setUsers([...users, userToAdd]);

    // Reset form and close dialog
    setNewUser({
      name: "",
      email: "",
      role: "user",
      password: "",
      status: "active",
    });
    setShowAddUserDialog(false);

    toast.success(`User ${userToAdd.name} created successfully`);
  };

  // Handle opening the edit user dialog
  const handleOpenEditUser = (user) => {
    setEditUser({
      id: user.id,
      name: user.name,
      email: user.email,
      role: user.role,
      status: user.status,
    });
    setShowEditUserDialog(true);
  };

  // Handle saving edited user
  const handleSaveEditUser = () => {
    // Form validation
    if (!editUser.name || !editUser.email) {
      toast.error("Please fill in all required fields");
      return;
    }

    // Update user in the list
    const updatedUsers = users.map((user) => {
      if (user.id === editUser.id) {
        return { ...user, ...editUser };
      }
      return user;
    });

    setUsers(updatedUsers);
    setShowEditUserDialog(false);
    toast.success(`User ${editUser.name} updated successfully`);
  };

  // Handle user deletion
  const handleDeleteUser = () => {
    if (!selectedUser) return;

    const updatedUsers = users.filter((user) => user.id !== selectedUser.id);
    setUsers(updatedUsers);
    setShowDeleteConfirm(false);
    setSelectedUser(null);

    toast.success("User deleted successfully");
  };

  // Handle toggling user status
  const handleToggleStatus = (userId) => {
    const updatedUsers = users.map((user) => {
      if (user.id === userId) {
        const newStatus = user.status === "active" ? "inactive" : "active";
        toast.success(
          `User ${user.name} ${newStatus === "active" ? "activated" : "deactivated"}`
        );
        return { ...user, status: newStatus };
      }
      return user;
    });

    setUsers(updatedUsers);
  };

  // Open delete confirmation
  const openDeleteConfirmation = (user) => {
    setSelectedUser(user);
    setShowDeleteConfirm(true);
  };

  // Handle bulk user selection
  const handleSelectUser = (userId) => {
    if (selectedUsers.includes(userId)) {
      setSelectedUsers(selectedUsers.filter((id) => id !== userId));
    } else {
      setSelectedUsers([...selectedUsers, userId]);
    }
  };

  // Handle "select all" functionality
  const handleSelectAllUsers = (e) => {
    if (e.target.checked) {
      const allUserIds = filteredUsers.map((user) => user.id);
      setSelectedUsers(allUserIds);
    } else {
      setSelectedUsers([]);
    }
  };

  // Handle bulk action initiation
  const handleBulkAction = (action) => {
    setBulkAction(action);
    setBulkActionDetails({
      role: "",
      status: "",
      reason: "",
    });
    setShowBulkActionDialog(true);
  };

  // Execute bulk action
  const executeBulkAction = () => {
    // In a real implementation, this would make API calls

    // Simulate action on selected users
    toast.success(`${bulkAction} applied to ${selectedUsers.length} users`);

    // Reset states
    setShowBulkActionDialog(false);
    setSelectedUsers([]);
    setBulkAction(null);
  };

  // Role permissions matrix
  const ROLE_PERMISSIONS = {
    admin: {
      name: "Administrator",
      description: "Full system access with all privileges",
      permissions: {
        dashboard: { view: true, edit: true },
        users: { view: true, create: true, edit: true, delete: true },
        projects: { view: true, create: true, edit: true, delete: true },
        settings: { view: true, edit: true },
        billing: { view: true, edit: true },
        analytics: { view: true, export: true },
        system: { view: true, edit: true },
      },
    },
    manager: {
      name: "Manager",
      description: "Can manage users and view analytics",
      permissions: {
        dashboard: { view: true, edit: false },
        users: { view: true, create: true, edit: true, delete: false },
        projects: { view: true, create: true, edit: true, delete: false },
        settings: { view: true, edit: false },
        billing: { view: true, edit: false },
        analytics: { view: true, export: true },
        system: { view: false, edit: false },
      },
    },
    analyst: {
      name: "Analyst",
      description: "Can view and analyze data",
      permissions: {
        dashboard: { view: true, edit: false },
        users: { view: false, create: false, edit: false, delete: false },
        projects: { view: true, create: false, edit: false, delete: false },
        settings: { view: false, edit: false },
        billing: { view: false, edit: false },
        analytics: { view: true, export: true },
        system: { view: false, edit: false },
      },
    },
    user: {
      name: "User",
      description: "Standard user with basic access",
      permissions: {
        dashboard: { view: true, edit: false },
        users: { view: false, create: false, edit: false, delete: false },
        projects: { view: true, create: true, edit: true, delete: true },
        settings: { view: true, edit: false },
        billing: { view: false, edit: false },
        analytics: { view: false, export: false },
        system: { view: false, edit: false },
      },
    },
    guest: {
      name: "Guest",
      description: "Limited read-only access",
      permissions: {
        dashboard: { view: true, edit: false },
        users: { view: false, create: false, edit: false, delete: false },
        projects: { view: true, create: false, edit: false, delete: false },
        settings: { view: false, edit: false },
        billing: { view: false, edit: false },
        analytics: { view: false, export: false },
        system: { view: false, edit: false },
      },
    },
  };

  // Add component for showing detailed user permissions
  const PermissionsDisplay = ({ role, customPermissions = null }) => {
    const rolePermissions =
      customPermissions || ROLE_PERMISSIONS[role] || ROLE_PERMISSIONS.user;

    return (
      <div className="mt-4 space-y-4">
        <h4 className="text-lg font-medium">
          {rolePermissions.name} Permissions
        </h4>
        <p className="text-muted-foreground">{rolePermissions.description}</p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          {Object.entries(rolePermissions.permissions).map(
            ([category, perms]) => (
              <Card key={category} className="overflow-hidden">
                <CardHeader className="py-3">
                  <CardTitle className="text-base capitalize">
                    {category}
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0 pb-3">
                  <ul className="space-y-2">
                    {Object.entries(perms).map(([action, allowed]) => (
                      <li
                        key={action}
                        className="flex items-center justify-between"
                      >
                        <span className="capitalize text-sm">{action}</span>
                        {allowed ? (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            <Check className="h-3 w-3 mr-1" /> Allowed
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            <X className="h-3 w-3 mr-1" /> Restricted
                          </span>
                        )}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )
          )}
        </div>
      </div>
    );
  };

  // Component for role editor
  const RoleEditor = ({ role, onSave, onCancel }) => {
    const [roleName, setRoleName] = useState(role?.name || "");
    const [roleDescription, setRoleDescription] = useState(
      role?.description || ""
    );
    const [permissions, setPermissions] = useState(role?.permissions || {});

    const handlePermissionChange = (category, action, value) => {
      setPermissions({
        ...permissions,
        [category]: {
          ...permissions[category],
          [action]: value,
        },
      });
    };

    const handleSave = () => {
      onSave({
        id: role?.id || `role-${Date.now()}`,
        name: roleName,
        description: roleDescription,
        permissions,
      });
    };

    return (
      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="roleName">Role Name</Label>
          <Input
            id="roleName"
            value={roleName}
            onChange={(e) => setRoleName(e.target.value)}
            placeholder="e.g., Manager"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="roleDescription">Description</Label>
          <Input
            id="roleDescription"
            value={roleDescription}
            onChange={(e) => setRoleDescription(e.target.value)}
            placeholder="e.g., Can manage users and projects"
          />
        </div>

        <h4 className="font-medium mt-4">Permissions</h4>

        {Object.entries(ROLE_PERMISSIONS.user.permissions).map(
          ([category, actions]) => (
            <div key={category} className="mt-4">
              <h5 className="text-sm font-medium capitalize mb-2">
                {category}
              </h5>
              <div className="space-y-2 border rounded-md p-3">
                {Object.keys(actions).map((action) => (
                  <div
                    key={action}
                    className="flex items-center justify-between"
                  >
                    <span className="text-sm capitalize">{action}</span>
                    <Switch
                      checked={permissions[category]?.[action] || false}
                      onCheckedChange={(checked) =>
                        handlePermissionChange(category, action, checked)
                      }
                    />
                  </div>
                ))}
              </div>
            </div>
          )
        )}

        <div className="flex justify-end space-x-2 mt-6">
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button onClick={handleSave}>Save Role</Button>
        </div>
      </div>
    );
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
        <Button
          className="flex items-center gap-2"
          onClick={() => setShowAddUserDialog(true)}
        >
          <UserPlus className="h-4 w-4" />
          Add User
        </Button>
      </div>

      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
              <CardTitle>Users ({filteredUsers.length})</CardTitle>
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

                <div className="relative">
                  <Button
                    variant="outline"
                    className="flex items-center gap-1"
                    onClick={() => setRoleDropdownOpen(!roleDropdownOpen)}
                  >
                    <Filter className="h-4 w-4" />
                    <span className="hidden md:inline">Role</span>
                    <ChevronDown className="h-4 w-4" />
                  </Button>

                  {roleDropdownOpen && (
                    <div className="absolute right-0 mt-1 w-48 bg-white border rounded-md shadow-lg z-10">
                      <div className="p-1">
                        <button
                          className={`w-full text-left px-3 py-2 text-sm rounded-md ${
                            selectedRoleFilter === "all"
                              ? "bg-gray-100"
                              : "hover:bg-gray-50"
                          }`}
                          onClick={() => {
                            setSelectedRoleFilter("all");
                            setRoleDropdownOpen(false);
                          }}
                        >
                          All Roles
                        </button>
                        <button
                          className={`w-full text-left px-3 py-2 text-sm rounded-md ${
                            selectedRoleFilter === "admin"
                              ? "bg-gray-100"
                              : "hover:bg-gray-50"
                          }`}
                          onClick={() => {
                            setSelectedRoleFilter("admin");
                            setRoleDropdownOpen(false);
                          }}
                        >
                          Admin
                        </button>
                        <button
                          className={`w-full text-left px-3 py-2 text-sm rounded-md ${
                            selectedRoleFilter === "moderator"
                              ? "bg-gray-100"
                              : "hover:bg-gray-50"
                          }`}
                          onClick={() => {
                            setSelectedRoleFilter("moderator");
                            setRoleDropdownOpen(false);
                          }}
                        >
                          Moderator
                        </button>
                        <button
                          className={`w-full text-left px-3 py-2 text-sm rounded-md ${
                            selectedRoleFilter === "analyst"
                              ? "bg-gray-100"
                              : "hover:bg-gray-50"
                          }`}
                          onClick={() => {
                            setSelectedRoleFilter("analyst");
                            setRoleDropdownOpen(false);
                          }}
                        >
                          Analyst
                        </button>
                        <button
                          className={`w-full text-left px-3 py-2 text-sm rounded-md ${
                            selectedRoleFilter === "user"
                              ? "bg-gray-100"
                              : "hover:bg-gray-50"
                          }`}
                          onClick={() => {
                            setSelectedRoleFilter("user");
                            setRoleDropdownOpen(false);
                          }}
                        >
                          User
                        </button>
                      </div>
                    </div>
                  )}
                </div>

                <div className="relative">
                  <Button
                    variant="outline"
                    className="flex items-center gap-1"
                    onClick={() => setStatusDropdownOpen(!statusDropdownOpen)}
                  >
                    <Filter className="h-4 w-4" />
                    <span className="hidden md:inline">Status</span>
                    <ChevronDown className="h-4 w-4" />
                  </Button>

                  {statusDropdownOpen && (
                    <div className="absolute right-0 mt-1 w-48 bg-white border rounded-md shadow-lg z-10">
                      <div className="p-1">
                        <button
                          className={`w-full text-left px-3 py-2 text-sm rounded-md ${
                            selectedStatusFilter === "all"
                              ? "bg-gray-100"
                              : "hover:bg-gray-50"
                          }`}
                          onClick={() => {
                            setSelectedStatusFilter("all");
                            setStatusDropdownOpen(false);
                          }}
                        >
                          All Status
                        </button>
                        <button
                          className={`w-full text-left px-3 py-2 text-sm rounded-md ${
                            selectedStatusFilter === "active"
                              ? "bg-gray-100"
                              : "hover:bg-gray-50"
                          }`}
                          onClick={() => {
                            setSelectedStatusFilter("active");
                            setStatusDropdownOpen(false);
                          }}
                        >
                          Active
                        </button>
                        <button
                          className={`w-full text-left px-3 py-2 text-sm rounded-md ${
                            selectedStatusFilter === "inactive"
                              ? "bg-gray-100"
                              : "hover:bg-gray-50"
                          }`}
                          onClick={() => {
                            setSelectedStatusFilter("inactive");
                            setStatusDropdownOpen(false);
                          }}
                        >
                          Inactive
                        </button>
                        <button
                          className={`w-full text-left px-3 py-2 text-sm rounded-md ${
                            selectedStatusFilter === "blocked"
                              ? "bg-gray-100"
                              : "hover:bg-gray-50"
                          }`}
                          onClick={() => {
                            setSelectedStatusFilter("blocked");
                            setStatusDropdownOpen(false);
                          }}
                        >
                          Blocked
                        </button>
                      </div>
                    </div>
                  )}
                </div>

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
                        Last Active
                      </th>
                      <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsers.length === 0 ? (
                      <tr>
                        <td
                          colSpan="8"
                          className="p-4 text-center text-muted-foreground"
                        >
                          No users found matching your filters
                        </td>
                      </tr>
                    ) : (
                      filteredUsers.map((user) => (
                        <tr
                          key={user.id}
                          className="border-b transition-colors hover:bg-muted/50"
                        >
                          <td className="p-4 align-middle">
                            <div className="flex items-center gap-3">
                              <img
                                src={user.avatar}
                                alt={user.name}
                                className="h-8 w-8 rounded-full object-cover"
                              />
                              <span className="font-medium">{user.name}</span>
                            </div>
                          </td>
                          <td className="p-4 align-middle">
                            <div className="flex items-center gap-2">
                              <Mail className="h-4 w-4 text-muted-foreground" />
                              <span>{user.email}</span>
                            </div>
                          </td>
                          <td className="p-4 align-middle">
                            <div
                              className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${getRoleColor(
                                user.role
                              )} text-white`}
                            >
                              {user.role.charAt(0).toUpperCase() +
                                user.role.slice(1)}
                            </div>
                          </td>
                          <td className="p-4 align-middle">
                            <div
                              className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${getStatusColor(
                                user.status
                              )} text-white`}
                            >
                              {user.status.charAt(0).toUpperCase() +
                                user.status.slice(1)}
                            </div>
                          </td>
                          <td className="p-4 align-middle">{user.projects}</td>
                          <td className="p-4 align-middle">{user.joined}</td>
                          <td className="p-4 align-middle">
                            {user.lastActive}
                          </td>
                          <td className="p-4 align-middle">
                            <div className="flex items-center gap-2">
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => handleOpenEditUser(user)}
                                title="Edit user"
                              >
                                <Edit className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => handleToggleStatus(user.id)}
                                title={
                                  user.status === "active"
                                    ? "Deactivate user"
                                    : "Activate user"
                                }
                              >
                                {user.status === "active" ? (
                                  <Ban className="h-4 w-4" />
                                ) : (
                                  <Check className="h-4 w-4" />
                                )}
                              </Button>
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => openDeleteConfirmation(user)}
                                title="Delete user"
                              >
                                <Trash2 className="h-4 w-4 text-red-500" />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              Showing {filteredUsers.length} of {users.length} users
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={filteredUsers.length === 0}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={filteredUsers.length === 0}
              >
                Next
              </Button>
            </div>
          </CardFooter>
        </Card>
      </motion.div>

      {/* Add User Dialog */}
      {showAddUserDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-lg shadow-lg w-full max-w-md">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">Add New User</h2>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setShowAddUserDialog(false)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              <div className="space-y-4">
                <div>
                  <Label htmlFor="name">Full Name</Label>
                  <Input
                    id="name"
                    placeholder="John Doe"
                    value={newUser.name}
                    onChange={(e) =>
                      setNewUser({ ...newUser, name: e.target.value })
                    }
                  />
                </div>

                <div>
                  <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="john.doe@example.com"
                    value={newUser.email}
                    onChange={(e) =>
                      setNewUser({ ...newUser, email: e.target.value })
                    }
                  />
                </div>

                <div>
                  <Label htmlFor="password">Password</Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type="password"
                      placeholder="••••••••"
                      value={newUser.password}
                      onChange={(e) =>
                        setNewUser({ ...newUser, password: e.target.value })
                      }
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="role">Role</Label>
                  <select
                    id="role"
                    className="w-full rounded-md border border-input px-3 py-2"
                    value={newUser.role}
                    onChange={(e) =>
                      setNewUser({ ...newUser, role: e.target.value })
                    }
                  >
                    <option value="user">User</option>
                    <option value="moderator">Moderator</option>
                    <option value="analyst">Analyst</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>

                <div>
                  <Label htmlFor="status">Status</Label>
                  <select
                    id="status"
                    className="w-full rounded-md border border-input px-3 py-2"
                    value={newUser.status}
                    onChange={(e) =>
                      setNewUser({ ...newUser, status: e.target.value })
                    }
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="blocked">Blocked</option>
                  </select>
                </div>

                <div className="flex items-center space-x-2 pt-2">
                  <Switch id="send-welcome" defaultChecked />
                  <Label htmlFor="send-welcome">Send welcome email</Label>
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <Button
                  variant="outline"
                  onClick={() => setShowAddUserDialog(false)}
                >
                  Cancel
                </Button>
                <Button onClick={handleAddUser}>Add User</Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit User Dialog */}
      {showEditUserDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-lg shadow-lg w-full max-w-md">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">Edit User</h2>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setShowEditUserDialog(false)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              <div className="space-y-4">
                <div>
                  <Label htmlFor="edit-name">Full Name</Label>
                  <Input
                    id="edit-name"
                    placeholder="John Doe"
                    value={editUser.name}
                    onChange={(e) =>
                      setEditUser({ ...editUser, name: e.target.value })
                    }
                  />
                </div>

                <div>
                  <Label htmlFor="edit-email">Email Address</Label>
                  <Input
                    id="edit-email"
                    type="email"
                    placeholder="john.doe@example.com"
                    value={editUser.email}
                    onChange={(e) =>
                      setEditUser({ ...editUser, email: e.target.value })
                    }
                  />
                </div>

                <div>
                  <Label htmlFor="edit-role">Role</Label>
                  <select
                    id="edit-role"
                    className="w-full rounded-md border border-input px-3 py-2"
                    value={editUser.role}
                    onChange={(e) =>
                      setEditUser({ ...editUser, role: e.target.value })
                    }
                  >
                    <option value="user">User</option>
                    <option value="moderator">Moderator</option>
                    <option value="analyst">Analyst</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>

                <div>
                  <Label htmlFor="edit-status">Status</Label>
                  <select
                    id="edit-status"
                    className="w-full rounded-md border border-input px-3 py-2"
                    value={editUser.status}
                    onChange={(e) =>
                      setEditUser({ ...editUser, status: e.target.value })
                    }
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="blocked">Blocked</option>
                  </select>
                </div>

                <div className="pt-2">
                  <Button variant="outline" className="w-full">
                    <Lock className="h-4 w-4 mr-2" />
                    Reset Password
                  </Button>
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <Button
                  variant="outline"
                  onClick={() => setShowEditUserDialog(false)}
                >
                  Cancel
                </Button>
                <Button onClick={handleSaveEditUser}>Save Changes</Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      {showDeleteConfirm && selectedUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-lg shadow-lg w-full max-w-md">
            <div className="p-6">
              <div className="flex items-center mb-4 text-red-500">
                <AlertTriangle className="h-6 w-6 mr-2" />
                <h2 className="text-xl font-bold">Confirm Deletion</h2>
              </div>

              <p className="mb-4">
                Are you sure you want to delete the user{" "}
                <strong>{selectedUser.name}</strong>? This action cannot be
                undone.
              </p>

              <div className="flex justify-end space-x-3 mt-6">
                <Button
                  variant="outline"
                  onClick={() => setShowDeleteConfirm(false)}
                >
                  Cancel
                </Button>
                <Button variant="destructive" onClick={handleDeleteUser}>
                  Delete User
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Bulk Action Dialog */}
      {showBulkActionDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-lg shadow-lg w-full max-w-md">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">Bulk Action</h2>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setShowBulkActionDialog(false)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              <div className="space-y-4">
                <div>
                  <Label htmlFor="bulk-action">Select Action</Label>
                  <select
                    id="bulk-action"
                    className="w-full rounded-md border border-input px-3 py-2"
                    value={bulkAction}
                    onChange={(e) => setBulkAction(e.target.value)}
                  >
                    <option value="">-- Select an action --</option>
                    <option value="activate">Activate Users</option>
                    <option value="deactivate">Deactivate Users</option>
                    <option value="delete">Delete Users</option>
                    <option value="assign_role">Assign Role</option>
                    <option value="remove_role">Remove Role</option>
                  </select>
                </div>

                {bulkAction === "assign_role" && (
                  <div>
                    <Label htmlFor="role">Select Role</Label>
                    <select
                      id="role"
                      className="w-full rounded-md border border-input px-3 py-2"
                      value={bulkActionDetails.role}
                      onChange={(e) =>
                        setBulkActionDetails({
                          ...bulkActionDetails,
                          role: e.target.value,
                        })
                      }
                    >
                      <option value="">-- Select a role --</option>
                      <option value="admin">Admin</option>
                      <option value="moderator">Moderator</option>
                      <option value="analyst">Analyst</option>
                      <option value="user">User</option>
                    </select>
                  </div>
                )}

                {bulkAction === "remove_role" && (
                  <div>
                    <Label htmlFor="reason">Reason for removal</Label>
                    <Input
                      id="reason"
                      placeholder="Enter reason"
                      value={bulkActionDetails.reason}
                      onChange={(e) =>
                        setBulkActionDetails({
                          ...bulkActionDetails,
                          reason: e.target.value,
                        })
                      }
                    />
                  </div>
                )}

                <div className="flex justify-end space-x-3 mt-6">
                  <Button
                    variant="outline"
                    onClick={() => setShowBulkActionDialog(false)}
                  >
                    Cancel
                  </Button>
                  <Button onClick={executeBulkAction}>Apply Action</Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Security Settings Section */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle>Security Settings</CardTitle>
            <CardDescription>
              Configure security policies for user accounts
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Label
                  htmlFor="require-mfa"
                  className="flex items-center gap-2"
                >
                  <Switch
                    id="require-mfa"
                    checked={securitySettings.requireMfa}
                    onCheckedChange={(checked) =>
                      setSecuritySettings({
                        ...securitySettings,
                        requireMfa: checked,
                      })
                    }
                  />
                  Multi-factor authentication
                </Label>
                <p className="text-sm text-muted-foreground">
                  {securitySettings.requireMfa ? "Enabled" : "Disabled"}
                </p>
              </div>

              <div>
                <Label htmlFor="password-expiry">Password expiry (days)</Label>
                <Input
                  id="password-expiry"
                  type="number"
                  min="0"
                  value={securitySettings.passwordExpiryDays}
                  onChange={(e) =>
                    setSecuritySettings({
                      ...securitySettings,
                      passwordExpiryDays: e.target.value,
                    })
                  }
                />
              </div>

              <div>
                <Label htmlFor="max-login-attempts">Max login attempts</Label>
                <Input
                  id="max-login-attempts"
                  type="number"
                  min="0"
                  value={securitySettings.maxLoginAttempts}
                  onChange={(e) =>
                    setSecuritySettings({
                      ...securitySettings,
                      maxLoginAttempts: e.target.value,
                    })
                  }
                />
              </div>

              <div>
                <Label htmlFor="session-timeout">
                  Session timeout (minutes)
                </Label>
                <Input
                  id="session-timeout"
                  type="number"
                  min="1"
                  value={securitySettings.sessionTimeoutMinutes}
                  onChange={(e) =>
                    setSecuritySettings({
                      ...securitySettings,
                      sessionTimeoutMinutes: e.target.value,
                    })
                  }
                />
              </div>

              <div>
                <Label htmlFor="enforce-password-history">
                  Enforce password history
                </Label>
                <Input
                  id="enforce-password-history"
                  type="number"
                  min="0"
                  value={securitySettings.enforcePasswordHistory}
                  onChange={(e) =>
                    setSecuritySettings({
                      ...securitySettings,
                      enforcePasswordHistory: e.target.value,
                    })
                  }
                />
              </div>

              <Button
                variant="outline"
                onClick={() => toast.success("Security settings updated")}
              >
                Save Security Settings
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Activity Logs Section */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle>Activity Logs</CardTitle>
            <CardDescription>
              View user activity logs and audit trails
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {userActivityLogs.length === 0 ? (
                <p className="text-center text-muted-foreground py-4">
                  No activity logs found
                </p>
              ) : (
                <div className="rounded-md border">
                  <div className="relative w-full overflow-auto">
                    <table className="w-full caption-bottom text-sm">
                      <thead>
                        <tr className="border-b transition-colors hover:bg-muted/50">
                          <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                            User
                          </th>
                          <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                            Action
                          </th>
                          <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                            Timestamp
                          </th>
                          <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                            IP Address
                          </th>
                          <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                            User Agent
                          </th>
                          <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                            Status
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {userActivityLogs.map((log, index) => (
                          <tr
                            key={index}
                            className="border-b transition-colors hover:bg-muted/50"
                          >
                            <td className="p-4 align-middle">
                              <div className="flex items-center gap-3">
                                <img
                                  src={
                                    users.find((user) => user.id === log.userId)
                                      ?.avatar
                                  }
                                  alt={log.userId}
                                  className="h-8 w-8 rounded-full object-cover"
                                />
                                <span className="font-medium">
                                  {
                                    users.find((user) => user.id === log.userId)
                                      ?.name
                                  }
                                </span>
                              </div>
                            </td>
                            <td className="p-4 align-middle">{log.action}</td>
                            <td className="p-4 align-middle">
                              {new Date(log.timestamp).toLocaleString()}
                            </td>
                            <td className="p-4 align-middle">
                              {log.ipAddress}
                            </td>
                            <td className="p-4 align-middle">
                              {log.userAgent}
                            </td>
                            <td className="p-4 align-middle">
                              <div
                                className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${log.status === "success" ? "bg-green-500" : "bg-red-500"} text-white`}
                              >
                                {log.status.charAt(0).toUpperCase() +
                                  log.status.slice(1)}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Role Management Section */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle>Role Management</CardTitle>
            <CardDescription>
              Configure user roles and permissions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="roles">
              <TabsList>
                <TabsTrigger value="roles">Roles</TabsTrigger>
                <TabsTrigger value="permissions">Permissions</TabsTrigger>
              </TabsList>

              <TabsContent value="roles" className="pt-4">
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-4 border rounded-md hover:bg-gray-50">
                    <div>
                      <h3 className="font-medium flex items-center">
                        <Shield className="h-4 w-4 mr-2 text-red-500" />
                        Administrator
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        Full system access with all permissions
                      </p>
                    </div>
                    <Button variant="outline" size="sm">
                      Edit
                    </Button>
                  </div>

                  <div className="flex justify-between items-center p-4 border rounded-md hover:bg-gray-50">
                    <div>
                      <h3 className="font-medium flex items-center">
                        <Shield className="h-4 w-4 mr-2 text-amber-500" />
                        Moderator
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        Can review and manage user content
                      </p>
                    </div>
                    <Button variant="outline" size="sm">
                      Edit
                    </Button>
                  </div>

                  <div className="flex justify-between items-center p-4 border rounded-md hover:bg-gray-50">
                    <div>
                      <h3 className="font-medium flex items-center">
                        <Shield className="h-4 w-4 mr-2 text-purple-500" />
                        Analyst
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        Can view reports and analytics data
                      </p>
                    </div>
                    <Button variant="outline" size="sm">
                      Edit
                    </Button>
                  </div>

                  <div className="flex justify-between items-center p-4 border rounded-md hover:bg-gray-50">
                    <div>
                      <h3 className="font-medium flex items-center">
                        <Shield className="h-4 w-4 mr-2 text-blue-500" />
                        User
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        Standard access to platform features
                      </p>
                    </div>
                    <Button variant="outline" size="sm">
                      Edit
                    </Button>
                  </div>

                  <Button className="mt-2" variant="outline">
                    <Plus className="h-4 w-4 mr-2" />
                    Add New Role
                  </Button>
                </div>
              </TabsContent>

              <TabsContent value="permissions" className="pt-4">
                <div className="space-y-6">
                  <div>
                    <h3 className="font-medium mb-2">Projects</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <Label htmlFor="create-projects">Create projects</Label>
                        <div className="flex items-center gap-2">
                          <select className="text-xs border rounded p-1">
                            <option value="all">All roles</option>
                            <option value="admin">Admin only</option>
                            <option value="custom">Custom</option>
                          </select>
                        </div>
                      </div>
                      <div className="flex justify-between items-center">
                        <Label htmlFor="delete-projects">Delete projects</Label>
                        <div className="flex items-center gap-2">
                          <select className="text-xs border rounded p-1">
                            <option value="all">All roles</option>
                            <option value="admin">Admin only</option>
                            <option value="custom" selected>
                              Custom
                            </option>
                          </select>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="font-medium mb-2">Analysis</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <Label htmlFor="run-analysis">Run analysis</Label>
                        <div className="flex items-center gap-2">
                          <select className="text-xs border rounded p-1">
                            <option value="all" selected>
                              All roles
                            </option>
                            <option value="admin">Admin only</option>
                            <option value="custom">Custom</option>
                          </select>
                        </div>
                      </div>
                      <div className="flex justify-between items-center">
                        <Label htmlFor="export-analysis">Export analysis</Label>
                        <div className="flex items-center gap-2">
                          <select className="text-xs border rounded p-1">
                            <option value="all">All roles</option>
                            <option value="admin">Admin only</option>
                            <option value="custom" selected>
                              Custom
                            </option>
                          </select>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="font-medium mb-2">Administration</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <Label htmlFor="manage-users">Manage users</Label>
                        <div className="flex items-center gap-2">
                          <select className="text-xs border rounded p-1">
                            <option value="all">All roles</option>
                            <option value="admin" selected>
                              Admin only
                            </option>
                            <option value="custom">Custom</option>
                          </select>
                        </div>
                      </div>
                      <div className="flex justify-between items-center">
                        <Label htmlFor="system-settings">System settings</Label>
                        <div className="flex items-center gap-2">
                          <select className="text-xs border rounded p-1">
                            <option value="all">All roles</option>
                            <option value="admin" selected>
                              Admin only
                            </option>
                            <option value="custom">Custom</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  </div>

                  <Button variant="outline">Save Permission Settings</Button>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
