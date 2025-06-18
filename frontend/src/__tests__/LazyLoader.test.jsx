import { screen } from "@testing-library/react";
import { render } from "../lib/test-utils";
import LazyLoader from "../components/LazyLoader";

// Mock the Suspense component to control loading behavior
jest.mock("react", () => {
  const originalReact = jest.requireActual("react");
  return {
    ...originalReact,
    Suspense: ({ children, fallback }) => {
      return children;
    },
  };
});

describe("LazyLoader Component", () => {
  test("renders children when not in loading state", () => {
    const TestComponent = () => (
      <div data-testid="test-component">Test Content</div>
    );

    render(
      <LazyLoader>
        <TestComponent />
      </LazyLoader>
    );

    // Verify the children component is rendered
    expect(screen.getByTestId("test-component")).toBeInTheDocument();
    expect(screen.getByText("Test Content")).toBeInTheDocument();
  });

  test("accepts custom fallback text", () => {
    // Here we test that the component accepts a fallbackText prop
    // We don't actually test the loading state since we've mocked Suspense
    const TestComponent = () => <div>Test Content</div>;

    render(
      <LazyLoader fallbackText="Custom loading message">
        <TestComponent />
      </LazyLoader>
    );

    // Verify the children component is rendered
    expect(screen.getByText("Test Content")).toBeInTheDocument();
  });
});
