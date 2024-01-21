import { rateLimit } from "express-rate-limit";

const MS_MINUTE = 60000;

const MAX_REQUESTS = 500;

const rateLimitMiddleware = (app) => {
  app.use(
    rateLimit({
      windowMs: 15 * MS_MINUTE,
      max: MAX_REQUESTS,
    })
  );
};

export default rateLimitMiddleware;
