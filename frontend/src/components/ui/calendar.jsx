import React from "react";
import { cn } from "../../lib/utils";

const Calendar = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "p-3 bg-white border border-gray-200 rounded-md shadow-lg",
      className
    )}
    {...props}
  >
    <div className="text-sm text-gray-500 text-center p-4">
      Calendar component placeholder
      <br />
      (Full calendar implementation would go here)
    </div>
  </div>
));

Calendar.displayName = "Calendar";

export { Calendar };
