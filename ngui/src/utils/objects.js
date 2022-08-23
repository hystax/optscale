export const isObject = (obj) => obj === Object(obj);

export const idx = (keys, object, defaultValue = undefined) =>
  keys.reduce((obj, key) => (obj && Object.prototype.hasOwnProperty.call(obj, key) ? obj[key] : defaultValue), object);

export const isEmpty = (object) => Object.keys(object).length === 0 && object.constructor === Object;

export const filterEmpty = (sourceObject) =>
  Object.keys(sourceObject)
    .filter((key) => sourceObject[key] || typeof sourceObject[key] === "boolean")
    .reduce(
      (targetObject, key) => ({
        ...targetObject,
        [key]: sourceObject[key]
      }),
      {}
    );

export const removeKey = (object, key) => {
  const { [key]: removedKey, ...obj } = object;
  return obj;
};

/**
 *
 * @param {Object} object - object to sort
 * @param {"desc"|"DESC"|"asc"|"ASC"} order - sorting order
 *
 * @example
 * const obj = { a: 1, b: 3, c: 2 };
 * const sortD = sortByValue(obj, "desc")
 * // sortD = { b: 3, c: 2, a: 1 }
 *
 * const sortA = sortByValue(obj, "asc")
 * // sortA = { a: 1, c: 2, b: 3 }
 *
 * @returns {object}
 */
export const sortByValue = (object, order = "asc") => {
  if (!["asc", "desc"].includes(order.toLowerCase())) {
    throw new Error("Incorrect 'order' value");
  }

  const ascSortFunction = (a, b) => a[1] - b[1];
  const descSortFunction = (a, b) => b[1] - a[1];

  const sortFunction = {
    desc: descSortFunction,
    asc: ascSortFunction
  }[order.toLowerCase()];

  return Object.fromEntries(Object.entries(object).sort(sortFunction));
};

export const toKeyValueString = (object, separator = ":", joinWith = ",") =>
  isEmpty(object)
    ? ""
    : Object.entries(object)
        .map(([key, value]) => `${key}${separator} ${value}`)
        .join(`${joinWith} `);

export const objectMap = (object, mapFunction) =>
  Object.fromEntries(Object.entries(object).map(([key, value], index) => [key, mapFunction(value, key, index)]));
