import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ResetPasswordForm from "./ResetPasswordForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ResetPasswordForm onSubmit={() => console.log("submit")} isLoading={false} sendState="SUCCESS" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
