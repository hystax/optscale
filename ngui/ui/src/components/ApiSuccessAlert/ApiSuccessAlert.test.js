import React from "react";
import { createRoot } from "react-dom/client";
import { LATEST_SUCCESS_HANDLED_LABEL } from "api/reducer";
import TestProvider from "tests/TestProvider";
import ApiSuccessAlert from "./ApiSuccessAlert";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider
      state={{
        api: { [LATEST_SUCCESS_HANDLED_LABEL]: "" }
      }}
    >
      <ApiSuccessAlert />
    </TestProvider>
  );
  root.unmount();
});
