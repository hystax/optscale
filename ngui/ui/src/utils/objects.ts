export const isObject = (obj: unknown) => obj === Object(obj);

export const idx = (keys: string[], object: Record<string, unknown>, defaultValue: unknown = undefined) =>
  keys.reduce((obj: unknown, key: string): unknown => {
    if (obj && Object.prototype.hasOwnProperty.call(obj, key)) {
      return (obj as Record<string, unknown>)[key];
    }

    return defaultValue;
  }, object);

export const isEmpty = (object: Record<string, unknown>) => Object.keys(object).length === 0 && object.constructor === Object;

export const filterEmpty = (
  sourceObject: Record<string, unknown>,
  options: {
    allowEmptyString?: boolean;
  } = {}
): Record<string, unknown> => {
  const { allowEmptyString = false } = options;

  return Object.keys(sourceObject)
    .filter((key) => {
      if (sourceObject[key] === "" && allowEmptyString) {
        return true;
      }

      return sourceObject[key] || typeof sourceObject[key] === "boolean";
    })
    .reduce(
      (targetObject, key) => ({
        ...targetObject,
        [key]: sourceObject[key]
      }),
      {}
    );
};

export const removeKey = <T extends Record<string, unknown>, K extends keyof T>(object: T, key: K) => {
  const { [key]: removedKey, ...obj } = object;
  return obj;
};

/**
 * @example
 * const obj = { a: 1, b: 3, c: 2 };
 * const sortD = sortByValue(obj, "desc")
 * // sortD = { b: 3, c: 2, a: 1 }
 *
 * const sortA = sortByValue(obj, "asc")
 * // sortA = { a: 1, c: 2, b: 3 }
 */
export const sortByValue = <T extends number>(object: Record<string, T>, order: "asc" | "desc" = "asc"): Record<string, T> => {
  const ascSortFunction = (a: [string, T], b: [string, T]) => a[1] - b[1];
  const descSortFunction = (a: [string, T], b: [string, T]) => b[1] - a[1];

  const sortFunction = {
    desc: descSortFunction,
    asc: ascSortFunction
  }[order];

  return Object.fromEntries(Object.entries(object).sort(sortFunction));
};

export const toKeyValueString = (object: Record<string, unknown>, separator = ":", joinWith = ",") =>
  isEmpty(object)
    ? ""
    : Object.entries(object)
        .map(([key, value]) => `${key}${separator} ${value}`)
        .join(`${joinWith} `);

export const objectMap = <T extends Record<string, unknown>, V extends T[keyof T], K extends keyof T>(
  object: T,
  mapFunction: (value: V, key: K, index: number) => unknown
) => Object.fromEntries(Object.entries(object).map(([key, value], index) => [key, mapFunction(value as V, key as K, index)]));

export const removeUndefinedValues = (object: Record<string, unknown>) =>
  Object.fromEntries(Object.entries(object).filter(([, value]) => value !== undefined));
