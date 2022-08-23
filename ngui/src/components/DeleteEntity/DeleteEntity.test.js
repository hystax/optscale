import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import DeleteEntity from "./DeleteEntity";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <DeleteEntity
        message={{ messageId: "deleteResourcesQuestion", values: { count: 1 } }}
        deleteButtonProps={{
          onDelete: () => jest.fn
        }}
        onCancel={() => jest.fn}
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
