// cypress/e2e/api-tests.cy.js
// Tests that focus on API interaction without UI

describe('API Tests', () => {
    beforeEach(() => {
        // Set the auth token for API requests
        cy.setCookie('authToken', 'fake-jwt-token');

        // Set localStorage auth
        cy.window().then((win) => {
            win.localStorage.setItem('auth', JSON.stringify({
                token: 'fake-jwt-token',
                user: {
                    id: 1,
                    name: 'Test User',
                    email: 'test@example.com',
                    role: 'user',
                },
            }));
        });
    });

    it('successfully retrieves user profile via API', () => {
        cy.request({
            method: 'GET',
            url: '/api/users/profile',
            headers: {
                Authorization: 'Bearer fake-jwt-token',
            },
        }).then((response) => {
            expect(response.status).to.eq(200);
            expect(response.body).to.have.property('id');
            expect(response.body).to.have.property('name');
            expect(response.body).to.have.property('email');
            expect(response.body).to.have.property('role');
        });
    });

    it('creates a new project via API', () => {
        const newProject = {
            name: 'API Test Project',
            description: 'Project created via API test',
            platform: 'WhatsApp',
            type: 'Personal',
        };

        cy.request({
            method: 'POST',
            url: '/api/projects',
            headers: {
                Authorization: 'Bearer fake-jwt-token',
            },
            body: newProject,
        }).then((response) => {
            expect(response.status).to.eq(201);
            expect(response.body).to.have.property('id');
            expect(response.body.name).to.eq(newProject.name);
            expect(response.body.description).to.eq(newProject.description);

            // Store the project ID for later use
            const projectId = response.body.id;
            cy.wrap(projectId).as('projectId');
        });
    });

    it('retrieves project list via API', () => {
        cy.request({
            method: 'GET',
            url: '/api/projects',
            headers: {
                Authorization: 'Bearer fake-jwt-token',
            },
        }).then((response) => {
            expect(response.status).to.eq(200);
            expect(response.body).to.have.property('projects');
            expect(response.body.projects).to.be.an('array');
            expect(response.body.projects.length).to.be.greaterThan(0);
        });
    });

    it('updates a project via API', function () {
        // Use the project ID from the creation test
        // Note: This test depends on the 'creates a new project via API' test
        if (this.projectId) {
            const projectId = this.projectId;
            const updatedProject = {
                name: 'Updated API Test Project',
                description: 'Project updated via API test',
                status: 'completed',
            };

            cy.request({
                method: 'PUT',
                url: `/api/projects/${projectId}`,
                headers: {
                    Authorization: 'Bearer fake-jwt-token',
                },
                body: updatedProject,
            }).then((response) => {
                expect(response.status).to.eq(200);
                expect(response.body.name).to.eq(updatedProject.name);
                expect(response.body.description).to.eq(updatedProject.description);
                expect(response.body.status).to.eq(updatedProject.status);
            });
        } else {
            // Skip if project ID isn't available
            this.skip();
        }
    });

    it('creates a new analysis via API', function () {
        // Use the project ID from the creation test
        if (this.projectId) {
            const projectId = this.projectId;
            const newAnalysis = {
                name: 'API Test Analysis',
                type: 'standard',
            };

            cy.request({
                method: 'POST',
                url: `/api/projects/${projectId}/analyses`,
                headers: {
                    Authorization: 'Bearer fake-jwt-token',
                },
                body: newAnalysis,
            }).then((response) => {
                expect(response.status).to.eq(201);
                expect(response.body).to.have.property('id');
                expect(response.body.name).to.eq(newAnalysis.name);
                expect(response.body.projectId).to.eq(projectId);

                // Store the analysis ID for later use
                const analysisId = response.body.id;
                cy.wrap(analysisId).as('analysisId');
            });
        } else {
            // Skip if project ID isn't available
            this.skip();
        }
    });

    it('retrieves analysis results via API', function () {
        // Use the project ID and analysis ID from previous tests
        if (this.projectId && this.analysisId) {
            const projectId = this.projectId;
            const analysisId = this.analysisId;

            cy.request({
                method: 'GET',
                url: `/api/projects/${projectId}/analyses/${analysisId}`,
                headers: {
                    Authorization: 'Bearer fake-jwt-token',
                },
            }).then((response) => {
                expect(response.status).to.eq(200);
                expect(response.body).to.have.property('id');
                expect(response.body).to.have.property('name');
                expect(response.body).to.have.property('status');
            });
        } else {
            // Skip if IDs aren't available
            this.skip();
        }
    });

    it('gets whisper suggestions via API', () => {
        const whisperRequest = {
            message: 'Can you help me with a response to this difficult message?',
            conversationContext: 'The user is upset about a delayed delivery.',
            platform: 'WhatsApp',
        };

        cy.request({
            method: 'POST',
            url: '/api/whisper/suggest',
            headers: {
                Authorization: 'Bearer fake-jwt-token',
            },
            body: whisperRequest,
        }).then((response) => {
            expect(response.status).to.eq(200);
            expect(response.body).to.have.property('suggestions');
            expect(response.body.suggestions).to.be.an('array');
            expect(response.body.suggestions.length).to.be.greaterThan(0);
        });
    });

    it('handles invalid API requests properly', () => {
        // Test with missing required fields
        const invalidProject = {
            // Missing name field
            description: 'Invalid project',
        };

        cy.request({
            method: 'POST',
            url: '/api/projects',
            headers: {
                Authorization: 'Bearer fake-jwt-token',
            },
            body: invalidProject,
            failOnStatusCode: false,
        }).then((response) => {
            expect(response.status).to.eq(400);
            expect(response.body).to.have.property('message');
            expect(response.body.message).to.include('name');
        });
    });

    it('handles authentication errors properly', () => {
        // Test with invalid token
        cy.request({
            method: 'GET',
            url: '/api/users/profile',
            headers: {
                Authorization: 'Bearer invalid-token',
            },
            failOnStatusCode: false,
        }).then((response) => {
            expect(response.status).to.eq(401);
            expect(response.body).to.have.property('message');
            expect(response.body.message).to.include('unauthorized');
        });
    });

    it('handles not found errors properly', () => {
        // Test with non-existent resource
        cy.request({
            method: 'GET',
            url: '/api/projects/9999',
            headers: {
                Authorization: 'Bearer fake-jwt-token',
            },
            failOnStatusCode: false,
        }).then((response) => {
            expect(response.status).to.eq(404);
            expect(response.body).to.have.property('message');
            expect(response.body.message).to.include('not found');
        });
    });
});
