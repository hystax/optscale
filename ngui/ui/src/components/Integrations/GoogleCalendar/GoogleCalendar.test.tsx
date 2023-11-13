import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import GoogleCalendar from "./GoogleCalendar";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <GoogleCalendar calendarSynchronization={{}} />
    </TestProvider>
  );
  root.unmount();
});
