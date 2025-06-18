import React, { Suspense } from "react";
import { Loader } from "lucide-react";

/**
 * LazyLoader component to handle loading state for lazy-loaded components
 *
 * @param {Object} props Component properties
 * @param {React.ReactNode} props.children The lazy-loaded component to render
 * @param {string} props.fallbackText Optional text to display during loading
 * @returns {React.ReactElement} The rendered component with loading state
 */
const LazyLoader = ({ children, fallbackText = "Loading..." }) => {
  const LoadingFallback = () => (
    <div className="flex flex-col items-center justify-center min-h-[40vh]">
      <Loader className="h-10 w-10 animate-spin text-primary" />
      <p className="mt-4 text-md text-muted-foreground">{fallbackText}</p>
    </div>
  );

  return <Suspense fallback={<LoadingFallback />}>{children}</Suspense>;
};

export default LazyLoader;
