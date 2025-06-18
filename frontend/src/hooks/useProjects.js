import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../lib/api';

export function useProjects() {
    const queryClient = useQueryClient();

    const listProjects = useQuery(['projects'], async () => {
        const { data } = await api.get('/projects');
        return data;
    });

    const createProject = useMutation({
        mutationFn: async (payload) => {
            const { data } = await api.post('/projects', payload);
            return data;
        },
        onSuccess: () => queryClient.invalidateQueries(['projects']),
    });

    const updateProject = useMutation({
        mutationFn: async ({ id, payload }) => {
            const { data } = await api.put(`/projects/${id}`, payload);
            return data;
        },
        onSuccess: (data) => {
            queryClient.invalidateQueries(['projects']);
            queryClient.invalidateQueries(['project', data.id]);
        },
    });

    const deleteProject = useMutation({
        mutationFn: async (id) => {
            await api.delete(`/projects/${id}`);
            return id;
        },
        onSuccess: (id) => {
            queryClient.invalidateQueries(['projects']);
            queryClient.invalidateQueries(['project', id]);
        },
    });

    return {
        listProjects,
        createProject,
        updateProject,
        deleteProject
    };
}

export function useProject(id) {
    return useQuery(['project', id], async () => {
        if (!id) return null;
        const { data } = await api.get(`/projects/${id}`);
        return data;
    }, {
        enabled: !!id, // Only run if id is provided
    });
}
