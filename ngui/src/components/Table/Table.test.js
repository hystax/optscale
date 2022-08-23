import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Table from "./Table";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Table
        localization={{
          emptyMessageId: "notFound"
        }}
        data={[]}
        columns={[]}
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
