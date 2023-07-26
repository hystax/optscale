import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import MlRunsetTemplateEdit from "./MlRunsetTemplateEdit";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlRunsetTemplateEdit
        models={[]}
        dataSources={[]}
        runsetTemplate={{}}
        onSubmit={jest.fn}
        onCancel={jest.fn}
        defaultValues={{}}
      />
    </TestProvider>
  );
  root.unmount();
});
