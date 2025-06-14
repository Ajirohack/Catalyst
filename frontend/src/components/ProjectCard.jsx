import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Chip,
  Box,
  LinearProgress,
  Avatar,
  IconButton,
  Menu,
  MenuItem
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  Person as PersonIcon,
  Schedule as ScheduleIcon,
  TrendingUp as TrendingUpIcon,
  Chat as ChatIcon
} from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';

const ProjectCard = ({ 
  project, 
  onEdit, 
  onDelete, 
  onArchive, 
  onContinue 
}) => {
  const [anchorEl, setAnchorEl] = React.useState(null);
  const open = Boolean(anchorEl);

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'paused':
        return 'warning';
      case 'completed':
        return 'info';
      case 'archived':
        return 'default';
      default:
        return 'default';
    }
  };

  const getPlatformIcon = (platform) => {
    switch (platform.toLowerCase()) {
      case 'whatsapp':
        return '💬';
      case 'messenger':
        return '📱';
      case 'discord':
        return '🎮';
      case 'slack':
        return '💼';
      case 'teams':
        return '👥';
      case 'telegram':
        return '✈️';
      case 'sms':
        return '📱';
      case 'email':
        return '📧';
      default:
        return '💬';
    }
  };

  const calculateProgress = () => {
    if (!project.goals || project.goals.length === 0) return 0;
    const completedGoals = project.goals.filter(goal => goal.completed).length;
    return (completedGoals / project.goals.length) * 100;
  };

  const getTimeAgo = (date) => {
    if (!date) return 'Never';
    return formatDistanceToNow(new Date(date), { addSuffix: true });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ y: -4 }}
    >
      <Card 
        sx={{ 
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          '&:hover': {
            boxShadow: 6,
          },
          borderRadius: 2,
          overflow: 'visible'
        }}
      >
        {/* Header */}
        <Box sx={{ p: 2, pb: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Avatar sx={{ width: 32, height: 32, fontSize: '1rem' }}>
                {getPlatformIcon(project.platform)}
              </Avatar>
              <Box>
                <Typography variant="h6" component="h3" sx={{ fontWeight: 600, lineHeight: 1.2 }}>
                  {project.name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {project.role} • {project.platform}
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip 
                label={project.status} 
                color={getStatusColor(project.status)}
                size="small"
                sx={{ textTransform: 'capitalize' }}
              />
              <IconButton
                size="small"
                onClick={handleMenuClick}
                sx={{ opacity: 0.7, '&:hover': { opacity: 1 } }}
              >
                <MoreVertIcon fontSize="small" />
              </IconButton>
            </Box>
          </Box>

          {project.partner_name && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
              <PersonIcon fontSize="small" color="action" />
              <Typography variant="body2" color="text.secondary">
                {project.partner_name}
              </Typography>
            </Box>
          )}
        </Box>

        {/* Content */}
        <CardContent sx={{ flexGrow: 1, pt: 0 }}>
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
                value={calculateProgress()} 
                sx={{ 
                  height: 6, 
                  borderRadius: 3,
                  backgroundColor: 'grey.200',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 3
                  }
                }}
              />
            </Box>
          )}

          {/* Stats */}
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <ScheduleIcon fontSize="small" color="action" />
              <Typography variant="caption" color="text.secondary">
                Created {getTimeAgo(project.created_at)}
              </Typography>
            </Box>
            
            {project.last_activity && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <TrendingUpIcon fontSize="small" color="action" />
                <Typography variant="caption" color="text.secondary">
                  Active {getTimeAgo(project.last_activity)}
                </Typography>
              </Box>
            )}
          </Box>
        </CardContent>

        {/* Actions */}
        <CardActions sx={{ p: 2, pt: 0 }}>
          <Button 
            variant="contained" 
            fullWidth
            startIcon={<ChatIcon />}
            onClick={() => onContinue(project)}
            sx={{ 
              borderRadius: 2,
              textTransform: 'none',
              fontWeight: 600
            }}
          >
            Continue Project
          </Button>
        </CardActions>

        {/* Menu */}
        <Menu
          anchorEl={anchorEl}
          open={open}
          onClose={handleMenuClose}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        >
          <MenuItem onClick={() => { onEdit(project); handleMenuClose(); }}>
            Edit Project
          </MenuItem>
          <MenuItem onClick={() => { onArchive(project); handleMenuClose(); }}>
            {project.status === 'archived' ? 'Unarchive' : 'Archive'}
          </MenuItem>
          <MenuItem 
            onClick={() => { onDelete(project); handleMenuClose(); }}
            sx={{ color: 'error.main' }}
          >
            Delete Project
          </MenuItem>
        </Menu>
      </Card>
    </motion.div>
  );
};

export default ProjectCard;