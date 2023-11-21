import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import ConfigureFrame from "frames/configure";
import IssuePanelFrame from "frames/issue_left_panel";

const container = document.getElementById("root");
const root = createRoot(container);

root.render(
  <BrowserRouter>
    <Routes>
      <Route path="/jira_ui/configure/" element={<ConfigureFrame />} />
      <Route path="/jira_ui/issue_left_panel/" element={<IssuePanelFrame />} />
    </Routes>
  </BrowserRouter>
);
