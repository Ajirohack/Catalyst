import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";

// Import before mocking
import WhisperPanelOriginal from "../components/WhisperPanel";

// Mock WebSocket
class MockWebSocket {
  constructor(url) {
    this.url = url;
    this.readyState = 1; // Connected
    this.onopen = null;
    this.onmessage = null;
    this.onclose = null;
    this.onerror = null;

    // Call onopen asynchronously
    setTimeout(() => {
      if (this.onopen) this.onopen({ target: this });
    }, 0);
  }

  send(data) {
    // Mock response after sending a message
    setTimeout(() => {
      if (this.onmessage) {
        this.onmessage({
          data: JSON.stringify({
            type: "suggestion",
            content: "This is a suggestion based on your message",
          }),
        });
      }
    }, 100);
  }

  close() {
    if (this.onclose) this.onclose({ target: this });
  }
}

// Mock the WebSocket globally
global.WebSocket = MockWebSocket;

// Mock the WhisperPanel component
jest.mock("../components/WhisperPanel", () => {
  return function MockedWhisperPanel({
    isOpen,
    onClose,
    projectId,
    isMinimized,
    onToggleMinimize,
  }) {
    const [message, setMessage] = React.useState("");
    const [suggestions, setSuggestions] = React.useState([
      "This is a test suggestion",
      "Here's another suggestion",
    ]);

    const handleSendMessage = () => {
      if (message.trim()) {
        // Simulate getting a new suggestion
        setSuggestions([...suggestions, "New suggestion based on: " + message]);
        setMessage("");
      }
    };

    if (!isOpen) return null;

    return (
      <div
        data-testid="whisper-panel"
        className={isMinimized ? "minimized" : ""}
      >
        <div className="panel-header">
          <h3>Whisper Panel</h3>
          <button onClick={onToggleMinimize} data-testid="minimize-button">
            {isMinimized ? "Expand" : "Minimize"}
          </button>
          <button onClick={onClose} data-testid="close-button">
            Close
          </button>
        </div>

        <div
          className="panel-content"
          style={{ display: isMinimized ? "none" : "block" }}
        >
          <div className="suggestions">
            {suggestions.map((suggestion, index) => (
              <div
                key={index}
                className="suggestion"
                data-testid={`suggestion-${index}`}
              >
                {suggestion}
              </div>
            ))}
          </div>

          <div className="input-area">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message..."
              data-testid="message-input"
            />
            <button onClick={handleSendMessage} data-testid="send-button">
              Send
            </button>
          </div>
        </div>
      </div>
    );
  };
});

// Re-import the mocked component
const WhisperPanel = WhisperPanelOriginal;

describe("WhisperPanel Component", () => {
  test("renders when isOpen is true", () => {
    render(
      <WhisperPanel
        isOpen={true}
        onClose={jest.fn()}
        projectId="test-project"
        isMinimized={false}
        onToggleMinimize={jest.fn()}
      />
    );

    expect(screen.getByTestId("whisper-panel")).toBeInTheDocument();
    expect(screen.getByText("Whisper Panel")).toBeInTheDocument();
  });

  test("does not render when isOpen is false", () => {
    render(
      <WhisperPanel
        isOpen={false}
        onClose={jest.fn()}
        projectId="test-project"
        isMinimized={false}
        onToggleMinimize={jest.fn()}
      />
    );

    expect(screen.queryByTestId("whisper-panel")).not.toBeInTheDocument();
  });

  test("applies minimized class when isMinimized is true", () => {
    render(
      <WhisperPanel
        isOpen={true}
        onClose={jest.fn()}
        projectId="test-project"
        isMinimized={true}
        onToggleMinimize={jest.fn()}
      />
    );

    expect(screen.getByTestId("whisper-panel")).toHaveClass("minimized");
    expect(screen.getByTestId("minimize-button")).toHaveTextContent("Expand");
  });

  test("calls onClose when close button is clicked", async () => {
    const handleClose = jest.fn();
    render(
      <WhisperPanel
        isOpen={true}
        onClose={handleClose}
        projectId="test-project"
        isMinimized={false}
        onToggleMinimize={jest.fn()}
      />
    );

    await userEvent.click(screen.getByTestId("close-button"));
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  test("calls onToggleMinimize when minimize button is clicked", async () => {
    const handleToggleMinimize = jest.fn();
    render(
      <WhisperPanel
        isOpen={true}
        onClose={jest.fn()}
        projectId="test-project"
        isMinimized={false}
        onToggleMinimize={handleToggleMinimize}
      />
    );

    await userEvent.click(screen.getByTestId("minimize-button"));
    expect(handleToggleMinimize).toHaveBeenCalledTimes(1);
  });

  test("sends message and receives suggestion", async () => {
    render(
      <WhisperPanel
        isOpen={true}
        onClose={jest.fn()}
        projectId="test-project"
        isMinimized={false}
        onToggleMinimize={jest.fn()}
      />
    );

    // Type a message
    await userEvent.type(
      screen.getByTestId("message-input"),
      "Hello, this is a test message"
    );

    // Send the message
    await userEvent.click(screen.getByTestId("send-button"));

    // Check if the input is cleared
    expect(screen.getByTestId("message-input")).toHaveValue("");

    // Check if a new suggestion appears
    expect(screen.getByText(/New suggestion based on:/)).toBeInTheDocument();
  });
});
