import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import { AWS_CNR } from "utils/constants";
import UpdateDataSourceCredentialsForm from "./UpdateDataSourceCredentialsForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <UpdateDataSourceCredentialsForm id="id" type={AWS_CNR} config={{}} onSubmit={vi.fn} />
    </TestProvider>
  );
  root.unmount();
});
