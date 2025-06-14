import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  CircularProgress,
  Pagination,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
  Menu,
  ListItemIcon,
  ListItemText,
  Divider,
  Paper,
  Avatar,
  LinearProgress
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Add as AddIcon,
  MoreVert as MoreVertIcon,
  PlayArrow as PlayIcon,
  Edit as EditIcon,
  Archive as ArchiveIcon,
  Unarchive as UnarchiveIcon,
  Delete as DeleteIcon,
  Psychology as PsychologyIcon,
  Favorite as FavoriteIcon,
  Business as BusinessIcon,
  School as SchoolIcon,
  Group as GroupIcon,
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
  RadioButtonUnchecked as RadioButtonUncheckedIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import ProjectCard from '../components/ProjectCard';

const ROLE_ICONS = {
  romantic_partner: <FavoriteIcon />,
  business_partner: <BusinessIcon />,
  friend: <GroupIcon />,
  family_member: <FavoriteIcon />,
  colleague: <BusinessIcon />,
  mentor_mentee: <SchoolIcon />,
  other: <GroupIcon />
};

const STATUS_COLORS = {
  active: 'success',
  paused: 'warning',
  completed: 'info',
  archived: 'default'
};

const ContinueProject = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [filteredProjects, setFilteredProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [roleFilter, setRoleFilter] = useState('all');
  const [sortBy, setSortBy] = useState('updated_at');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedProject, setSelectedProject] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [menuAnchor, setMenuAnchor] = useState(null);
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    completed: 0,
    archived: 0
  });

  const itemsPerPage = 9;

  useEffect(() => {
    fetchProjects();
    fetchStats();
  }, [page, sortBy]);

  useEffect(() => {
    filterProjects();
  }, [projects, searchTerm, statusFilter, roleFilter]);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/projects/', {
        params: {
          page,
          limit: itemsPerPage,
          sort_by: sortBy,
          order: 'desc'
        }
      });
      setProjects(response.data.projects || []);
      setTotalPages(Math.ceil((response.data.total || 0) / itemsPerPage));
    } catch (err) {
      setError('Failed to load projects. Please try again.');
      console.error('Error fetching projects:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/projects/stats');
      setStats(response.data);
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  const filterProjects = () => {
    let filtered = [...projects];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(project =>
        project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project.partner_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(project => project.status === statusFilter);
    }

    // Role filter
    if (roleFilter !== 'all') {
      filtered = filtered.filter(project => project.role === roleFilter);
    }

    setFilteredProjects(filtered);
  };

  const handleProjectAction = async (projectId, action) => {
    try {
      let endpoint = '';
      let data = {};

      switch (action) {
        case 'continue':
          // Navigate to project dashboard or analysis page
          navigate(`/project/${projectId}`);
          return;
        case 'pause':
          endpoint = `/api/projects/${projectId}/status`;
          data = { status: 'paused' };
          break;
        case 'resume':
          endpoint = `/api/projects/${projectId}/status`;
          data = { status: 'active' };
          break;
        case 'complete':
          endpoint = `/api/projects/${projectId}/status`;
          data = { status: 'completed' };
          break;
        case 'archive':
          endpoint = `/api/projects/${projectId}/status`;
          data = { status: 'archived' };
          break;
        case 'unarchive':
          endpoint = `/api/projects/${projectId}/status`;
          data = { status: 'active' };
          break;
        default:
          return;
      }

      await axios.patch(`http://localhost:8000${endpoint}`, data);
      fetchProjects();
      fetchStats();
      setMenuAnchor(null);
    } catch (err) {
      setError(`Failed to ${action} project. Please try again.`);
    }
  };

  const handleDeleteProject = async () => {
    if (!selectedProject) return;

    try {
      await axios.delete(`http://localhost:8000/api/projects/${selectedProject.id}`);
      fetchProjects();
      fetchStats();
      setDeleteDialogOpen(false);
      setSelectedProject(null);
    } catch (err) {
      setError('Failed to delete project. Please try again.');
    }
  };

  const handleMenuOpen = (event, project) => {
    setMenuAnchor(event.currentTarget);
    setSelectedProject(project);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
    setSelectedProject(null);
  };

  const getProjectProgress = (project) => {
    if (!project.goals || project.goals.length === 0) return 0;
    const completedGoals = project.goals.filter(goal => goal.completed).length;
    return Math.round((completedGoals / project.goals.length) * 100);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getTimeSince = (dateString) => {
    const now = new Date();
    const date = new Date(dateString);
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
    return `${Math.ceil(diffDays / 30)} months ago`;
  };

  if (loading && projects.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Box sx={{ p: 3 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <PsychologyIcon color="primary" />
            Your Projects
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Continue working on your relationship projects and track your progress
          </Typography>
        </Box>

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h4" color="primary">
                      {stats.total}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Projects
                    </Typography>
                  </Box>
                  <PsychologyIcon sx={{ fontSize: 40, color: 'primary.main', opacity: 0.3 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h4" color="success.main">
                      {stats.active}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Active
                    </Typography>
                  </Box>
                  <PlayIcon sx={{ fontSize: 40, color: 'success.main', opacity: 0.3 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h4" color="info.main">
                      {stats.completed}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Completed
                    </Typography>
                  </Box>
                  <CheckCircleIcon sx={{ fontSize: 40, color: 'info.main', opacity: 0.3 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h4" color="text.secondary">
                      {stats.archived}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Archived
                    </Typography>
                  </Box>
                  <ArchiveIcon sx={{ fontSize: 40, color: 'text.secondary', opacity: 0.3 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Filters and Search */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Search projects..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  )
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  label="Status"
                >
                  <MenuItem value="all">All Status</MenuItem>
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="paused">Paused</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="archived">Archived</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth>
                <InputLabel>Role</InputLabel>
                <Select
                  value={roleFilter}
                  onChange={(e) => setRoleFilter(e.target.value)}
                  label="Role"
                >
                  <MenuItem value="all">All Roles</MenuItem>
                  <MenuItem value="romantic_partner">Romantic Partner</MenuItem>
                  <MenuItem value="business_partner">Business Partner</MenuItem>
                  <MenuItem value="friend">Friend</MenuItem>
                  <MenuItem value="family_member">Family Member</MenuItem>
                  <MenuItem value="colleague">Colleague</MenuItem>
                  <MenuItem value="mentor_mentee">Mentor/Mentee</MenuItem>
                  <MenuItem value="other">Other</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth>
                <InputLabel>Sort By</InputLabel>
                <Select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  label="Sort By"
                >
                  <MenuItem value="updated_at">Last Updated</MenuItem>
                  <MenuItem value="created_at">Date Created</MenuItem>
                  <MenuItem value="name">Name</MenuItem>
                  <MenuItem value="status">Status</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => navigate('/new')}
                sx={{ height: 56 }}
              >
                New Project
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Projects Grid */}
        {filteredProjects.length === 0 ? (
          <Paper sx={{ p: 6, textAlign: 'center' }}>
            <PsychologyIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              {projects.length === 0 ? 'No projects yet' : 'No projects match your filters'}
            </Typography>
            <Typography variant="body1" color="text.secondary" gutterBottom>
              {projects.length === 0
                ? 'Create your first relationship project to get started with AI-powered coaching'
                : 'Try adjusting your search or filter criteria'
              }
            </Typography>
            {projects.length === 0 && (
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => navigate('/new')}
                sx={{ mt: 2 }}
              >
                Create Your First Project
              </Button>
            )}
          </Paper>
        ) : (
          <>
            <Grid container spacing={3}>
              <AnimatePresence>
                {filteredProjects.map((project, index) => (
                  <Grid item xs={12} sm={6} lg={4} key={project.id}>
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                    >
                      <Card
                        sx={{
                          height: '100%',
                          display: 'flex',
                          flexDirection: 'column',
                          cursor: 'pointer',
                          transition: 'all 0.3s ease',
                          '&:hover': {
                            transform: 'translateY(-4px)',
                            boxShadow: 4
                          }
                        }}
                        onClick={() => handleProjectAction(project.id, 'continue')}
                      >
                        <CardContent sx={{ flexGrow: 1 }}>
                          {/* Header */}
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                                {ROLE_ICONS[project.role] || <GroupIcon />}
                              </Avatar>
                              <Box>
                                <Typography variant="h6" noWrap sx={{ maxWidth: 150 }}>
                                  {project.name}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {project.platform}
                                </Typography>
                              </Box>
                            </Box>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Chip
                                label={project.status}
                                color={STATUS_COLORS[project.status]}
                                size="small"
                                sx={{ textTransform: 'capitalize' }}
                              />
                              <IconButton
                                size="small"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleMenuOpen(e, project);
                                }}
                              >
                                <MoreVertIcon />
                              </IconButton>
                            </Box>
                          </Box>

                          {/* Partner */}
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            <strong>Partner:</strong> {project.partner_name || 'Not specified'}
                          </Typography>

                          {/* Description */}
                          {project.description && (
                            <Typography
                              variant="body2"
                              color="text.secondary"
                              sx={{
                                mb: 2,
                                display: '-webkit-box',
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: 'vertical',
                                overflow: 'hidden'
                              }}
                            >
                              {project.description}
                            </Typography>
                          )}

                          {/* Goals Progress */}
                          {project.goals && project.goals.length > 0 && (
                            <Box sx={{ mb: 2 }}>
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                                <Typography variant="body2" color="text.secondary">
                                  Goals Progress
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                  {project.goals.filter(g => g.completed).length}/{project.goals.length}
                                </Typography>
                              </Box>
                              <LinearProgress
                                variant="determinate"
                                value={getProjectProgress(project)}
                                sx={{ height: 6, borderRadius: 3 }}
                              />
                            </Box>
                          )}

                          {/* Dates */}
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 'auto' }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                              <ScheduleIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                              <Typography variant="caption" color="text.secondary">
                                {getTimeSince(project.updated_at)}
                              </Typography>
                            </Box>
                            <Typography variant="caption" color="text.secondary">
                              Created {formatDate(project.created_at)}
                            </Typography>
                          </Box>
                        </CardContent>
                      </Card>
                    </motion.div>
                  </Grid>
                ))}
              </AnimatePresence>
            </Grid>

            {/* Pagination */}
            {totalPages > 1 && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                <Pagination
                  count={totalPages}
                  page={page}
                  onChange={(e, value) => setPage(value)}
                  color="primary"
                  size="large"
                />
              </Box>
            )}
          </>
        )}

        {/* Context Menu */}
        <Menu
          anchorEl={menuAnchor}
          open={Boolean(menuAnchor)}
          onClose={handleMenuClose}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        >
          <MenuItem onClick={() => handleProjectAction(selectedProject?.id, 'continue')}>
            <ListItemIcon>
              <PlayIcon />
            </ListItemIcon>
            <ListItemText>Continue Project</ListItemText>
          </MenuItem>
          <MenuItem onClick={() => navigate(`/project/${selectedProject?.id}/edit`)}>
            <ListItemIcon>
              <EditIcon />
            </ListItemIcon>
            <ListItemText>Edit Project</ListItemText>
          </MenuItem>
          <Divider />
          {selectedProject?.status === 'active' && (
            <MenuItem onClick={() => handleProjectAction(selectedProject?.id, 'pause')}>
              <ListItemIcon>
                <RadioButtonUncheckedIcon />
              </ListItemIcon>
              <ListItemText>Pause Project</ListItemText>
            </MenuItem>
          )}
          {selectedProject?.status === 'paused' && (
            <MenuItem onClick={() => handleProjectAction(selectedProject?.id, 'resume')}>
              <ListItemIcon>
                <PlayIcon />
              </ListItemIcon>
              <ListItemText>Resume Project</ListItemText>
            </MenuItem>
          )}
          {selectedProject?.status !== 'completed' && (
            <MenuItem onClick={() => handleProjectAction(selectedProject?.id, 'complete')}>
              <ListItemIcon>
                <CheckCircleIcon />
              </ListItemIcon>
              <ListItemText>Mark Complete</ListItemText>
            </MenuItem>
          )}
          <Divider />
          {selectedProject?.status !== 'archived' ? (
            <MenuItem onClick={() => handleProjectAction(selectedProject?.id, 'archive')}>
              <ListItemIcon>
                <ArchiveIcon />
              </ListItemIcon>
              <ListItemText>Archive Project</ListItemText>
            </MenuItem>
          ) : (
            <MenuItem onClick={() => handleProjectAction(selectedProject?.id, 'unarchive')}>
              <ListItemIcon>
                <UnarchiveIcon />
              </ListItemIcon>
              <ListItemText>Unarchive Project</ListItemText>
            </MenuItem>
          )}
          <Divider />
          <MenuItem
            onClick={() => {
              setDeleteDialogOpen(true);
              handleMenuClose();
            }}
            sx={{ color: 'error.main' }}
          >
            <ListItemIcon>
              <DeleteIcon sx={{ color: 'error.main' }} />
            </ListItemIcon>
            <ListItemText>Delete Project</ListItemText>
          </MenuItem>
        </Menu>

        {/* Delete Confirmation Dialog */}
        <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
          <DialogTitle>Delete Project</DialogTitle>
          <DialogContent>
            <Typography>
              Are you sure you want to delete "{selectedProject?.name}"? This action cannot be undone.
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleDeleteProject} color="error" variant="contained">
              Delete
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </motion.div>
  );
};

export default ContinueProject;