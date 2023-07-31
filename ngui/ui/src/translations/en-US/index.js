import app from "./app.json";
import currencies from "./currencies.json";
import error from "./errors.json";
import finops from "./finops.json";
import success from "./success.json";

export default { ...app, ...error, ...success, ...finops, ...currencies };
