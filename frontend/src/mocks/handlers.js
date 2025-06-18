// src/mocks/handlers.js
// Mock Service Worker handlers for API endpoints
import { rest } from 'msw';

// Base API URL
const BASE_URL = 'http://localhost:8000/api';

export const handlers = [
    // Auth endpoints
    rest.post(`${BASE_URL}/auth/login`, (req, res, ctx) => {
        const { email, password } = req.body;

        if (email === 'test@example.com' && password === 'password') {
            return res(
                ctx.status(200),
                ctx.json({
                    token: 'fake-jwt-token',
                    user: {
                        id: 1,
                        name: 'Test User',
                        email: 'test@example.com',
                        role: 'user',
                    },
                })
            );
        }

        return res(
            ctx.status(401),
            ctx.json({
                message: 'Invalid credentials',
            })
        );
    }),

    rest.post(`${BASE_URL}/auth/register`, (req, res, ctx) => {
        return res(
            ctx.status(201),
            ctx.json({
                message: 'User registered successfully',
                user: {
                    id: 2,
                    name: req.body.name,
                    email: req.body.email,
                    role: 'user',
                },
            })
        );
    }),

    // Users endpoints
    rest.get(`${BASE_URL}/users`, (req, res, ctx) => {
        return res(
            ctx.status(200),
            ctx.json({
                users: [
                    {
                        id: 1,
                        name: 'Test User',
                        email: 'test@example.com',
                        role: 'user',
                        status: 'active',
                    },
                    {
                        id: 2,
                        name: 'Admin User',
                        email: 'admin@example.com',
                        role: 'admin',
                        status: 'active',
                    },
                ],
            })
        );
    }),

    // Projects endpoints
    rest.get(`${BASE_URL}/projects`, (req, res, ctx) => {
        return res(
            ctx.status(200),
            ctx.json({
                projects: [
                    {
                        id: 1,
                        name: 'Test Project',
                        description: 'This is a test project',
                        status: 'active',
                        createdAt: '2025-06-01T00:00:00.000Z',
                        updatedAt: '2025-06-10T00:00:00.000Z',
                    },
                    {
                        id: 2,
                        name: 'Another Project',
                        description: 'This is another test project',
                        status: 'completed',
                        createdAt: '2025-05-15T00:00:00.000Z',
                        updatedAt: '2025-06-05T00:00:00.000Z',
                    },
                ],
            })
        );
    }),

    rest.get(`${BASE_URL}/projects/:id`, (req, res, ctx) => {
        const { id } = req.params;

        return res(
            ctx.status(200),
            ctx.json({
                id: Number(id),
                name: `Project ${id}`,
                description: `This is project ${id}`,
                status: 'active',
                createdAt: '2025-06-01T00:00:00.000Z',
                updatedAt: '2025-06-10T00:00:00.000Z',
                analyses: [
                    {
                        id: 1,
                        name: 'Initial Analysis',
                        status: 'completed',
                        createdAt: '2025-06-02T00:00:00.000Z',
                    },
                ],
            })
        );
    }),

    // Analysis endpoints
    rest.get(`${BASE_URL}/analysis/:id`, (req, res, ctx) => {
        const { id } = req.params;

        return res(
            ctx.status(200),
            ctx.json({
                id: Number(id),
                name: `Analysis ${id}`,
                projectId: 1,
                status: 'completed',
                createdAt: '2025-06-02T00:00:00.000Z',
                results: {
                    sentimentScore: 0.75,
                    toneAnalysis: {
                        positive: 65,
                        neutral: 25,
                        negative: 10,
                    },
                    keyThemes: ['communication', 'trust', 'respect'],
                    suggestedResponses: [
                        'I understand how you feel about that.',
                        'Let me share my perspective on this.',
                        'I appreciate your honesty about this issue.',
                    ],
                },
            })
        );
    }),

    // Analytics endpoints
    rest.get(`${BASE_URL}/analytics/dashboard`, (req, res, ctx) => {
        return res(
            ctx.status(200),
            ctx.json({
                userGrowth: [
                    { date: '2025-01-01', count: 10 },
                    { date: '2025-02-01', count: 20 },
                    { date: '2025-03-01', count: 30 },
                    { date: '2025-04-01', count: 45 },
                    { date: '2025-05-01', count: 60 },
                    { date: '2025-06-01', count: 80 },
                ],
                projectMetrics: {
                    total: 150,
                    active: 75,
                    completed: 50,
                    abandoned: 25,
                },
                platformUsage: [
                    { platform: 'WhatsApp', count: 45 },
                    { platform: 'Messenger', count: 30 },
                    { platform: 'Slack', count: 25 },
                    { platform: 'Teams', count: 20 },
                    { platform: 'Discord', count: 15 },
                    { platform: 'Others', count: 15 },
                ],
                engagementMetrics: [
                    { date: '2025-01-01', messages: 100, suggestions: 20 },
                    { date: '2025-02-01', messages: 200, suggestions: 40 },
                    { date: '2025-03-01', messages: 300, suggestions: 60 },
                    { date: '2025-04-01', messages: 450, suggestions: 90 },
                    { date: '2025-05-01', messages: 600, suggestions: 120 },
                    { date: '2025-06-01', messages: 800, suggestions: 160 },
                ],
                userMetrics: {
                    messagesSent: 1250,
                    messagesSentGrowth: 15,
                    suggestionsReceived: 320,
                    suggestionsReceivedGrowth: 8,
                    avgResponseTime: 1.5,
                    avgResponseTimeGrowth: -5,
                },
            })
        );
    }),
];
