// src/hooks/useProjects.js - Enhanced with React Query
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../lib/api';
import toast from 'react-hot-toast';

export function useProjects() {
  const queryClient = useQueryClient();

  const listProjects = useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const { data } = await api.get('/projects');
      return data;
    },
    staleTime: 5 *60* 1000, // 5 minutes
    onError: (error) => {
      toast.error('Failed to load projects');
    }
  });

  const createProject = useMutation({
    mutationFn: async (payload) => {
      const { data } = await api.post('/projects', payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['projects']);
      toast.success('Project created successfully');
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to create project');
    }
  });

  const updateProject = useMutation({
    mutationFn: async ({ id, payload }) => {
      const { data } = await api.put(`/projects/${id}`, payload);
      return data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries(['projects']);
      queryClient.invalidateQueries(['project', data.id]);
      toast.success('Project updated successfully');
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to update project');
    }
  });

  const deleteProject = useMutation({
    mutationFn: async (id) => {
      await api.delete(`/projects/${id}`);
      return id;
    },
    onSuccess: (id) => {
      queryClient.invalidateQueries(['projects']);
      queryClient.invalidateQueries(['project', id]);
      toast.success('Project deleted successfully');
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to delete project');
    }
  });

  return {
    listProjects,
    createProject,
    updateProject,
    deleteProject
  };
}

export function useProject(id) {
  return useQuery({
    queryKey: ['project', id],
    queryFn: async () => {
      if (!id) return null;
      const { data } = await api.get(`/projects/${id}`);
      return data;
    },
    enabled: !!id,
    onError: (error) => {
      toast.error('Failed to load project details');
    }
  });
}

export function useProjectStats() {
  return useQuery({
    queryKey: ['project-stats'],
    queryFn: async () => {
      const { data } = await api.get('/projects/stats');
      return data;
    },
    staleTime: 10 *60* 1000, // 10 minutes
    onError: (error) => {
      console.error('Failed to load project stats:', error);
    }
  });
}
