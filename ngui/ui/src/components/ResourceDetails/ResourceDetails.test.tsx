import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ResourceDetails from "./ResourceDetails";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ResourceDetails details={{}} name="name" resourceType="type" tags={{}} meta={{}} />
    </TestProvider>
  );
  root.unmount();
});
