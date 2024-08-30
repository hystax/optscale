import { useEffect, useState } from "react";

const DEFAULT_DELAY = 1000;

const defaultEqualityFn = <T>(left: T, right: T): boolean => left === right;

type UseDebouncedValueOptions<T> = {
  delay?: number;
  onDebouncedValueChange?: (value: T) => void;
  equalityFn?: (left: T, right: T) => boolean;
};

export const useDebouncedValue = <T>(value: T, options: UseDebouncedValueOptions<T> = {}): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  const { delay = DEFAULT_DELAY, onDebouncedValueChange, equalityFn = defaultEqualityFn } = options;

  useEffect(() => {
    const timer = setTimeout(() => {
      if (!equalityFn(value, debouncedValue)) {
        setDebouncedValue(value);
        if (typeof onDebouncedValueChange === "function") {
          onDebouncedValueChange(value);
        }
      }
    }, delay);

    return () => {
      clearTimeout(timer);
    };
  }, [debouncedValue, delay, equalityFn, onDebouncedValueChange, value]);

  return debouncedValue;
};
