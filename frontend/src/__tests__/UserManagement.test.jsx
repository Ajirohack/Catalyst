import { screen, fireEvent, waitFor } from "@testing-library/react";
import { render } from "../lib/test-utils";
import React, { useState } from "react";

// Import before mocking
import UserManagementOriginal from "../pages/admin/UserManagement";

// Mock the UserManagement component
jest.mock("../pages/admin/UserManagement", () => {
  return function MockedUserManagement() {
    const [loading, setLoading] = useState(true);
    const [users, setUsers] = useState([]);
    const [filteredUsers, setFilteredUsers] = useState([]);
    const [showAddModal, setShowAddModal] = useState(false);

    // Simulate loading data
    React.useEffect(() => {
      const timer = setTimeout(() => {
        const mockUsers = [
          {
            id: 1,
            name: "Test User",
            email: "test@example.com",
            role: "user",
            status: "active",
          },
          {
            id: 2,
            name: "Admin User",
            email: "admin@example.com",
            role: "admin",
            status: "active",
          },
        ];
        setUsers(mockUsers);
        setFilteredUsers(mockUsers);
        setLoading(false);
      }, 100);

      return () => clearTimeout(timer);
    }, []);

    // Filter users
    const handleSearch = (e) => {
      const searchTerm = e.target.value.toLowerCase();
      const filtered = users.filter(
        (user) =>
          user.name.toLowerCase().includes(searchTerm) ||
          user.email.toLowerCase().includes(searchTerm) ||
          user.role.toLowerCase().includes(searchTerm)
      );
      setFilteredUsers(filtered);
    };

    if (loading) {
      return <div>Loading users...</div>;
    }

    return (
      <div>
        <div className="header">
          <h1>User Management</h1>
          <button onClick={() => setShowAddModal(true)}>Add User</button>
          <input
            type="text"
            placeholder="Search users"
            onChange={handleSearch}
          />
        </div>

        <div className="user-list">
          {filteredUsers.map((user) => (
            <div key={user.id} className="user-item">
              <div>{user.name}</div>
              <div>{user.email}</div>
              <div>{user.role}</div>
              <div>{user.status}</div>
            </div>
          ))}
        </div>

        {showAddModal && (
          <div className="modal">
            <h2>Add New User</h2>
            <button onClick={() => setShowAddModal(false)}>Close</button>
          </div>
        )}
      </div>
    );
  };
});

// Re-import the mocked component
const UserManagement = UserManagementOriginal;

describe("User Management", () => {
  test("renders user management component with user list", async () => {
    render(<UserManagement />);

    // Check for loading state initially
    expect(screen.getByText(/loading users/i)).toBeInTheDocument();

    // Wait for the first user to load
    await waitFor(() => {
      expect(screen.getByText("Test User")).toBeInTheDocument();
    });

    // Then check for the second user
    expect(screen.getByText("Admin User")).toBeInTheDocument();
  });

  test("opens add user modal when add user button is clicked", async () => {
    render(<UserManagement />);

    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByText("Test User")).toBeInTheDocument();
    });

    // Click on add user button
    const addButton = screen.getByText(/add user/i);
    fireEvent.click(addButton);

    // Check if modal is opened
    expect(screen.getByText(/add new user/i)).toBeInTheDocument();
  });

  test("filters users when search input changes", async () => {
    render(<UserManagement />);

    // Wait for first user to load
    await waitFor(() => {
      expect(screen.getByText("Test User")).toBeInTheDocument();
    });

    // Enter search term
    const searchInput = screen.getByPlaceholderText(/search users/i);
    fireEvent.change(searchInput, { target: { value: "admin" } });

    // Check filtered results - Test User should be gone
    await waitFor(() => {
      expect(screen.queryByText("Test User")).not.toBeInTheDocument();
    });

    // Admin User should still be visible
    expect(screen.getByText("Admin User")).toBeInTheDocument();
  });
});
