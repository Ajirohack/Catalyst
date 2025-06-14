import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';

// Components
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import WhisperPanel from './components/WhisperPanel';

// Pages
import Dashboard from './pages/Dashboard';
import NewProject from './pages/NewProject';
import ContinueProject from './pages/ContinueProject';
import Timeline from './pages/Timeline';
import ProjectDetails from './pages/ProjectDetails';
import Analytics from './pages/Analytics';

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#6366f1',
      light: '#818cf8',
      dark: '#4f46e5',
    },
    secondary: {
      main: '#ec4899',
      light: '#f472b6',
      dark: '#db2777',
    },
    background: {
      default: '#f8fafc',
      paper: '#ffffff',
    },
    text: {
      primary: '#1e293b',
      secondary: '#64748b',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 600,
    },
    h4: {
      fontSize: '1.25rem',
      fontWeight: 600,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          fontWeight: 500,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
          borderRadius: 12,
        },
      },
    },
  },
});

// Create query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  const [whisperPanelOpen, setWhisperPanelOpen] = React.useState(false);
  const [selectedProject, setSelectedProject] = React.useState(null);

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Box sx={{ display: 'flex', minHeight: '100vh' }}>
            {/* Sidebar */}
            <Sidebar 
              onWhisperToggle={() => setWhisperPanelOpen(!whisperPanelOpen)}
              selectedProject={selectedProject}
              onProjectSelect={setSelectedProject}
            />
            
            {/* Main Content */}
            <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
              {/* Header */}
              <Header 
                onWhisperToggle={() => setWhisperPanelOpen(!whisperPanelOpen)}
                whisperPanelOpen={whisperPanelOpen}
              />
              
              {/* Page Content */}
              <Box 
                component="main" 
                sx={{ 
                  flexGrow: 1, 
                  p: 3,
                  backgroundColor: 'background.default',
                  minHeight: 'calc(100vh - 64px)'
                }}
              >
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/new-project" element={<NewProject />} />
                  <Route path="/continue-project" element={<ContinueProject />} />
                  <Route path="/project/:id" element={<ProjectDetails />} />
                  <Route path="/timeline" element={<Timeline />} />
                  <Route path="/analytics" element={<Analytics />} />
                </Routes>
              </Box>
            </Box>
            
            {/* Whisper Panel */}
            <WhisperPanel 
              open={whisperPanelOpen}
              onClose={() => setWhisperPanelOpen(false)}
              selectedProject={selectedProject}
            />
          </Box>
        </Router>
        
        {/* Toast notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              theme: {
                primary: '#4aed88',
              },
            },
          }}
        />
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;