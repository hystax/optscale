import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import FormattedDuration from "./FormattedDuration";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <FormattedDuration durationInSeconds={0} />
    </TestProvider>
  );
  root.unmount();
});
