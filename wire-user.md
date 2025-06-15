// === src/lib/api.js ===
import axios from 'axios';

// Central Axios instance points to Catalyst backend.  
// Use Vite env var: VITE_API_BASE_URL = "<https://your-backend-url/api>"
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;

// === src/lib/queryClient.js ===
import { QueryClient } from '@tanstack/react-query';
export const queryClient = new QueryClient();

// === src/main.jsx (wrap root with QueryClientProvider) ===
/*
<React.StrictMode>
  <BrowserRouter>
    <AuthProvider>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </AuthProvider>
  </BrowserRouter>
</React.StrictMode>
*/

// === src/hooks/useProjects.js ===
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

  return { listProjects, createProject };
}

// === src/pages/user/NewProject.jsx ===
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useProjects } from '../../hooks/useProjects';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';

const schema = z.object({
  name: z.string().min(2),
  platform: z.string().min(2),
  role: z.enum(['coach', 'therapist', 'strategist']),
});

export default function NewProject() {
  const { createProject } = useProjects();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({ resolver: zodResolver(schema) });

  const onSubmit = async (values) => {
    await createProject.mutateAsync(values);
  };

  return (
    <Card className="max-w-lg mx-auto">
      <CardContent className="p-6">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input placeholder="Project name" {...register('name')} />
          {errors.name && <p className="text-red-500 text-sm">{errors.name.message}</p>}
          <Input placeholder="Platform (e.g., Instagram)" {...register('platform')} />
          {errors.platform && <p className="text-red-500 text-sm">{errors.platform.message}</p>}
          <select {...register('role')} className="w-full p-2 border rounded">
            <option value="coach">Coach</option>
            <option value="therapist">Therapist</option>
            <option value="strategist">Strategist</option>
          </select>
          <Button type="submit" disabled={createProject.isLoading}>
            {createProject.isLoading ? 'Creating...' : 'Create Project'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

// === src/pages/user/Continue.jsx ===
import { useProjects } from '../../hooks/useProjects';
import { Card } from '@/components/ui/card';

export default function Continue() {
  const { listProjects } = useProjects();

  if (listProjects.isLoading) return <p>Loading projects...</p>;
  if (listProjects.isError) return <p>Error loading projects</p>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {listProjects.data.map((proj) => (
        <Card key={proj.id} className="p-4">
          <h3 className="font-semibold mb-2">{proj.name}</h3>
          <p className="text-sm">Platform: {proj.platform}</p>
        </Card>
      ))}
    </div>
  );
}

// === src/pages/user/ProjectDetail.jsx (snippet for upload) ===
/*
import api from '../../lib/api';
...
const handleFileUpload = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  await api.post('/analysis/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};
*/

// === Content Script improvement (content.js) ===
/*Replace polling with MutationObserver for better performance*/
const observer = new MutationObserver(() => {
  const messages = Array.from(document.querySelectorAll('div'))
    .map((el) => el.innerText)
    .filter((text) => text.length > 10);
  if (messages.length) {
    chrome.storage.local.set({ latestMessages: messages.slice(-10) });
  }
});
observer.observe(document.body, { childList: true, subtree: true });
