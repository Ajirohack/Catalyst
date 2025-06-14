import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
  Grid,
  Divider,
  IconButton,
  Tooltip,
  FormHelperText,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Info as InfoIcon,
  Psychology as PsychologyIcon,
  Favorite as FavoriteIcon,
  Business as BusinessIcon,
  School as SchoolIcon,
  Group as GroupIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const PLATFORMS = [
  { value: 'whatsapp', label: 'WhatsApp', icon: '💬' },
  { value: 'telegram', label: 'Telegram', icon: '✈️' },
  { value: 'discord', label: 'Discord', icon: '🎮' },
  { value: 'slack', label: 'Slack', icon: '💼' },
  { value: 'email', label: 'Email', icon: '📧' },
  { value: 'sms', label: 'SMS', icon: '📱' },
  { value: 'other', label: 'Other', icon: '🔗' }
];

const ROLES = [
  { value: 'romantic_partner', label: 'Romantic Partner', icon: <FavoriteIcon />, description: 'Dating, relationships, marriage' },
  { value: 'business_partner', label: 'Business Partner', icon: <BusinessIcon />, description: 'Professional collaborations, negotiations' },
  { value: 'friend', label: 'Friend', icon: <GroupIcon />, description: 'Personal friendships, social connections' },
  { value: 'family_member', label: 'Family Member', icon: <FavoriteIcon />, description: 'Parents, siblings, relatives' },
  { value: 'colleague', label: 'Colleague', icon: <BusinessIcon />, description: 'Work relationships, team members' },
  { value: 'mentor_mentee', label: 'Mentor/Mentee', icon: <SchoolIcon />, description: 'Learning and guidance relationships' },
  { value: 'other', label: 'Other', icon: <GroupIcon />, description: 'Custom relationship type' }
];

const steps = ['Basic Info', 'Relationship Details', 'Goals & Upload', 'Review'];

const NewProject = () => {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // Form data
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    platform: '',
    role: '',
    partnerName: '',
    relationshipDuration: '',
    goals: [],
    isPrivate: true,
    enableAI: true,
    files: []
  });

  const [currentGoal, setCurrentGoal] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(null);
  };

  const handleAddGoal = () => {
    if (currentGoal.trim() && !formData.goals.includes(currentGoal.trim())) {
      setFormData(prev => ({
        ...prev,
        goals: [...prev.goals, currentGoal.trim()]
      }));
      setCurrentGoal('');
    }
  };

  const handleRemoveGoal = (goalToRemove) => {
    setFormData(prev => ({
      ...prev,
      goals: prev.goals.filter(goal => goal !== goalToRemove)
    }));
  };

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['text/plain', 'application/pdf', 'image/jpeg', 'image/png', 'image/gif'];

    for (const file of files) {
      if (file.size > maxSize) {
        setError(`File ${file.name} is too large. Maximum size is 10MB.`);
        return;
      }
      if (!allowedTypes.includes(file.type)) {
        setError(`File ${file.name} has unsupported format. Supported: PDF, images, text files.`);
        return;
      }
    }

    setFormData(prev => ({
      ...prev,
      files: [...prev.files, ...files]
    }));
  };

  const handleRemoveFile = (fileToRemove) => {
    setFormData(prev => ({
      ...prev,
      files: prev.files.filter(file => file !== fileToRemove)
    }));
  };

  const validateStep = (step) => {
    switch (step) {
      case 0:
        return formData.name.trim() && formData.platform && formData.role;
      case 1:
        return formData.partnerName.trim();
      case 2:
        return formData.goals.length > 0;
      case 3:
        return true;
      default:
        return false;
    }
  };

  const handleNext = () => {
    if (validateStep(activeStep)) {
      setActiveStep(prev => prev + 1);
      setError(null);
    } else {
      setError('Please fill in all required fields before proceeding.');
    }
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
    setError(null);
  };

  const handleSubmit = async () => {
    if (!validateStep(activeStep)) {
      setError('Please complete all required fields.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Create project
      const projectData = {
        name: formData.name,
        description: formData.description,
        platform: formData.platform,
        role: formData.role,
        partner_name: formData.partnerName,
        relationship_duration: formData.relationshipDuration,
        goals: formData.goals.map(goal => ({ description: goal, completed: false })),
        is_private: formData.isPrivate,
        enable_ai: formData.enableAI
      };

      const response = await axios.post('http://localhost:8000/api/projects/', projectData);
      const projectId = response.data.id;

      // Upload files if any
      if (formData.files.length > 0) {
        const uploadFormData = new FormData();
        formData.files.forEach(file => {
          uploadFormData.append('files', file);
        });
        uploadFormData.append('project_id', projectId);

        await axios.post(
          'http://localhost:8000/api/analysis/upload',
          uploadFormData,
          {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: (progressEvent) => {
              const progress = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
              setUploadProgress(progress);
            }
          }
        );
      }

      setSuccess(true);
      setTimeout(() => {
        navigate('/continue');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create project. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Project Name"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                placeholder="e.g., Sarah Relationship Project"
                required
                helperText="Give your project a memorable name"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Brief description of this relationship project..."
                multiline
                rows={3}
                helperText="Optional: Describe what you hope to achieve"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth required>
                <InputLabel>Communication Platform</InputLabel>
                <Select
                  value={formData.platform}
                  onChange={(e) => handleInputChange('platform', e.target.value)}
                  label="Communication Platform"
                >
                  {PLATFORMS.map((platform) => (
                    <MenuItem key={platform.value} value={platform.value}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <span>{platform.icon}</span>
                        {platform.label}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
                <FormHelperText>Where do you primarily communicate?</FormHelperText>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth required>
                <InputLabel>Relationship Type</InputLabel>
                <Select
                  value={formData.role}
                  onChange={(e) => handleInputChange('role', e.target.value)}
                  label="Relationship Type"
                >
                  {ROLES.map((role) => (
                    <MenuItem key={role.value} value={role.value}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {role.icon}
                        <Box>
                          <Typography variant="body2">{role.label}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {role.description}
                          </Typography>
                        </Box>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
                <FormHelperText>What type of relationship is this?</FormHelperText>
              </FormControl>
            </Grid>
          </Grid>
        );

      case 1:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Partner's Name"
                value={formData.partnerName}
                onChange={(e) => handleInputChange('partnerName', e.target.value)}
                placeholder="e.g., Sarah"
                required
                helperText="How do you refer to this person?"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Relationship Duration"
                value={formData.relationshipDuration}
                onChange={(e) => handleInputChange('relationshipDuration', e.target.value)}
                placeholder="e.g., 2 years, 6 months, Just started"
                helperText="How long have you known each other?"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.isPrivate}
                    onChange={(e) => handleInputChange('isPrivate', e.target.checked)}
                  />
                }
                label="Keep this project private"
              />
              <Typography variant="caption" color="text.secondary" display="block">
                Private projects are only visible to you
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.enableAI}
                    onChange={(e) => handleInputChange('enableAI', e.target.checked)}
                  />
                }
                label="Enable AI coaching suggestions"
              />
              <Typography variant="caption" color="text.secondary" display="block">
                Get real-time AI-powered relationship advice
              </Typography>
            </Grid>
          </Grid>
        );

      case 2:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Relationship Goals
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <TextField
                  fullWidth
                  label="Add a goal"
                  value={currentGoal}
                  onChange={(e) => setCurrentGoal(e.target.value)}
                  placeholder="e.g., Improve communication, Resolve conflicts better"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddGoal();
                    }
                  }}
                />
                <Button
                  variant="contained"
                  onClick={handleAddGoal}
                  disabled={!currentGoal.trim()}
                  sx={{ minWidth: 'auto', px: 2 }}
                >
                  <AddIcon />
                </Button>
              </Box>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
                {formData.goals.map((goal, index) => (
                  <Chip
                    key={index}
                    label={goal}
                    onDelete={() => handleRemoveGoal(goal)}
                    color="primary"
                    variant="outlined"
                  />
                ))}
              </Box>
              {formData.goals.length === 0 && (
                <Alert severity="info" sx={{ mb: 3 }}>
                  Add at least one goal to help AI provide better suggestions
                </Alert>
              )}
            </Grid>
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Upload Conversation Data (Optional)
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Upload chat exports, screenshots, or documents to help AI understand your communication patterns
              </Typography>
              
              <Box
                sx={
                  {
                    border: '2px dashed',
                    borderColor: 'primary.main',
                    borderRadius: 2,
                    p: 3,
                    textAlign: 'center',
                    cursor: 'pointer',
                    '&:hover': {
                      bgcolor: 'action.hover'
                    }
                  }
                }
                onClick={() => document.getElementById('file-upload').click()}
              >
                <input
                  id="file-upload"
                  type="file"
                  multiple
                  accept=".pdf,.txt,.jpg,.jpeg,.png,.gif"
                  onChange={handleFileUpload}
                  style={{ display: 'none' }}
                />
                <UploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
                <Typography variant="body1" gutterBottom>
                  Click to upload files or drag and drop
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Supported: PDF, images, text files (max 10MB each)
                </Typography>
              </Box>
              
              {formData.files.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Uploaded Files:
                  </Typography>
                  {formData.files.map((file, index) => (
                    <Box
                      key={index}
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        p: 1,
                        border: 1,
                        borderColor: 'divider',
                        borderRadius: 1,
                        mb: 1
                      }}
                    >
                      <Typography variant="body2">
                        {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                      </Typography>
                      <IconButton
                        size="small"
                        onClick={() => handleRemoveFile(file)}
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  ))}
                </Box>
              )}
            </Grid>
          </Grid>
        );

      case 3:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Review Your Project
              </Typography>
              <Card variant="outlined">
                <CardContent>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Project Name
                      </Typography>
                      <Typography variant="body1" gutterBottom>
                        {formData.name}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Platform
                      </Typography>
                      <Typography variant="body1" gutterBottom>
                        {PLATFORMS.find(p => p.value === formData.platform)?.label}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Relationship Type
                      </Typography>
                      <Typography variant="body1" gutterBottom>
                        {ROLES.find(r => r.value === formData.role)?.label}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Partner
                      </Typography>
                      <Typography variant="body1" gutterBottom>
                        {formData.partnerName}
                      </Typography>
                    </Grid>
                    {formData.description && (
                      <Grid item xs={12}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Description
                        </Typography>
                        <Typography variant="body1" gutterBottom>
                          {formData.description}
                        </Typography>
                      </Grid>
                    )}
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Goals ({formData.goals.length})
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                        {formData.goals.map((goal, index) => (
                          <Chip key={index} label={goal} size="small" />
                        ))}
                      </Box>
                    </Grid>
                    {formData.files.length > 0 && (
                      <Grid item xs={12}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Files ({formData.files.length})
                        </Typography>
                        <Typography variant="body2">
                          {formData.files.map(f => f.name).join(', ')}
                        </Typography>
                      </Grid>
                    )}
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        );

      default:
        return null;
    }
  };

  if (success) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '60vh',
            textAlign: 'center'
          }}
        >
          <PsychologyIcon sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
          <Typography variant="h4" gutterBottom>
            Project Created Successfully!
          </Typography>
          <Typography variant="body1" color="text.secondary" gutterBottom>
            Your relationship project has been set up. Redirecting to your projects...
          </Typography>
          <CircularProgress sx={{ mt: 2 }} />
        </Box>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <PsychologyIcon color="primary" />
          Create New Project
        </Typography>
        <Typography variant="body1" color="text.secondary" gutterBottom>
          Set up a new relationship coaching project with AI-powered insights
        </Typography>

        <Paper sx={{ p: 3, mt: 3 }}>
          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          {renderStepContent(activeStep)}

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
            <Button
              onClick={handleBack}
              disabled={activeStep === 0}
              variant="outlined"
            >
              Back
            </Button>
            
            <Box sx={{ display: 'flex', gap: 1 }}>
              {activeStep === steps.length - 1 ? (
                <Button
                  variant="contained"
                  onClick={handleSubmit}
                  disabled={loading || !validateStep(activeStep)}
                  startIcon={loading ? <CircularProgress size={20} /> : <PsychologyIcon />}
                >
                  {loading ? 'Creating Project...' : 'Create Project'}
                </Button>
              ) : (
                <Button
                  variant="contained"
                  onClick={handleNext}
                  disabled={!validateStep(activeStep)}
                >
                  Next
                </Button>
              )}
            </Box>
          </Box>

          {uploadProgress > 0 && uploadProgress < 100 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" gutterBottom>
                Uploading files... {uploadProgress}%
              </Typography>
              <Box sx={{ width: '100%', bgcolor: 'grey.200', borderRadius: 1 }}>
                <Box
                  sx={{
                    width: `${uploadProgress}%`,
                    bgcolor: 'primary.main',
                    height: 8,
                    borderRadius: 1,
                    transition: 'width 0.3s ease'
                  }}
                />
              </Box>
            </Box>
          )}
        </Paper>
      </Box>
    </motion.div>
  );
};

export default NewProject;