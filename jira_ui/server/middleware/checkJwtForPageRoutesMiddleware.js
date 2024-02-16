const pagePathPattern = /\/jira_ui\/(configure|issue_left_panel)/;

const checkJwtForPageRoutesMiddleware = (app) => {
  app.use(pagePathPattern, async (req, res, next) => {
    const { jwt } = req.query;

    const response = await fetch("http://jira-bus/jira_bus/v2/authorize", {
      method: "POST",
      body: JSON.stringify({
        url: req.originalUrl,
        method: "GET",
        jwt,
      }),
    });

    const { status: responseCode } = response;

    if (responseCode >= 400) {
      res.sendStatus(responseCode);
      return;
    }
    next();
  });
};

export default checkJwtForPageRoutesMiddleware;
