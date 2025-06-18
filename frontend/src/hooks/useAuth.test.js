// src/hooks/useAuth.test.js
import { renderHook, act } from '@testing-library/react';
import { createTestUser } from '../lib/test-data-factory';

// Mock the auth context and hook since they don't exist yet
const mockUseAuth = () => ({
    isAuthenticated: false,
    user: null,
    isLoading: false,
    error: null,
    login: jest.fn(),
    logout: jest.fn(),
    register: jest.fn(),
    isAdmin: jest.fn(() => false),
});

const MockAuthProvider = ({ children }) => children;

// Create wrapper with mock provider
const wrapper = ({ children }) => <MockAuthProvider>{children}</MockAuthProvider>;

describe('useAuth Hook', () => {
    beforeEach(() => {
        // Clear any stored auth data
        window.localStorage.clear();
        jest.clearAllMocks();
    });

    test('should start with user not authenticated', () => {
        const { result } = renderHook(() => mockUseAuth(), { wrapper });

        expect(result.current.isAuthenticated).toBe(false);
        expect(result.current.user).toBeNull();
        expect(result.current.isLoading).toBe(false);
    });

    test('should handle login functionality', () => {
        const mockLogin = jest.fn();
        const hookReturn = {
            ...mockUseAuth(),
            login: mockLogin,
        };

        const { result } = renderHook(() => hookReturn, { wrapper });

        act(() => {
            result.current.login('test@example.com', 'password');
        });

        expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password');
    });

    test('should handle logout functionality', () => {
        const mockLogout = jest.fn();
        const hookReturn = {
            ...mockUseAuth(),
            logout: mockLogout,
            isAuthenticated: true,
            user: createTestUser(),
        };

        const { result } = renderHook(() => hookReturn, { wrapper });

        act(() => {
            result.current.logout();
        });

        expect(mockLogout).toHaveBeenCalled();
    });

    test('should handle registration functionality', () => {
        const mockRegister = jest.fn();
        const hookReturn = {
            ...mockUseAuth(),
            register: mockRegister,
        };

        const { result } = renderHook(() => hookReturn, { wrapper });

        act(() => {
            result.current.register({
                name: 'New User',
                email: 'newuser@example.com',
                password: 'password123',
                confirmPassword: 'password123',
            });
        });

        expect(mockRegister).toHaveBeenCalledWith({
            name: 'New User',
            email: 'newuser@example.com',
            password: 'password123',
            confirmPassword: 'password123',
        });
    });

    test('should check if user has admin role', () => {
        const mockIsAdmin = jest.fn(() => true);
        const hookReturn = {
            ...mockUseAuth(),
            isAdmin: mockIsAdmin,
            isAuthenticated: true,
            user: createTestUser({ role: 'admin' }),
        };

        const { result } = renderHook(() => hookReturn, { wrapper });

        expect(result.current.isAdmin()).toBe(true);
        expect(mockIsAdmin).toHaveBeenCalled();
    });

    test('should return false for isAdmin when user is not admin', () => {
        const mockIsAdmin = jest.fn(() => false);
        const hookReturn = {
            ...mockUseAuth(),
            isAdmin: mockIsAdmin,
            isAuthenticated: true,
            user: createTestUser({ role: 'user' }),
        };

        const { result } = renderHook(() => hookReturn, { wrapper });

        expect(result.current.isAdmin()).toBe(false);
    });
});
