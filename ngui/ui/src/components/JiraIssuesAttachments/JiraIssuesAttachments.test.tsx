import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import JiraIssuesAttachments from "./JiraIssuesAttachments";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <JiraIssuesAttachments />
    </TestProvider>
  );
  root.unmount();
});
