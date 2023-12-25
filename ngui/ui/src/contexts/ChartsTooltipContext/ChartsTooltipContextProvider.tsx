import React from "react";
import ChartsTooltipContext from "./ChartsTooltipContext";

const ChartsTooltipContextProvider = ({ children, setMousePosition, mousePosition }) => (
  <ChartsTooltipContext.Provider value={{ setMousePosition, mousePosition }}>{children}</ChartsTooltipContext.Provider>
);

export default ChartsTooltipContextProvider;
