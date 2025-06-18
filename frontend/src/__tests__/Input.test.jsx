import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Input } from "../components/ui/input";
import React from "react";

describe("Input Component", () => {
  test("renders input element with default attributes", () => {
    render(<Input />);

    const input = screen.getByRole("textbox");
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute("type", "text");
  });

  test("accepts different input types", () => {
    const { rerender } = render(<Input type="email" />);

    expect(screen.getByRole("textbox")).toHaveAttribute("type", "email");

    rerender(<Input type="password" />);
    expect(screen.getByLabelText("")).toHaveAttribute("type", "password");

    rerender(<Input type="number" />);
    expect(screen.getByLabelText("")).toHaveAttribute("type", "number");
  });

  test("handles value changes", async () => {
    const handleChange = jest.fn();
    render(<Input onChange={handleChange} />);

    const input = screen.getByRole("textbox");
    await userEvent.type(input, "test value");

    expect(handleChange).toHaveBeenCalled();
    expect(input).toHaveValue("test value");
  });

  test("applies custom className", () => {
    render(<Input className="custom-input" />);

    const input = screen.getByRole("textbox");
    expect(input).toHaveClass("custom-input");
  });

  test("accepts and applies additional props", () => {
    render(
      <Input
        placeholder="Enter text here"
        disabled
        required
        aria-label="Test input"
        data-testid="test-input"
      />
    );

    const input = screen.getByTestId("test-input");
    expect(input).toHaveAttribute("placeholder", "Enter text here");
    expect(input).toBeDisabled();
    expect(input).toBeRequired();
    expect(input).toHaveAttribute("aria-label", "Test input");
  });

  test("forwards ref to input element", () => {
    const ref = React.createRef();
    render(<Input ref={ref} data-testid="test-input" />);

    const input = screen.getByTestId("test-input");
    expect(ref.current).toBe(input);
  });
});
