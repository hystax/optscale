const path = require("path");
const express = require("express");

const BUILD_PATH = path.join(__dirname, "build");
const BUILD_INDEX_PATH = path.join(__dirname, "build", "index.html");
const BUILD_STORYBOOK_PATH = path.join(__dirname, "storybook");
const BUILD_STORYBOOK_INDEX_PATH = path.join(__dirname, "storybook", "index.html");

const app = express();

app.use(express.static(BUILD_PATH));
app.use(express.static(BUILD_STORYBOOK_PATH));

app.use("/storybook", (req, res) => {
  res.sendFile(BUILD_STORYBOOK_INDEX_PATH);
});

app.use("*", (req, res) => {
  res.sendFile(BUILD_INDEX_PATH);
});

app.listen(9999);
