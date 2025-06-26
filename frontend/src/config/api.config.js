// API Configuration for different environments

// Environment detection
const getEnvironment = () => {
  if (process.env.NODE_ENV === 'production') {
    return 'production';
  } else if (process.env.NODE_ENV === 'test') {
    return 'test';
  }
  return 'development';
};

// Configuration for different environments
const environments = {
  development: {
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
    timeout: 10000,
    environment: 'development',
    features: {
      requestLogging: true,
      responseLogging: true,
      errorReporting: true,
    },
  },
  test: {
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
    timeout: 5000,
    environment: 'test',
    features: {
      requestLogging: false,
      responseLogging: false,
      errorReporting: false,
    },
  },
  production: {
    baseURL: process.env.REACT_APP_API_URL || 'https://api.catalyst.com',
    timeout: 15000,
    environment: 'production',
    features: {
      requestLogging: false,
      responseLogging: false,
      errorReporting: true,
    },
  },
};

// API endpoints
const endpoints = {
  // Authentication
  auth: {
    login: '/auth/login',
    register: '/auth/register',
    logout: '/auth/logout',
    refresh: '/auth/refresh',
    forgotPassword: '/auth/forgot-password',
    resetPassword: '/auth/reset-password',
    verifyEmail: '/auth/verify-email',
  },
  
  // Projects
  projects: {
    list: '/projects',
    create: '/projects',
    get: (id) => `/projects/${id}`,
    update: (id) => `/projects/${id}`,
    delete: (id) => `/projects/${id}`,
    analyze: (id) => `/projects/${id}/analyze`,
  },
  
  // Analysis
  analysis: {
    list: '/analysis',
    create: '/analysis',
    get: (id) => `/analysis/${id}`,
    results: (id) => `/analysis/${id}/results`,
    status: (id) => `/analysis/${id}/status`,
  },
  
  // Knowledge Base
  knowledgeBase: {
    list: '/knowledge-base',
    upload: '/knowledge-base/upload',
    search: '/knowledge-base/search',
    get: (id) => `/knowledge-base/${id}`,
    delete: (id) => `/knowledge-base/${id}`,
  },
  
  // AI Providers
  aiProviders: {
    list: '/ai-providers',
    create: '/ai-providers',
    get: (id) => `/ai-providers/${id}`,
    update: (id) => `/ai-providers/${id}`,
    delete: (id) => `/ai-providers/${id}`,
    test: (id) => `/ai-providers/${id}/test`,
  },
  
  // Admin
  admin: {
    users: '/admin/users',
    analytics: '/admin/analytics',
    logs: '/admin/logs',
    system: '/admin/system',
  },
};

// Get API configuration based on environment
export const getApiConfig = () => {
  const env = getEnvironment();
  return environments[env];
};

// Get specific endpoint
export const getEndpoint = (path) => {
  const keys = path.split('.');
  let endpoint = endpoints;
  
  for (const key of keys) {
    if (endpoint[key]) {
      endpoint = endpoint[key];
    } else {
      throw new Error(`Endpoint not found: ${path}`);
    }
  }
  
  return endpoint;
};

// Export default configuration
const apiConfig = {
  getApiConfig,
  getEndpoint,
  environments,
  endpoints,
};

export default apiConfig;