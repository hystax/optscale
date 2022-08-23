import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ProfileMenuContainer from "./ProfileMenuContainer";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider
      state={{
        auth: { GET_TOKEN: { userId: "123" } }
      }}
    >
      <ProfileMenuContainer name={"profile-name"} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
