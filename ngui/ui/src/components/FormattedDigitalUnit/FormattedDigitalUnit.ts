import { intl } from "translations/react-intl-config";
import { getLastElement } from "utils/arrays";

export const IEC_UNITS = Object.freeze({
  BYTE: "iec_byte",
  KIBIBYTE: "kibibyte",
  MEBIBYTE: "mebibyte",
  GIBIBYTE: "gibibyte",
  TEBIBYTE: "tebibyte",
  PEBIBYTE: "pebibyte"
});

export const SI_UNITS = Object.freeze({
  BYTE: "si_byte",
  KILOBYTE: "kilobyte",
  MEGABYTE: "megabyte",
  GIGABYTE: "gigabyte",
  TERABYTE: "terabyte",
  PETABYTE: "petabyte"
});

const IEC_SYSTEM_OF_UNITS = Object.freeze({
  BASE: 1024,
  UNITS: Object.values(IEC_UNITS)
});

const SI_SYSTEM_OF_UNITS = Object.freeze({
  BASE: 1000,
  UNITS: Object.values(SI_UNITS)
});

const getSystemOfUnits = (unitName) => [IEC_SYSTEM_OF_UNITS, SI_SYSTEM_OF_UNITS].find(({ UNITS }) => UNITS.includes(unitName));

const getConvertedValueAndRelativeNextUnitIndex = (value, base) => {
  const relativeNextUnitIndex = Math.floor(Math.log(value) / Math.log(base));
  const convertedValue = parseFloat(value / base ** relativeNextUnitIndex);

  return [convertedValue, relativeNextUnitIndex];
};

export const getConvertedValueAndUnitName = (value, baseUnit = SI_UNITS.BYTE) => {
  const { BASE, UNITS } = getSystemOfUnits(baseUnit);

  const isLastUnit = () => baseUnit === getLastElement(UNITS);

  if (value < BASE || isLastUnit(baseUnit)) {
    return [value, baseUnit];
  }

  const [convertedValue, relativeNextUnitIndex] = getConvertedValueAndRelativeNextUnitIndex(value, BASE);

  const baseUnitIndex = UNITS.indexOf(baseUnit);
  const transformedValueUnit = UNITS[baseUnitIndex + relativeNextUnitIndex];

  return [convertedValue, transformedValueUnit];
};

const APPROXIMATE_ZERO_THRESHOLD = 0.01;

export const formatDigitalUnit = ({ value, baseUnit = SI_UNITS.BYTE, maximumFractionDigits }) => {
  const [convertedValue, unitName] = getConvertedValueAndUnitName(value, baseUnit);

  const formattedNumber =
    convertedValue !== 0 && convertedValue < APPROXIMATE_ZERO_THRESHOLD
      ? "≈0"
      : intl.formatNumber(convertedValue, { maximumFractionDigits });

  const formattedUnit = intl.formatMessage({ id: "digitalUnits" }, { unit: unitName });

  return `${formattedNumber} ${formattedUnit}`;
};

const FormattedDigitalUnit = ({ value, baseUnit = SI_UNITS.BYTE, maximumFractionDigits }) =>
  formatDigitalUnit({ value, baseUnit, maximumFractionDigits });

export default FormattedDigitalUnit;
