import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../lib/api';

export function useAnalysis() {
    const queryClient = useQueryClient();

    const uploadConversation = useMutation({
        mutationFn: async ({ file, projectId, metadata }) => {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('project_id', projectId);

            if (metadata) {
                formData.append('metadata', JSON.stringify(metadata));
            }

            const { data } = await api.post('/analysis/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return data;
        },
        onSuccess: (data, variables) => {
            queryClient.invalidateQueries(['project', variables.projectId]);
            queryClient.invalidateQueries(['analysis', variables.projectId]);
        },
    });

    /**
     * Start a new analysis for a project
     */
    const startAnalysis = useMutation({
        mutationFn: async ({ projectId, options = {} }) => {
            const { data } = await api.post(`/analysis/projects/${projectId}/start`, options);
            return data;
        },
        onSuccess: (data, variables) => {
            queryClient.invalidateQueries(['analysis', variables.projectId]);
            queryClient.invalidateQueries(['projects']); // Update project list to show analysis status

            // Start polling for progress if analysis was started successfully
            if (data && data.analysis_id) {
                queryClient.invalidateQueries(['analysis-progress', variables.projectId, data.analysis_id]);
            }
        }
    });

    /**
     * Cancel an ongoing analysis
     */
    const cancelAnalysis = useMutation({
        mutationFn: async ({ projectId, analysisId }) => {
            const { data } = await api.post(`/analysis/projects/${projectId}/cancel`, { analysis_id: analysisId });
            return data;
        },
        onSuccess: (data, variables) => {
            queryClient.invalidateQueries(['analysis', variables.projectId]);
            queryClient.invalidateQueries(['projects']);
            queryClient.invalidateQueries(['analysis-progress', variables.projectId, variables.analysisId]);
        }
    });

    /**
     * Export analysis results to different formats
     */
    const exportAnalysis = useMutation({
        mutationFn: async ({ projectId, analysisId, format = 'pdf' }) => {
            const { data } = await api.post(`/analysis/projects/${projectId}/export/${analysisId}`, { format });
            return data;
        }
    });

    return {
        uploadConversation,
        startAnalysis,
        cancelAnalysis,
        exportAnalysis
    };
}

export function useAnalysisHistory(projectId) {
    return useQuery(
        ['analysis', projectId],
        async () => {
            if (!projectId) return [];
            const { data } = await api.get(`/analysis/history/${projectId}`);
            return data;
        },
        {
            enabled: !!projectId,
            staleTime: 5 * 60 * 1000, // 5 minutes
        }
    );
}

export function useAnalysisDetails(analysisId) {
    return useQuery(
        ['analysis-details', analysisId],
        async () => {
            if (!analysisId) return null;
            const { data } = await api.get(`/analysis/${analysisId}`);
            return data;
        },
        {
            enabled: !!analysisId,
            staleTime: 5 * 60 * 1000, // 5 minutes
        }
    );
}

/**
 * Hook for tracking real-time progress of an ongoing analysis
 */
export function useAnalysisProgress(projectId, analysisId) {
    return useQuery(
        ['analysis-progress', projectId, analysisId],
        async () => {
            if (!projectId || !analysisId) return null;
            const { data } = await api.get(`/analysis/projects/${projectId}/progress/${analysisId}`);
            return data;
        },
        {
            enabled: !!projectId && !!analysisId,
            refetchInterval: (data) => {
                // Poll more frequently while in progress, stop polling when complete or failed
                if (!data || data.status === 'in_progress') {
                    return 2000; // 2 seconds
                }
                return false; // Stop polling
            },
            refetchIntervalInBackground: true,
            staleTime: 0, // Always refetch when requested
        }
    );
}

/**
 * Hook for fetching a specific analysis by ID
 */
export function useSpecificAnalysis(projectId, analysisId) {
    return useQuery(
        ['specific-analysis', projectId, analysisId],
        async () => {
            if (!projectId || !analysisId) return null;
            const { data } = await api.get(`/analysis/projects/${projectId}/results/${analysisId}`);
            return data;
        },
        {
            enabled: !!projectId && !!analysisId,
            staleTime: 5 * 60 * 1000, // 5 minutes
        }
    );
}

/**
 * Hook for fetching detailed metrics for an analysis
 */
export function useAnalysisMetrics(projectId, analysisId) {
    return useQuery(
        ['analysis-metrics', projectId, analysisId],
        async () => {
            if (!projectId || !analysisId) return null;
            const { data } = await api.get(`/analysis/projects/${projectId}/metrics/${analysisId}`);
            return data;
        },
        {
            enabled: !!projectId && !!analysisId,
            staleTime: 5 * 60 * 1000, // 5 minutes
        }
    );
}
