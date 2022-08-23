import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ButtonGroup from "./ButtonGroup";

it("renders with action", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ButtonGroup
        activeButtonIndex={0}
        buttons={[
          {
            id: "add",
            messageId: "add",
            onClick: (e) => console.log(e)
          }
        ]}
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
