import * as React from "react";
import * as SliderPrimitive from "@radix-ui/react-slider";
import { cn } from "../../lib/utils";

interface SliderProps
  extends React.ComponentPropsWithoutRef<typeof SliderPrimitive.Root> {
  label?: string;
  description?: string;
  showValue?: boolean;
  unit?: string;
  formatValue?: (value: number) => string;
}

const Slider = React.forwardRef<
  React.ElementRef<typeof SliderPrimitive.Root>,
  SliderProps
>(
  (
    {
      className,
      label,
      description,
      showValue = true,
      unit,
      formatValue,
      value,
      defaultValue,
      ...props
    },
    ref
  ) => {
    const currentValues = value ?? defaultValue ?? [0];
    const displayValue = currentValues
      .map(current => formatValue ? formatValue(current) : current.toString())
      .join(" – ");

    return (
      <div className="space-y-3">
        {(label || showValue) && (
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              {label && (
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  {label}
                </label>
              )}
              {description && (
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                  {description}
                </p>
              )}
            </div>
            {showValue && (
              <span className="text-sm font-mono text-gray-600 dark:text-gray-400">
                {displayValue}
                {unit && ` ${unit}`}
              </span>
            )}
          </div>
        )}
        <SliderPrimitive.Root
          ref={ref}
          value={value}
          defaultValue={defaultValue}
          className={cn(
            "relative flex w-full touch-none select-none items-center",
            className
          )}
          {...props}
        >
          <SliderPrimitive.Track className="relative h-2 w-full grow overflow-hidden rounded-full bg-secondary">
            <SliderPrimitive.Range className="absolute h-full bg-primary" />
          </SliderPrimitive.Track>
          {currentValues.map((_, index) => (
            <SliderPrimitive.Thumb
              key={index}
              aria-label={currentValues.length === 1 ? label : `${label ?? "Range"} ${index === 0 ? "minimum" : index === currentValues.length - 1 ? "maximum" : index + 1}`}
              className="block h-5 w-5 rounded-full border-2 border-primary bg-background ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:bg-accent"
            />
          ))}
        </SliderPrimitive.Root>
      </div>
    );
  }
);
Slider.displayName = SliderPrimitive.Root.displayName;

export { Slider };
