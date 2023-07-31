import { createIntl, createIntlCache } from "react-intl";
import localeManager from "./localeManager";

// https://formatjs.io/docs/react-intl/api/#createintl
const cache = createIntlCache(); // This is optional but highly recommended since it prevents memory leak
export const intl = createIntl(localeManager.getConfig(), cache);

export default localeManager.getConfig();
