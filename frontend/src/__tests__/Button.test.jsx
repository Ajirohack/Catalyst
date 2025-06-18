import { screen, render } from "@testing-library/react";
import { Button } from "../components/ui/button";
import userEvent from "@testing-library/user-event";
import React from "react";

describe("Button Component", () => {
  test("renders button with correct text", () => {
    render(<Button>Click Me</Button>);
    expect(
      screen.getByRole("button", { name: /click me/i })
    ).toBeInTheDocument();
  });

  test("handles click events", async () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click Me</Button>);

    const button = screen.getByRole("button", { name: /click me/i });
    await userEvent.click(button);

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test("renders disabled state correctly", () => {
    render(<Button disabled>Disabled Button</Button>);

    const button = screen.getByRole("button", { name: /disabled button/i });
    expect(button).toBeDisabled();
  });

  test("applies custom className", () => {
    render(<Button className="custom-class">Custom Button</Button>);

    const button = screen.getByRole("button", { name: /custom button/i });
    expect(button).toHaveClass("custom-class");
  });

  test("renders with different variants", () => {
    const { rerender } = render(
      <Button variant="outline">Outline Button</Button>
    );

    expect(screen.getByRole("button", { name: /outline button/i })).toHaveClass(
      "outline"
    );

    rerender(<Button variant="destructive">Destructive Button</Button>);
    expect(
      screen.getByRole("button", { name: /destructive button/i })
    ).toHaveClass("destructive");
  });

  test("renders with different sizes", () => {
    const { rerender } = render(<Button size="sm">Small Button</Button>);

    expect(screen.getByRole("button", { name: /small button/i })).toHaveClass(
      "sm"
    );

    rerender(<Button size="lg">Large Button</Button>);
    expect(screen.getByRole("button", { name: /large button/i })).toHaveClass(
      "lg"
    );
  });
});
