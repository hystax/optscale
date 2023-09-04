import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import ConfigureFrame from "frames/configure";
import IssuePanelFrame from "frames/issue_left_panel";
import reportWebVitals from "./reportWebVitals";

ReactDOM.render(
  <Router>
    <Switch>
      <Route path="/jira_ui/configure/">
        <ConfigureFrame />
      </Route>
      <Route path="/jira_ui/issue_left_panel/">
        <IssuePanelFrame />
      </Route>
    </Switch>
  </Router>,
  document.getElementById("root")
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
