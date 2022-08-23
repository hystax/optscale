import { useRef, useState } from "react";

export const useInitialMount = () => {
  const isInitialMountRef = useRef(true);
  const [isInitialMount, setIsInitialMount] = useState(isInitialMountRef.current);

  return { isInitialMount, setIsInitialMount };
};
