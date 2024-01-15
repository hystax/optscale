import isValidJwt from "../utils/isValidJwt.js";

const PAGE_ROUTES = Object.freeze(
  "/jira_ui/configure",
  "/jira_ui/issue_left_panel"
);

const checkJwtParameterForGetPageRoutesMiddleware = (app) => {
  app.use(PAGE_ROUTES, (req, res, next) => {
    const { jwt } = req.query;

    if (!isValidJwt(jwt)) {
      res.sendStatus(401);
      return;
    }

    next();
  });
};

export default checkJwtParameterForGetPageRoutesMiddleware;
