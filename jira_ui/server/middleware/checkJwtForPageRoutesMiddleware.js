import https from "https";
import fetch from "node-fetch";

const pagePathPattern = /\/jira_ui\/(configure|issue_left_panel)/;

const checkJwtForPageRoutesMiddleware = (app) => {
  app.use(pagePathPattern, async (req, res, next) => {
    const { jwt } = req.query;

    const httpsAgent = new https.Agent({
      rejectUnauthorized: false,
    });

    const response = await fetch(
      "https://ngingress-nginx-ingress-controller:443/jira_bus/v2/authorize",
      {
        method: "POST",
        agent: httpsAgent,
        body: JSON.stringify({
          url: req.originalUrl,
          method: "GET",
          jwt,
        }),
      }
    );

    const { status: responseCode } = response;

    if (responseCode >= 400) {
      res.sendStatus(responseCode);
      return;
    }
    next();
  });
};

export default checkJwtForPageRoutesMiddleware;
