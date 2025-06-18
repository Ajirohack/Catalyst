import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../lib/api';

export function useWhisper(projectId) {
    const queryClient = useQueryClient();

    // Get whisper suggestions for a project
    const getSuggestions = useQuery(
        ['whisper', 'suggestions', projectId],
        async () => {
            if (!projectId) return [];
            const { data } = await api.get(`/analysis/whisper/${projectId}/suggestions`);
            return data;
        },
        {
            enabled: !!projectId,
            refetchInterval: 30000, // Refetch every 30 seconds
        }
    );

    // Send a message to be analyzed for whisper suggestions
    const analyzeMessage = useMutation({
        mutationFn: async ({ projectId, message }) => {
            const { data } = await api.post(`/analysis/whisper/${projectId}/analyze`, {
                message
            });
            return data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries(['whisper', 'suggestions', projectId]);
        }
    });

    // Mark a suggestion as applied or dismissed
    const updateSuggestion = useMutation({
        mutationFn: async ({ suggestionId, action }) => {
            const { data } = await api.post(`/analysis/whisper/suggestion/${suggestionId}/${action}`);
            return data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries(['whisper', 'suggestions', projectId]);
        }
    });

    return {
        getSuggestions,
        analyzeMessage,
        updateSuggestion
    };
}
