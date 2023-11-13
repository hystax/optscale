import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import CurrentBooking from "./CurrentBooking";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <CurrentBooking employeeName="A" acquiredSince={1} releasedAt={2} />
    </TestProvider>
  );
  root.unmount();
});
