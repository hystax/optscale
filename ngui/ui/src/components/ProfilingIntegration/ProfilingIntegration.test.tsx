import { createRoot } from "react-dom/client";
import { ProfilingIntegrationModalContextProvider } from "contexts/ProfilingIntegrationModalContext";
import TestProvider from "tests/TestProvider";
import ProfilingIntegration from "./ProfilingIntegration";

it("renders with action", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ProfilingIntegrationModalContextProvider onClose={vi.fn}>
        <ProfilingIntegration />
      </ProfilingIntegrationModalContextProvider>
    </TestProvider>
  );
  root.unmount();
});
