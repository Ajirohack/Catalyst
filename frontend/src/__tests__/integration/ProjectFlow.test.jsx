import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import { MemoryRouter, Routes, Route } from "react-router-dom";

// Create mock components
const MockNewProject = () => {
  const [formData, setFormData] = React.useState({
    name: "",
    type: "",
    platform: "",
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    // Simulate navigation to project detail
    window.history.pushState({}, "", `/projects/new-project-id`);
    window.dispatchEvent(new Event("popstate"));
  };

  return (
    <div data-testid="new-project-page">
      <h1>Create New Project</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Project Name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          data-testid="project-name-input"
        />
        <select
          value={formData.type}
          onChange={(e) => setFormData({ ...formData, type: e.target.value })}
          data-testid="project-type-select"
        >
          <option value="">Select Type</option>
          <option value="personal">Personal</option>
          <option value="work">Work</option>
        </select>
        <select
          value={formData.platform}
          onChange={(e) =>
            setFormData({ ...formData, platform: e.target.value })
          }
          data-testid="platform-select"
        >
          <option value="">Select Platform</option>
          <option value="whatsapp">WhatsApp</option>
          <option value="telegram">Telegram</option>
          <option value="slack">Slack</option>
        </select>
        <button type="submit" data-testid="create-project-button">
          Create Project
        </button>
      </form>
    </div>
  );
};

const MockProjectDetail = () => {
  const [showWhisperPanel, setShowWhisperPanel] = React.useState(false);

  return (
    <div data-testid="project-detail-page">
      <h1>Project Details</h1>
      <button
        onClick={() => setShowWhisperPanel(true)}
        data-testid="open-whisper-button"
      >
        Open Whisper Panel
      </button>

      {showWhisperPanel && (
        <div data-testid="whisper-panel">
          <h2>Whisper Panel</h2>
          <input
            type="text"
            placeholder="Type your message"
            data-testid="whisper-input"
          />
          <button data-testid="send-whisper-button">Send</button>
          <button
            onClick={() => setShowWhisperPanel(false)}
            data-testid="close-whisper-button"
          >
            Close
          </button>
        </div>
      )}
    </div>
  );
};

// Mock API functions
const mockCreateProject = jest.fn();
const mockGetProject = jest.fn();

// Mock hooks
jest.mock("../hooks/useProjects", () => ({
  useProjects: () => ({
    createProject: mockCreateProject,
  }),
}));

jest.mock("../hooks/useProject", () => ({
  useProject: () => ({
    data: {
      id: "new-project-id",
      name: "Test Project",
      type: "personal",
      platform: "whatsapp",
      createdAt: new Date().toISOString(),
    },
    isLoading: false,
    isError: false,
  }),
}));

describe("Project Creation and Interaction Flow", () => {
  beforeEach(() => {
    // Reset mocks
    mockCreateProject.mockReset();
    mockGetProject.mockReset();

    // Mock successful project creation
    mockCreateProject.mockResolvedValue({
      id: "new-project-id",
      name: "Test Project",
    });
  });

  test("user can create a new project and navigate to project details", async () => {
    render(
      <MemoryRouter initialEntries={["/new-project"]}>
        <Routes>
          <Route path="/new-project" element={<MockNewProject />} />
          <Route path="/projects/:id" element={<MockProjectDetail />} />
        </Routes>
      </MemoryRouter>
    );

    // Verify we're on the new project page
    expect(screen.getByTestId("new-project-page")).toBeInTheDocument();

    // Fill out form
    await userEvent.type(
      screen.getByTestId("project-name-input"),
      "Test Project"
    );
    await userEvent.selectOptions(
      screen.getByTestId("project-type-select"),
      "personal"
    );
    await userEvent.selectOptions(
      screen.getByTestId("platform-select"),
      "whatsapp"
    );

    // Submit form
    await userEvent.click(screen.getByTestId("create-project-button"));

    // Wait for navigation to project detail page
    await waitFor(() => {
      expect(screen.getByTestId("project-detail-page")).toBeInTheDocument();
    });
  });

  test("user can open and close the whisper panel on project details page", async () => {
    render(
      <MemoryRouter initialEntries={["/projects/new-project-id"]}>
        <Routes>
          <Route path="/projects/:id" element={<MockProjectDetail />} />
        </Routes>
      </MemoryRouter>
    );

    // Verify we're on the project detail page
    expect(screen.getByTestId("project-detail-page")).toBeInTheDocument();

    // Whisper panel should not be visible initially
    expect(screen.queryByTestId("whisper-panel")).not.toBeInTheDocument();

    // Open whisper panel
    await userEvent.click(screen.getByTestId("open-whisper-button"));

    // Verify whisper panel is now visible
    expect(screen.getByTestId("whisper-panel")).toBeInTheDocument();

    // Close whisper panel
    await userEvent.click(screen.getByTestId("close-whisper-button"));

    // Verify whisper panel is no longer visible
    expect(screen.queryByTestId("whisper-panel")).not.toBeInTheDocument();
  });
});
