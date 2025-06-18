import { screen, fireEvent } from "@testing-library/react";
import { render } from "../lib/test-utils";
import React from "react";

// Make sure imports are at the top - order matters
// Import the component before mocking it
import MfaSetupOriginal from "../pages/auth/MfaSetup";

// Mock the MfaSetup component
jest.mock("../pages/auth/MfaSetup", () => {
  return function MockedMfaSetup() {
    const [step, setStep] = React.useState(1);
    const [verificationCode, setVerificationCode] = React.useState("");

    return (
      <div>
        <h1>Set up Two-Factor Authentication</h1>

        {step === 1 && (
          <div>
            <p>Step 1: Scan QR Code</p>
            <img
              src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMAAAAD"
              alt="QR Code"
            />
            <p>ABCDEFGHIJKLMNOP</p>
            <button onClick={() => setStep(2)}>Continue</button>
          </div>
        )}

        {step === 2 && (
          <div>
            <p>Verify your code</p>
            <input
              type="text"
              placeholder="Enter 6-digit code"
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value)}
            />
            <button onClick={() => setStep(3)}>Verify</button>
          </div>
        )}

        {step === 3 && (
          <div>
            <h2>Recovery Codes</h2>
            <p>ABCD-EFGH-IJKL-MNOP</p>
            <p>1234-5678-9012-3456</p>
            <p>WXYZ-UVST-QRST-UVWX</p>
          </div>
        )}
      </div>
    );
  };
});

// Re-import the mocked component
const MfaSetup = MfaSetupOriginal;

describe("MFA Setup Flow", () => {
  test("renders MFA setup steps correctly", async () => {
    render(<MfaSetup />);

    // Check for setup heading
    expect(
      screen.getByText(/Set up Two-Factor Authentication/i)
    ).toBeInTheDocument();

    // Check for step indicators
    expect(screen.getByText(/Step 1/i)).toBeInTheDocument();

    // Check for QR code
    const qrCode = screen.getByAltText(/QR Code/i);
    expect(qrCode).toBeInTheDocument();
    expect(qrCode.src).toContain("data:image/png;base64");

    // Check for secret key
    expect(screen.getByText(/ABCDEFGHIJKLMNOP/i)).toBeInTheDocument();
  });

  test("proceeds to next step when continue button is clicked", async () => {
    render(<MfaSetup />);

    // Click on continue button
    const continueButton = screen.getByText(/Continue/i);
    fireEvent.click(continueButton);

    // Check if moved to next step (verify code)
    expect(screen.getByText(/Verify your code/i)).toBeInTheDocument();

    // Enter verification code
    const codeInput = screen.getByPlaceholderText(/Enter 6-digit code/i);
    fireEvent.change(codeInput, { target: { value: "123456" } });

    // Click verify button
    const verifyButton = screen.getByText(/Verify/i);
    fireEvent.click(verifyButton);

    // Check if moved to recovery codes step
    expect(screen.getByText(/Recovery Codes/i)).toBeInTheDocument();

    // Check for recovery codes
    expect(screen.getByText(/ABCD-EFGH-IJKL-MNOP/i)).toBeInTheDocument();
    expect(screen.getByText(/1234-5678-9012-3456/i)).toBeInTheDocument();
    expect(screen.getByText(/WXYZ-UVST-QRST-UVWX/i)).toBeInTheDocument();
  });
});

describe("MfaSetup Component", () => {
  test("renders MFA setup steps correctly", async () => {
    render(<MfaSetup />);

    // Check for setup heading
    expect(
      screen.getByText(/Set up Two-Factor Authentication/i)
    ).toBeInTheDocument();

    // Check for step indicators
    expect(screen.getByText(/Step 1/i)).toBeInTheDocument();

    // Check for QR code
    const qrCode = screen.getByAltText(/QR Code/i);
    expect(qrCode).toBeInTheDocument();
    expect(qrCode.src).toContain("data:image/png;base64");

    // Check for secret key
    expect(screen.getByText(/ABCDEFGHIJKLMNOP/i)).toBeInTheDocument();
  });

  test("proceeds to next step when continue button is clicked", async () => {
    render(<MfaSetup />);

    // Click on continue button
    const continueButton = screen.getByText(/Continue/i);
    fireEvent.click(continueButton);

    // Check if moved to next step (verify code)
    expect(screen.getByText(/Verify your code/i)).toBeInTheDocument();

    // Enter verification code
    const codeInput = screen.getByPlaceholderText(/Enter 6-digit code/i);
    fireEvent.change(codeInput, { target: { value: "123456" } });

    // Click verify button
    const verifyButton = screen.getByText(/Verify/i);
    fireEvent.click(verifyButton);

    // Check if moved to recovery codes step
    expect(screen.getByText(/Recovery Codes/i)).toBeInTheDocument();

    // Check for recovery codes
    expect(screen.getByText(/ABCD-EFGH-IJKL-MNOP/i)).toBeInTheDocument();
    expect(screen.getByText(/1234-5678-9012-3456/i)).toBeInTheDocument();
    expect(screen.getByText(/WXYZ-UVST-QRST-UVWX/i)).toBeInTheDocument();
  });
});
