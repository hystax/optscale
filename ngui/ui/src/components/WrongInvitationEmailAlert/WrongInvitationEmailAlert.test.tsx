import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import WrongInvitationEmailAlert from "./WrongInvitationEmailAlert";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <WrongInvitationEmailAlert />
    </TestProvider>
  );
  root.unmount();
});
