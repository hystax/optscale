import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import UpdateCostModelSideModal from "./UpdateCostModelSideModal";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <UpdateCostModelSideModal isOpen setIsOpen={jest.fn} cloudAccountId="cloudAccountId" costModel={{}} />
    </TestProvider>
  );
  root.unmount();
});
