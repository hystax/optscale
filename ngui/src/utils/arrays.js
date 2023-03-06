import { removeKey, idx } from "./objects";

export const getLength = (array) => +Array.isArray(array) && array.length;

export const isEmpty = (array) => !(Array.isArray(array) && array.length);

export const getValuesByObjectKey = (array, key) => array.map((item) => item[key]);

export const getIntersection = (targetArray, searchArray) => targetArray.filter((item) => searchArray.includes(item));

export const getDifference = (targetArray, searchArray) => targetArray.filter((item) => !searchArray.includes(item));

export const getUniqueValuesFromObjectsByKey = (array, key) => [...new Set(array.map((item) => item[key]))];

export const hasIntersection = (targetArray, searchArray) => getIntersection(targetArray, searchArray).length !== 0;

export const isIdentical = (targetArray, searchArray) =>
  getIntersection(targetArray, searchArray).length === targetArray.length;

export const cloneWithObjects = (array) => array.map((item) => ({ ...item }));

export const cloneWithArrays = (array) => array.map((item) => [...item]);

export const removeObjects = (array, key, value) => array.filter((obj) => obj[key] !== value);

export const removeFromObjects = (array, key) => array.map((obj) => removeKey(obj, key));

export const getSumByObjectKey = (array, key) => array.reduce((sum, cur) => sum + (cur[key] || 0), 0);

export const checkEveryValueByKey = (array, key, value) => array.every((item) => item[key] === value);

export const getSumByNestedObjectKey = (array, key, nested) =>
  array.reduce((sum, obj) => {
    const x = parseFloat(obj[key]?.[nested]);
    if (Number.isNaN(x)) {
      const err = new Error();
      console.warn(`obj[key][nested] is not a number. 0 value will be used instead\n`, err.stack);
      return sum + 0;
    }
    return sum + x;
  }, 0);

export const sortObjects = ({ array, field, type = "desc", compareFunction }) => {
  const defaultCompareFunction = (valueOne, valueTwo) => {
    const testValueOne = Array.isArray(field) ? idx(field, valueOne) : valueOne[field];
    const testValueTwo = Array.isArray(field) ? idx(field, valueTwo) : valueTwo[field];
    if (testValueOne > testValueTwo) {
      return type === "desc" ? -1 : 1;
    }
    if (testValueOne < testValueTwo) {
      return type === "desc" ? 1 : -1;
    }
    return 0;
  };
  return [...array].sort(typeof compareFunction === "function" ? compareFunction : defaultCompareFunction);
};

export const sortObjectsAlphabetically = ({ array, field }) => {
  const compareFunction = (firstEl, secondEl) => firstEl[field].localeCompare(secondEl[field]);

  return sortObjects({ array, compareFunction });
};

/**
 * Recursive search for parents by child.
 *
 * @param {object} child - the object for which we are looking for parent
 * @param {array} sourceArray - list all objects to find the parent
 * @param {string} resultByKey - the key is to get the data from the right object if it is not, return the object itself
 * @returns {array} - array of objects(if there is a resultByKey, then other data)
 *
 */
export const getRecursiveParent = (child, sourceArray, resultByKey) => {
  if (child.parent_id) {
    const parent = sourceArray.find((el) => child.parent_id === el.id);
    if (parent) {
      const result = getRecursiveParent(parent, sourceArray, resultByKey);
      result.push(resultByKey ? parent[resultByKey] : parent);
      return result;
    }
  }
  return [];
};

/**
 * Sort object on the array of object on the particular order
 *
 * @param {array} arrayOfObject
 * @param {array} order - array of values
 * @param {string} objectKey - key to get value to compare with element in the `order` array
 *
 * @returns Array of objects
 *
 * @example
 * const arrayOfObject = [
 *  { a: "1" }, { a: "2" }, { a: "3" }, { a: "4" }, { a: "5" }, { a: "6" }
 * ];
 *
 * setObjectOrder(arr, ["1", "4", "2", "456"], "a")
 * // [ { a: "1" }, { a: "4" }, { a: "2" }, { a: "3" }, { a: "5" }, { a: "6" } ]
 *
 */
export const setObjectsOrder = (arrayOfObject, order, objectKey) =>
  order.reverse().reduce((resultArray, value) => {
    const index = resultArray.findIndex((obj) => obj[objectKey] === value);

    if (index !== -1) {
      const { [index]: obj, ...restElements } = resultArray;

      return [obj, ...Object.values(restElements).map((object) => object)];
    }
    return resultArray;
  }, arrayOfObject);

// TODO - can use getChunks ???
export const splitIntoTwoChunks = (array, firstChunkLength) => [
  array.slice(0, firstChunkLength),
  array.slice(firstChunkLength, array.length)
];

export const splitIntoChunks = (array, chunkSize) =>
  Array(Math.ceil(array.length / chunkSize))
    .fill()
    .map((_, index) => index * chunkSize)
    .map((begin) => array.slice(begin, begin + chunkSize));

export const getChunks = (array, size) =>
  Array.from({ length: Math.ceil(array.length / size) }, (_v, i) => array.slice(i * size, i * size + size));

/**
 *
 * @param {Array} array - The collection to iterate over
 * @param {string|Function} iteratee - The iteratee to transform keys
 *
 * @description
 * Creates an object composed of keys generated from the results of running each element of collection thru iteratee.
 *
 * @example "String iteratee"
 * const arr = [ {name: 1}, {name: 2} ]
 * const res = createGroupsObjectFromArray(arr, "name")
 * res = { '1': [ { name: 1 } ], '2': [ { name: 2 } ] }
 *
 * @example "String iteratee"
 * const arr = [ {id: 1}, {name: 1}, {name: 2} ]
 * const res = createGroupsObjectFromArray(arr, "name")
 * res = {
 *  '1': [ { name: 1 } ],
 *  '2': [ { name: 2 } ],
 *  undefined: [ { id: 1 } ]
 * }
 *
 * @example "Function iteratee"
 * const arr = [ { pool: { name: "name1" }}, { pool: { name: "name2"}} ]
 * res = createGroupsObjectFromArray(arr, (x) => x.pool.name)
 * res = {
 *    name1: [ { pool: { name: 'name1' } } ],
 *    name2: [ { pool: { name: 'name2' } } ]
 * }
 */
export const createGroupsObjectFromArray = (array, iteratee) =>
  array.reduce((groups, currentObject) => {
    const key = typeof iteratee === "function" ? iteratee(currentObject) : currentObject[iteratee];
    const grs = groups;

    if (!grs[key]) {
      grs[key] = [];
    }
    grs[key].push(currentObject);

    return grs;
  }, {});

export const getFirstAndLastElements = (array) => (!isEmpty(array) ? [array[0], array[array.length - 1]] : []);

export const getElementsSum = (numbers) => numbers.reduce((sum, number) => sum + number, 0);

export const getArithmeticMean = (numbers) => {
  const numbersSum = getElementsSum(numbers);
  const numbersCount = numbers.length;

  return numbersSum / numbersCount;
};

export const getLastElement = (array) => array[array.length - 1];

export const isLastItem = (itemIndex, itemsCount) => itemIndex === itemsCount - 1;

export const findMaxNumber = (array) =>
  array.reduce((maxValue, currentValue) => Math.max(currentValue, maxValue), Number.MIN_VALUE);
