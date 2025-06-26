import React, { useState, useEffect } from "react";
import {
  Eye,
  EyeOff,
  Lock,
  Mail,
  Shield,
  AlertCircle,
  CheckCircle,
  X,
  Loader,
} from "lucide-react";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../../components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import { Alert, AlertDescription, AlertTitle } from "../../components/ui/alert";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { useAuth } from "../../context/AuthContext";
import { toast } from "react-hot-toast";

const Login = () => {
  const { login, loading, isInitializing } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Form states
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [cooldownRemaining, setCooldownRemaining] = useState(0);

  // 2FA states
  const [show2FA, setShow2FA] = useState(false);
  const [twoFactorCode, setTwoFactorCode] = useState("");

  // Error handling
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});

  // Extract the reason for redirection to login page if any
  const { state } = location;
  const redirectReason = state?.reason;
  const from = state?.from?.pathname || "/dashboard";

  // Check for login cooldown on component mount
  useEffect(() => {
    const checkCooldown = () => {
      // const remaining = securityUtils.getLoginCooldownRemaining();
      const remaining = 0;
      setCooldownRemaining(remaining);

      if (remaining > 0) {
        const timer = setInterval(() => {
          // const newRemaining = securityUtils.getLoginCooldownRemaining();
          const newRemaining = 0;
          setCooldownRemaining(newRemaining);

          if (newRemaining <= 0) {
            clearInterval(timer);
          }
        }, 1000);

        return () => clearInterval(timer);
      }
    };

    checkCooldown();
  }, []);

  // Reset error when form changes
  useEffect(() => {
    setError("");
    setFieldErrors({});
  }, [email, password]);

  // Handle session expiry message
  useEffect(() => {
    if (redirectReason) {
      let message = "";

      switch (redirectReason) {
        case "session_expired":
          message = "Your session has expired. Please log in again.";
          break;
        case "inactivity":
          message = "You were logged out due to inactivity.";
          break;
        case "security_concern":
          message = "You were logged out due to a security concern.";
          break;
        case "logged_out_in_other_tab":
          message = "You were logged out in another tab.";
          break;
        default:
          break;
      }

      if (message) {
        setError(message);
      }
    }
  }, [redirectReason]);

  // Form validation
  const validateForm = () => {
    const errors = {};

    if (!email) {
      errors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.email = "Please enter a valid email address";
    }

    if (!password) {
      errors.password = "Password is required";
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle login form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Check if in cooldown period
    if (cooldownRemaining > 0) {
      setError(
        `Too many failed attempts. Please try again in ${cooldownRemaining} seconds.`
      );
      return;
    }

    // Validate form
    if (!validateForm()) {
      return;
    }

    try {
      setError("");
      const response = await login({ email, password }, rememberMe);

      if (response?.requiresTwoFactor) {
        setShow2FA(true);
        toast.success(
          "Please enter the verification code from your authenticator app."
        );
      } else {
        toast.success("Login successful!");
        navigate(from, { replace: true });
      }
    } catch (error) {
      console.error("Login error:", error);

      if (error.response?.status === 423) {
        // Account locked
        setError(
          "Your account has been locked due to too many failed attempts. Please contact support."
        );
      } else {
        setError(error.response?.data?.message || "Invalid email or password");
      }
    }
  };

  // Handle 2FA verification
  const handleVerify2FA = async (e) => {
    e.preventDefault();

    if (!twoFactorCode) {
      setFieldErrors({ twoFactorCode: "Verification code is required" });
      return;
    }

    try {
      setError("");
      await login.verify2FA(twoFactorCode);
      toast.success("Verification successful!");
      navigate(from, { replace: true });
    } catch (error) {
      console.error("2FA verification error:", error);
      setError(error.response?.data?.message || "Invalid verification code");
    }
  };

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.4,
      },
    },
  };

  // If auth is still initializing, show loading state
  if (isInitializing) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader className="h-12 w-12 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-background p-4">
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="w-full max-w-md"
      >
        <div className="flex justify-center mb-6">
          <motion.img
            src="/assets/catalyst-logo.svg"
            alt="Catalyst Logo"
            className="h-16 w-auto"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5 }}
          />
        </div>

        <motion.div variants={itemVariants}>
          <Card className="border-border/40 shadow-lg">
            <CardHeader>
              <CardTitle>Welcome to Catalyst</CardTitle>
              <CardDescription>
                Sign in to your account to continue
              </CardDescription>
            </CardHeader>

            <CardContent>
              <Tabs defaultValue="login" className="w-full">
                <TabsList className="grid w-full grid-cols-2 mb-4">
                  <TabsTrigger value="login">Login</TabsTrigger>
                  <TabsTrigger value="register">Register</TabsTrigger>
                </TabsList>

                <TabsContent value="login" className="space-y-4">
                  {/* Error Display */}
                  {error && (
                    <Alert variant="destructive">
                      <AlertCircle className="h-4 w-4" />
                      <AlertTitle>Error</AlertTitle>
                      <AlertDescription>{error}</AlertDescription>
                    </Alert>
                  )}

                  {/* Cooldown Warning */}
                  {cooldownRemaining > 0 && (
                    <Alert variant="destructive">
                      <AlertCircle className="h-4 w-4" />
                      <AlertTitle>Account Protection</AlertTitle>
                      <AlertDescription>
                        Too many failed attempts. Please try again in{" "}
                        {cooldownRemaining} seconds.
                      </AlertDescription>
                    </Alert>
                  )}

                  {/* Login Form or 2FA Form */}
                  {!show2FA ? (
                    <form onSubmit={handleSubmit} className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="email">Email</Label>
                        <div className="relative">
                          <Mail className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                          <Input
                            id="email"
                            type="email"
                            placeholder="you@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className={`pl-10 ${
                              fieldErrors.email ? "border-red-500" : ""
                            }`}
                            disabled={loading || cooldownRemaining > 0}
                          />
                        </div>
                        {fieldErrors.email && (
                          <p className="text-sm text-red-500">
                            {fieldErrors.email}
                          </p>
                        )}
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <Label htmlFor="password">Password</Label>
                          <Link
                            to="/forgot-password"
                            className="text-xs text-primary hover:underline"
                          >
                            Forgot password?
                          </Link>
                        </div>
                        <div className="relative">
                          <Lock className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                          <Input
                            id="password"
                            type={showPassword ? "text" : "password"}
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className={`pl-10 ${
                              fieldErrors.password ? "border-red-500" : ""
                            }`}
                            disabled={loading || cooldownRemaining > 0}
                          />
                          <button
                            type="button"
                            onClick={() => setShowPassword(!showPassword)}
                            className="absolute right-3 top-2.5 text-muted-foreground"
                            disabled={loading}
                          >
                            {showPassword ? (
                              <EyeOff className="h-4 w-4" />
                            ) : (
                              <Eye className="h-4 w-4" />
                            )}
                          </button>
                        </div>
                        {fieldErrors.password && (
                          <p className="text-sm text-red-500">
                            {fieldErrors.password}
                          </p>
                        )}
                      </div>

                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="remember"
                          className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                          checked={rememberMe}
                          onChange={(e) => setRememberMe(e.target.checked)}
                          disabled={loading}
                        />
                        <Label htmlFor="remember" className="text-sm">
                          Remember me for 30 days
                        </Label>
                      </div>

                      <Button
                        type="submit"
                        className="w-full"
                        disabled={loading || cooldownRemaining > 0}
                      >
                        {loading ? (
                          <>
                            <Loader className="mr-2 h-4 w-4 animate-spin" />
                            Signing in...
                          </>
                        ) : (
                          "Sign in"
                        )}
                      </Button>
                    </form>
                  ) : (
                    <form onSubmit={handleVerify2FA} className="space-y-4">
                      <div className="mb-4 text-center">
                        <Shield className="mx-auto h-12 w-12 text-primary mb-2" />
                        <h3 className="text-lg font-medium">
                          Two-Factor Authentication
                        </h3>
                        <p className="text-sm text-muted-foreground">
                          Enter the verification code from your authenticator
                          app
                        </p>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="twoFactorCode">Verification Code</Label>
                        <Input
                          id="twoFactorCode"
                          placeholder="Enter 6-digit code"
                          value={twoFactorCode}
                          onChange={(e) =>
                            setTwoFactorCode(
                              e.target.value.replace(/\D/g, "").slice(0, 6)
                            )
                          }
                          className={
                            fieldErrors.twoFactorCode ? "border-red-500" : ""
                          }
                          disabled={loading}
                          maxLength={6}
                        />
                        {fieldErrors.twoFactorCode && (
                          <p className="text-sm text-red-500">
                            {fieldErrors.twoFactorCode}
                          </p>
                        )}
                      </div>

                      <Button
                        type="submit"
                        className="w-full"
                        disabled={loading || twoFactorCode.length !== 6}
                      >
                        {loading ? (
                          <>
                            <Loader className="mr-2 h-4 w-4 animate-spin" />
                            Verifying...
                          </>
                        ) : (
                          "Verify"
                        )}
                      </Button>

                      <Button
                        type="button"
                        variant="ghost"
                        className="w-full"
                        onClick={() => setShow2FA(false)}
                        disabled={loading}
                      >
                        <X className="mr-2 h-4 w-4" />
                        Back to Login
                      </Button>
                    </form>
                  )}
                </TabsContent>

                <TabsContent value="register">
                  <div className="p-6 text-center">
                    <h3 className="text-lg font-medium mb-2">
                      Create a New Account
                    </h3>
                    <p className="text-sm text-muted-foreground mb-4">
                      Ready to get started with Catalyst?
                    </p>
                    <Link to="/register">
                      <Button className="w-full">Register Now</Button>
                    </Link>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>

            <CardFooter className="flex flex-col space-y-4">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-background px-2 text-muted-foreground">
                    Or continue with
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <Button variant="outline" type="button" disabled={loading}>
                  <svg
                    className="mr-2 h-4 w-4"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      fill="#4285F4"
                    />
                    <path
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      fill="#34A853"
                    />
                    <path
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"
                      fill="#FBBC05"
                    />
                    <path
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                      fill="#EA4335"
                    />
                  </svg>
                  Google
                </Button>
                <Button variant="outline" type="button" disabled={loading}>
                  <svg
                    className="mr-2 h-4 w-4"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path d="M12.0002 0C5.37249 0 0 5.37249 0 12.0002C0 17.3022 3.43809 21.8015 8.20481 23.3882C8.8069 23.5032 9.0102 23.1466 9.0102 22.8434C9.0102 22.5695 8.99656 21.484 8.99656 20.4812C5.66492 21.2154 4.97147 19.0419 4.97147 19.0419C4.43521 17.6635 3.64565 17.307 3.64565 17.307C2.55148 16.5729 3.72857 16.5729 3.72857 16.5729C4.9347 16.6455 5.5641 17.7987 5.5641 17.7987C6.63487 19.6098 8.36981 19.0963 9.03684 18.793C9.1379 18.0316 9.4411 17.5181 9.77252 17.2149C7.1213 16.9253 4.33371 15.8993 4.33371 11.332C4.33371 10.0263 4.80364 8.95949 5.58143 8.12076C5.46674 7.81756 5.04708 6.5983 5.70137 4.95421C5.70137 4.95421 6.70764 4.63735 8.99656 6.18334C9.97547 5.91996 10.9816 5.78827 12.0002 5.78827C13.0188 5.78827 14.0249 5.91996 15.0038 6.18334C17.2927 4.63735 18.299 4.95421 18.299 4.95421C18.9533 6.5983 18.5336 7.81756 18.4189 8.12076C19.2103 8.95949 19.6666 10.0263 19.6666 11.332C19.6666 15.8993 16.879 16.9116 14.2142 17.2149C14.6339 17.6008 14.9999 18.3486 14.9999 19.5132C14.9999 21.1709 14.9862 22.4493 14.9862 22.8434C14.9862 23.1466 15.1895 23.5032 15.7916 23.3882C20.5584 21.8015 23.9964 17.3022 23.9964 12.0002C24.0104 5.37249 18.6243 0 12.0002 0Z" />
                  </svg>
                  GitHub
                </Button>
              </div>
            </CardFooter>
          </Card>
        </motion.div>

        <motion.p
          variants={itemVariants}
          className="text-center text-sm text-muted-foreground mt-4"
        >
          By using Catalyst, you agree to our{" "}
          <Link to="/terms" className="text-primary hover:underline">
            Terms of Service
          </Link>{" "}
          and{" "}
          <Link to="/privacy" className="text-primary hover:underline">
            Privacy Policy
          </Link>
          .
        </motion.p>
      </motion.div>
    </div>
  );
};

export default Login;
