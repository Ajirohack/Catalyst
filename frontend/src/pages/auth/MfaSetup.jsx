import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { toast } from "react-hot-toast";
import {
  Smartphone,
  Loader,
  Shield,
  Mail,
  CheckCircle,
  X,
  AlertTriangle,
  LockKeyhole,
  KeyRound,
  InfoIcon,
  Copy,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
} from "../../components/ui/tabs";
import securityUtils from "../../utils/securityUtils";

export default function MfaSetup() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [mfaMethod, setMfaMethod] = useState("app");
  const [isLoading, setIsLoading] = useState(false);
  const [otpCode, setOtpCode] = useState("");
  const [recoveryCodesVisible, setRecoveryCodesVisible] = useState(false);
  const [email, setEmail] = useState("");
  const [secret, setSecret] = useState("");
  const [qrCodeUrl, setQrCodeUrl] = useState("");
  const [recoveryCodes, setRecoveryCodes] = useState([]);

  useEffect(() => {
    // Get user email - in a real app, this would come from user context or profile
    setEmail("user@example.com");

    // Generate the MFA secret and QR code
    const generatedSecret = securityUtils.generateTOTPSecret();
    setSecret(generatedSecret);

    const qrUrl = securityUtils.getTOTPQRCodeUrl(generatedSecret, email);
    setQrCodeUrl(qrUrl);

    // Generate recovery codes
    generateRecoveryCodes();
  }, []);

  const generateRecoveryCodes = () => {
    // In a real app, these would be generated on the server and returned via API
    const codes = [];
    for (let i = 0; i < 10; i++) {
      codes.push(
        Math.random().toString(36).substring(2, 6).toUpperCase() +
          "-" +
          Math.random().toString(36).substring(2, 6).toUpperCase() +
          "-" +
          Math.random().toString(36).substring(2, 6).toUpperCase()
      );
    }
    setRecoveryCodes(codes);
  };

  const handleVerifyCode = () => {
    setIsLoading(true);

    // In a real app, this would verify with the server
    setTimeout(() => {
      setIsLoading(false);

      // Simulate success (in production, this would check against the TOTP algorithm)
      if (otpCode.length === 6) {
        toast.success("MFA verification successful!");
        setStep(2);
      } else {
        toast.error("Invalid verification code. Please try again.");
      }
    }, 1500);
  };

  const handleCompleteMfaSetup = () => {
    setIsLoading(true);

    // In a real app, this would call an API to enable MFA on the user's account
    setTimeout(() => {
      setIsLoading(false);

      // Store MFA settings locally
      securityUtils.storeMFASettings(true, mfaMethod);

      // Save device as trusted
      const deviceInfo = securityUtils.getDeviceInfo();
      securityUtils.addTrustedDevice(deviceInfo);

      toast.success("Two-factor authentication has been enabled!");
      navigate("/settings", { state: { mfaEnabled: true } });
    }, 1500);
  };

  const copyRecoveryCodes = () => {
    navigator.clipboard.writeText(recoveryCodes.join("\n"));
    toast.success("Recovery codes copied to clipboard!");
  };

  const pageVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0, transition: { duration: 0.3 } },
    exit: { opacity: 0, y: -20, transition: { duration: 0.2 } },
  };

  return (
    <motion.div
      className="container max-w-md py-12"
      initial="initial"
      animate="animate"
      exit="exit"
      variants={pageVariants}
    >
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Shield className="mr-2 h-6 w-6 text-primary" />
            Two-Factor Authentication Setup
          </CardTitle>
          <CardDescription>
            Enhance your account security with two-factor authentication
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="app" onValueChange={setMfaMethod}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="app">
                <Smartphone className="h-4 w-4 mr-2" />
                Authenticator App
              </TabsTrigger>
              <TabsTrigger value="email">
                <Mail className="h-4 w-4 mr-2" />
                Email
              </TabsTrigger>
            </TabsList>

            <TabsContent value="app" className="mt-4">
              {step === 1 && (
                <div className="space-y-4">
                  <div className="rounded-lg bg-muted p-4">
                    <h3 className="text-sm font-medium mb-2">
                      Step 1: Scan QR Code
                    </h3>
                    <p className="text-xs text-muted-foreground mb-4">
                      Use an authenticator app like Google Authenticator, Authy,
                      or Microsoft Authenticator to scan this QR code.
                    </p>

                    <div className="flex justify-center my-4">
                      {qrCodeUrl ? (
                        <img
                          src={qrCodeUrl}
                          alt="QR Code for MFA"
                          className="h-48 w-48 border border-border rounded"
                        />
                      ) : (
                        <div className="h-48 w-48 border border-border rounded flex items-center justify-center">
                          <Loader className="h-8 w-8 animate-spin text-muted-foreground" />
                        </div>
                      )}
                    </div>

                    <div className="mt-4">
                      <p className="text-xs mb-1">
                        Can't scan the QR code? Use this setup key instead:
                      </p>
                      <div className="flex items-center space-x-2 bg-background rounded border p-2 text-sm font-mono">
                        <span className="flex-1 overflow-hidden overflow-ellipsis">
                          {secret}
                        </span>
                        <Button
                          size="icon"
                          variant="ghost"
                          onClick={() => {
                            navigator.clipboard.writeText(secret);
                            toast.success("Secret copied to clipboard!");
                          }}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="otpCode">Verification Code</Label>
                    <Input
                      id="otpCode"
                      placeholder="Enter 6-digit code"
                      value={otpCode}
                      onChange={(e) =>
                        setOtpCode(
                          e.target.value.replace(/\D/g, "").substring(0, 6)
                        )
                      }
                      maxLength={6}
                    />
                  </div>

                  <Button
                    onClick={handleVerifyCode}
                    disabled={otpCode.length !== 6 || isLoading}
                    className="w-full"
                  >
                    {isLoading ? (
                      <>
                        <Loader className="mr-2 h-4 w-4 animate-spin" />{" "}
                        Verifying...
                      </>
                    ) : (
                      <>
                        <KeyRound className="mr-2 h-4 w-4" /> Verify Code
                      </>
                    )}
                  </Button>
                </div>
              )}

              {step === 2 && (
                <div className="space-y-4">
                  <div className="rounded-lg bg-muted p-4">
                    <h3 className="text-sm font-medium flex items-center">
                      <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                      Verification Successful
                    </h3>
                    <p className="text-xs text-muted-foreground mt-1">
                      You've successfully set up two-factor authentication.
                    </p>
                  </div>

                  <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
                    <h3 className="text-sm font-medium flex items-center text-amber-800">
                      <AlertTriangle className="h-4 w-4 mr-2 text-amber-500" />
                      Save Your Recovery Codes
                    </h3>
                    <p className="text-xs text-amber-700 mt-1 mb-3">
                      If you lose access to your authenticator app, you'll need
                      these recovery codes to access your account. Keep them in
                      a safe place.
                    </p>

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() =>
                        setRecoveryCodesVisible(!recoveryCodesVisible)
                      }
                      className="mb-2"
                    >
                      {recoveryCodesVisible
                        ? "Hide Codes"
                        : "Show Recovery Codes"}
                    </Button>

                    {recoveryCodesVisible && (
                      <div className="mt-2 p-3 bg-white border rounded font-mono text-xs">
                        {recoveryCodes.map((code, index) => (
                          <div key={index} className="py-1">
                            {code}
                          </div>
                        ))}
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={copyRecoveryCodes}
                          className="mt-2 w-full"
                        >
                          <Copy className="h-3 w-3 mr-1" /> Copy All Codes
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </TabsContent>

            <TabsContent value="email" className="mt-4">
              <div className="space-y-4">
                <div className="rounded-lg bg-muted p-4">
                  <h3 className="text-sm font-medium mb-2">
                    Email-Based Verification
                  </h3>
                  <p className="text-xs text-muted-foreground">
                    We'll send a verification code to your email whenever you
                    sign in from a new device.
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="emailAddress">Confirm Your Email</Label>
                  <Input
                    id="emailAddress"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your@email.com"
                  />
                </div>

                <div className="flex items-start space-x-2 text-xs">
                  <InfoIcon className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                  <p className="text-muted-foreground">
                    Note: Email-based verification is less secure than using an
                    authenticator app, but can be more convenient.
                  </p>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
        <CardFooter className="flex justify-between">
          <Button variant="outline" onClick={() => navigate("/settings")}>
            Cancel
          </Button>

          {step === 2 ? (
            <Button onClick={handleCompleteMfaSetup} disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader className="mr-2 h-4 w-4 animate-spin" /> Processing...
                </>
              ) : (
                <>
                  <CheckCircle className="mr-2 h-4 w-4" /> Complete Setup
                </>
              )}
            </Button>
          ) : (
            mfaMethod === "email" && (
              <Button
                onClick={() => setStep(2)}
                disabled={!email.includes("@")}
              >
                <Mail className="mr-2 h-4 w-4" /> Send Verification
              </Button>
            )
          )}
        </CardFooter>
      </Card>
    </motion.div>
  );
}
