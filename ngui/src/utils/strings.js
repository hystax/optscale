export const emailRegex = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i;

export const notWhitespaceRegex = /\S/;

/**
 * any amount of spaces (>=0) + , or ; or whitespace + any amout of spaces (>=0)
 */
const emailsListSeparatorRegex = /\s*(?:,|;|\s)\s*/;

export const splitInvites = (emails) => emails.split(emailsListSeparatorRegex).filter(Boolean);

export const isString = (s) => typeof s === "string" || s instanceof String;

export const getInitialsFromName = (initials) => {
  if (!isString(initials)) {
    return "";
  }
  return initials
    .split(" ")
    .map((str) => str.charAt(0).toUpperCase())
    .join("");
};

export const isEllipsisActive = (e) => {
  const c = e.current;
  return c ? c.offsetHeight < c.scrollHeight || c.offsetWidth < c.scrollWidth : false;
};

export const getSubstring = (substring, regex, modifier = "g") => {
  const re = new RegExp(regex, modifier);
  return substring.match(re);
};

export const getHash = (s) => {
  let h;
  for (let i = 0; i < s.length; i += 1) h = (Math.imul(31, h) + s.charCodeAt(i)) | 0;
  return h;
};

export const capitalize = (s) => (isString(s) ? s.charAt(0).toUpperCase() + s.slice(1) : "");

export const concatenate = (array, pre, separator) => {
  const string = array.join(separator);
  return `${pre}${string}`;
};

export const concatenateUrl = (array, pre = "/", separator = "/") => concatenate(array, pre, separator);

export const sliceByLimitWithEllipsis = (str = "", limit) => (str.length <= limit ? str : `${str.slice(0, limit)}...`);
export const sliceFromEndByLimitWithEllipsis = (str = "", limit) => (str.length <= limit ? str : `...${str.slice(-limit)}`);

export const isValidEmail = (email) => emailRegex.test(email);

/**
 * Formats inputs to "[size][format] [family]" string
 * @param {number} size - font size
 * @param {string} family - font family
 * @param {string} [format=rem] - px/rem
 *
 * @returns {string} Formatted string
 */
export const getFontString = (size, family, format = "rem") => `${size}${format} ${family}`;

export const isWhitespaceString = (string) => /^\s+$/.test(string);

export const splitAndTrim = (rawString, separator = ",") => rawString?.split(separator).map((s) => s.trim()) || [];

export const buildQueryParameters = (base, parameters) =>
  `${base}${concatenateUrl(
    parameters.filter((el) => el !== ""),
    "?",
    "&"
  )}`;

export const parseJSON = (jsonString, fallback = {}) => {
  try {
    return JSON.parse(jsonString);
  } catch {
    return fallback;
  }
};

export const booleanStringToBoolean = (string) =>
  ({
    true: true,
    false: false
  }[string.toLowerCase()] ?? string);

export const hasSymbolAtTheEnd = (variable, symbol) => (isString(variable) ? variable.slice(-1) === symbol : false);
