import { rateLimit } from "express-rate-limit";

const MS_MINUTE = 60000;

const MAX_REQUESTS = 500;

export default rateLimit({
  windowMs: 15 * MS_MINUTE,
  max: MAX_REQUESTS,
});
