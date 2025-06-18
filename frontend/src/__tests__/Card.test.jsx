import { render, screen } from "@testing-library/react";
import React from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "../components/ui/card";

// Mock card component if needed
jest.mock("../components/ui/card", () => {
  const actual = jest.requireActual("../components/ui/card");
  return {
    ...actual,
    Card: jest.fn(({ className, children, ...props }) => (
      <div
        className={`rounded-lg border bg-card text-card-foreground shadow-sm ${className || ""}`}
        data-testid="card"
        {...props}
      >
        {children}
      </div>
    )),
    CardHeader: jest.fn(({ className, children, ...props }) => (
      <div
        className={`flex flex-col space-y-1.5 p-6 ${className || ""}`}
        data-testid="card-header"
        {...props}
      >
        {children}
      </div>
    )),
    CardTitle: jest.fn(({ className, children, ...props }) => (
      <h3
        className={`text-2xl font-semibold leading-none tracking-tight ${className || ""}`}
        data-testid="card-title"
        {...props}
      >
        {children}
      </h3>
    )),
    CardDescription: jest.fn(({ className, children, ...props }) => (
      <p
        className={`text-sm text-muted-foreground ${className || ""}`}
        data-testid="card-description"
        {...props}
      >
        {children}
      </p>
    )),
    CardContent: jest.fn(({ className, children, ...props }) => (
      <div
        className={`p-6 pt-0 ${className || ""}`}
        data-testid="card-content"
        {...props}
      >
        {children}
      </div>
    )),
    CardFooter: jest.fn(({ className, children, ...props }) => (
      <div
        className={`flex items-center p-6 pt-0 ${className || ""}`}
        data-testid="card-footer"
        {...props}
      >
        {children}
      </div>
    )),
  };
});

describe("Card Component", () => {
  test("renders card with all subcomponents", () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Card Title</CardTitle>
          <CardDescription>Card Description</CardDescription>
        </CardHeader>
        <CardContent>
          <p>Card Content</p>
        </CardContent>
        <CardFooter>
          <p>Card Footer</p>
        </CardFooter>
      </Card>
    );

    // Check if all components render correctly
    expect(screen.getByTestId("card")).toBeInTheDocument();
    expect(screen.getByTestId("card-header")).toBeInTheDocument();
    expect(screen.getByTestId("card-title")).toBeInTheDocument();
    expect(screen.getByTestId("card-description")).toBeInTheDocument();
    expect(screen.getByTestId("card-content")).toBeInTheDocument();
    expect(screen.getByTestId("card-footer")).toBeInTheDocument();

    // Check content
    expect(screen.getByText("Card Title")).toBeInTheDocument();
    expect(screen.getByText("Card Description")).toBeInTheDocument();
    expect(screen.getByText("Card Content")).toBeInTheDocument();
    expect(screen.getByText("Card Footer")).toBeInTheDocument();
  });

  test("applies custom classNames to card components", () => {
    render(
      <Card className="custom-card">
        <CardHeader className="custom-header">
          <CardTitle className="custom-title">Custom Card</CardTitle>
        </CardHeader>
      </Card>
    );

    expect(screen.getByTestId("card")).toHaveClass("custom-card");
    expect(screen.getByTestId("card-header")).toHaveClass("custom-header");
    expect(screen.getByTestId("card-title")).toHaveClass("custom-title");
  });

  test("renders card without header or footer", () => {
    render(
      <Card>
        <CardContent>
          <p>Only Content</p>
        </CardContent>
      </Card>
    );

    expect(screen.getByTestId("card")).toBeInTheDocument();
    expect(screen.getByTestId("card-content")).toBeInTheDocument();
    expect(screen.getByText("Only Content")).toBeInTheDocument();
    expect(screen.queryByTestId("card-header")).not.toBeInTheDocument();
    expect(screen.queryByTestId("card-footer")).not.toBeInTheDocument();
  });
});
