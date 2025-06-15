// Legacy compatibility - use AuthContext instead
// import { useAuth } from "./AuthContext";

export function getUserRole() {
  // Temporary mock: return 'admin' or 'user'
  // TODO: Replace with useAuth hook in components
  return "user"; // Change to 'admin' to test admin layout
}

// Export the new context for migration
export { useAuth, AuthProvider } from "./AuthContext";
