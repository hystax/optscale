import { useCallback, useState } from "react";

export const useBoundingClientRect = () => {
  const [rectangle, setRectangle] = useState({});
  const [domElement, setDomElement] = useState(null);

  /* 
   https://reactjs.org/docs/hooks-faq.html#how-can-i-measure-a-dom-node
   
   It will allow us not to call useEffect in components and have a separate state for the measurements.
   It does not handle dynamic events such as scroll and resize.
   At the moment of the implementation it was not required, use useResizeObserver in that case.
  */

  const measuredRef = useCallback((node) => {
    if (node !== null) {
      setRectangle(node.getBoundingClientRect());
      setDomElement(node);
    }
  }, []);

  return [rectangle, measuredRef, domElement];
};
