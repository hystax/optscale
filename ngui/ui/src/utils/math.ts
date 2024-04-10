// TODO - revisit these utils and make calculation more precise. For example, 99.5 and above will be rounded to 100 which does not work for us in some cases.
export const getPercentageChangeModule = (newValue, oldValue) => Math.abs(100 - (newValue / oldValue) * 100);

export const getPercentageChange = (value1, value2) => {
  const result = 100 - (value1 / value2) * 100;

  // This check includes NaN and Infinity
  if (!Number.isFinite(result)) {
    return 0;
  }

  return result;
};

export const percentXofY = (x, y) => {
  if (x < 0 || y < 0) {
    console.warn("x or y is negative");
    return 0;
  }
  if (x === 0 && y === 0) {
    return 0;
  }
  return Number.parseFloat((x / y).toFixed(2));
};

export const intPercentXofY = (x, y) => parseFloat((percentXofY(x, y) * 100).toFixed());

export const round = (value, precision = 0) => {
  const multiplier = 10 ** precision;
  return Math.round((value + Number.EPSILON) * multiplier) / multiplier;
};

export const normalize = (value, domain, range) => {
  const [min, max] = domain;
  const [rangeStart = 0, rangeEnd = 1] = range;

  const normalized = (value - min) / (max - min);

  const scaled = normalized * (rangeEnd - rangeStart) + rangeStart;

  return scaled;
};

export const denormalize = (normalizedValue, domain, range) => {
  const [min, max] = domain;
  const [rangeStart = 0, rangeEnd = 1] = range;

  const ratio = (normalizedValue - rangeStart) / (rangeEnd - rangeStart);

  const denormalized = ratio * (max - min) + min;

  return denormalized;
};

export const isEven = (value: number) => value % 2 === 0;
