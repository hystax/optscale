import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import TextWithDataTestId from "./TextWithDataTestId";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <TextWithDataTestId dataTestId="test">test</TextWithDataTestId>
    </TestProvider>
  );
  root.unmount();
});
