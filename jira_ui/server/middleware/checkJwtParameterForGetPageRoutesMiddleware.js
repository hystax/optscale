import isValidJwt from "../utils/isValidJwt.js";

const pagePathPattern = /\/jira_ui\/(configure|issue_left_panel)/;

const checkJwtParameterForGetPageRoutesMiddleware = (app) => {
  app.use(pagePathPattern, (req, res, next) => {
    const { jwt } = req.query;

    if (!isValidJwt(jwt)) {
      res.sendStatus(401);
      return;
    }

    next();
  });
};

export default checkJwtParameterForGetPageRoutesMiddleware;
