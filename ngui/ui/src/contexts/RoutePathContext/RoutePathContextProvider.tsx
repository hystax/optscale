import { ReactNode } from "react";
import CurrentPathTemplateContext from "./RoutePathContext";

type RoutePathContextProviderProps = {
  children: ReactNode;
  path: string;
};

const RoutePathContextProvider = ({ children, path }: RoutePathContextProviderProps) => (
  <CurrentPathTemplateContext.Provider value={path}>{children}</CurrentPathTemplateContext.Provider>
);

export default RoutePathContextProvider;
