import { createRoot } from "react-dom/client";
import { BOOKING_ACQUIRE } from "services/WebhooksService";
import TestProvider from "tests/TestProvider";
import EnvironmentWebhook from "./EnvironmentWebhook";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <EnvironmentWebhook webhook={{}} resourceId="" action={BOOKING_ACQUIRE} />
    </TestProvider>
  );
  root.unmount();
});
