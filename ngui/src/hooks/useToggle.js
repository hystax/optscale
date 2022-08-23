import { useCallback, useState } from "react";

export const useToggle = (initialState) => {
  const [isToggled, setIsToggled] = useState(initialState);

  const toggle = useCallback(() => setIsToggled((state) => !state), []);

  return [isToggled, toggle];
};
