import { useRef, useEffect, useState } from "react";
import ResizeObserver from "resize-observer-polyfill";

export const useResizeObserver = (ref) => {
  const resizeObserverRef = useRef();

  const [width, setWidth] = useState(0);
  const [height, setHeight] = useState(0);

  useEffect(() => {
    if (resizeObserverRef.current) {
      return;
    }
    resizeObserverRef.current = new ResizeObserver((entries) => {
      const { width: rectWidth, height: rectHeight } = entries[0].contentRect;

      setWidth(rectWidth);
      setHeight(rectHeight);
    });
  }, [setWidth, setHeight]);

  useEffect(() => {
    if (!ref.current) {
      return undefined;
    }
    const element = ref.current;

    resizeObserverRef.current.observe(element);

    return () => resizeObserverRef.current.unobserve(element);
  }, [ref]);

  return { width, height };
};
