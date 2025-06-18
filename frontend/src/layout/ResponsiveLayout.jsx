import React, { useState } from "react";
import { motion } from "framer-motion";
import { X, Menu, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";

/**
 * Responsive layout component that adapts to different screen sizes
 * Features a collapsible sidebar and mobile navigation
 */
const ResponsiveLayout = ({ children, sidebar }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Toggle sidebar
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  // Toggle mobile menu
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile Header */}
      <header className="lg:hidden bg-white border-b px-4 py-3 flex justify-between items-center sticky top-0 z-20">
        <Button variant="ghost" size="icon" onClick={toggleMobileMenu}>
          <Menu className="h-5 w-5" />
        </Button>
        <div className="flex-1 flex justify-center">
          <img src="/logo.svg" alt="Catalyst Logo" className="h-8" />
        </div>
        <div className="w-8"></div> {/* Placeholder for balance */}
      </header>

      {/* Mobile Sidebar Overlay */}
      {isMobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={toggleMobileMenu}
        ></div>
      )}

      {/* Mobile Sidebar */}
      <div
        className={`fixed top-0 left-0 h-full bg-white z-40 w-64 transform transition-transform duration-300 ease-in-out lg:hidden ${
          isMobileMenuOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="p-4 border-b flex justify-between items-center">
          <div className="font-bold text-lg">Catalyst</div>
          <Button variant="ghost" size="icon" onClick={toggleMobileMenu}>
            <X className="h-5 w-5" />
          </Button>
        </div>
        <div className="overflow-y-auto h-[calc(100%-60px)] pb-20">
          {sidebar}
        </div>
      </div>

      {/* Desktop Layout */}
      <div className="flex h-screen overflow-hidden">
        {/* Desktop Sidebar */}
        <div
          className={`hidden lg:block bg-white border-r transition-all duration-300 ${
            isSidebarOpen ? "w-64" : "w-20"
          } flex-shrink-0 overflow-y-auto`}
        >
          <div
            className={`p-4 border-b flex ${isSidebarOpen ? "justify-between" : "justify-center"} items-center`}
          >
            {isSidebarOpen ? (
              <>
                <div className="font-bold text-lg">Catalyst</div>
                <Button variant="ghost" size="icon" onClick={toggleSidebar}>
                  <ChevronLeft className="h-5 w-5" />
                </Button>
              </>
            ) : (
              <Button variant="ghost" size="icon" onClick={toggleSidebar}>
                <ChevronRight className="h-5 w-5" />
              </Button>
            )}
          </div>

          <div className="overflow-y-auto">
            {/* Conditionally render sidebar content based on collapsed state */}
            {isSidebarOpen ? (
              sidebar
            ) : (
              <div className="py-4 flex flex-col items-center">
                {/* Icons-only version of the sidebar */}
                {React.Children.map(sidebar.props.children, (child) => {
                  // Extract just the icon from each sidebar item
                  if (React.isValidElement(child) && child.props.icon) {
                    return (
                      <div className="p-2 rounded-md hover:bg-gray-100 mb-2 cursor-pointer">
                        {child.props.icon}
                      </div>
                    );
                  }
                  return null;
                })}
              </div>
            )}
          </div>
        </div>

        {/* Main Content */}
        <motion.main
          className={`flex-1 overflow-y-auto transition-all duration-300 relative`}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          {children}
        </motion.main>
      </div>
    </div>
  );
};

export default ResponsiveLayout;
