import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import ConfigureFrame from "frames/configure";
import IssuePanelFrame from "frames/issue_left_panel";

const container = document.getElementById("root");
const root = createRoot(container);

root.render(
  <div
    /*
      ac-content class: This class wraps the contents of the app and dynamically resizes the iframe in Jira. 
      This class keeps the app content visible without scrollbars.
      https://developer.atlassian.com/cloud/jira/software/getting-started/#step-2--create-the-user-interface
    */
    className="ac-content"
  >
    <BrowserRouter>
      <Routes>
        <Route path="/jira_ui/configure/" element={<ConfigureFrame />} />
        <Route path="/jira_ui/issue_left_panel/" element={<IssuePanelFrame />} />
      </Routes>
    </BrowserRouter>
  </div>
);
