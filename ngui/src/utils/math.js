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

export const round = (value, precision) => {
  const multiplier = 10 ** (precision || 0);
  return Math.round(value * multiplier) / multiplier;
};
