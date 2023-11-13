import ProfilingIntegrationModalContext from "./ProfilingIntegrationModalContext";

const ProfilingIntegrationModalContextProvider = ({ children, onClose }) => (
  <ProfilingIntegrationModalContext.Provider
    value={{
      onClose
    }}
  >
    {children}
  </ProfilingIntegrationModalContext.Provider>
);

export default ProfilingIntegrationModalContextProvider;
