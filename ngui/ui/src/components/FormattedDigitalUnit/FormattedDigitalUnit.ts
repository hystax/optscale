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

type IecUnitType = (typeof IEC_UNITS)[keyof typeof IEC_UNITS];

type SiUnitType = (typeof SI_UNITS)[keyof typeof SI_UNITS];

type UnitType = IecUnitType | SiUnitType;

type FormattedDigitalUnitProps = {
  value: number;
  baseUnit?: UnitType;
  maximumFractionDigits?: number;
};

const IEC_SYSTEM_OF_UNITS = Object.freeze({
  BASE: 1024,
  UNITS: Object.values(IEC_UNITS) as readonly IecUnitType[]
});

const SI_SYSTEM_OF_UNITS = Object.freeze({
  BASE: 1000,
  UNITS: Object.values(SI_UNITS) as readonly SiUnitType[]
});

const getSystemOfUnits = (unitName: UnitType) => {
  if (Object.values(IEC_UNITS).includes(unitName as IecUnitType)) {
    return IEC_SYSTEM_OF_UNITS;
  }

  if (Object.values(SI_UNITS).includes(unitName as SiUnitType)) {
    return SI_SYSTEM_OF_UNITS;
  }

  throw Error(`${unitName} is not supported`);
};

const getConvertedValueAndRelativeNextUnitIndex = (value: number, base: number) => {
  const relativeNextUnitIndex = Math.floor(Math.log(value) / Math.log(base));
  const convertedValue = parseFloat(String(value / base ** relativeNextUnitIndex));

  return [convertedValue, relativeNextUnitIndex] as const;
};

export const getConvertedValueAndUnitName = (
  value: FormattedDigitalUnitProps["value"],
  baseUnit: FormattedDigitalUnitProps["baseUnit"] = SI_UNITS.BYTE
) => {
  const { BASE, UNITS } = getSystemOfUnits(baseUnit);

  const isLastUnit = () => baseUnit === getLastElement(UNITS);

  if (value < BASE || isLastUnit()) {
    return [value, baseUnit] as const;
  }

  const [convertedValue, relativeNextUnitIndex] = getConvertedValueAndRelativeNextUnitIndex(value, BASE);

  const baseUnitIndex = (UNITS as string[]).indexOf(baseUnit);
  const transformedValueUnit = UNITS[baseUnitIndex + relativeNextUnitIndex];

  return [convertedValue, transformedValueUnit] as const;
};

const APPROXIMATE_ZERO_THRESHOLD = 0.01;

export const formatDigitalUnit = ({ value, baseUnit = SI_UNITS.BYTE, maximumFractionDigits }: FormattedDigitalUnitProps) => {
  const [convertedValue, unitName] = getConvertedValueAndUnitName(value, baseUnit);

  const formattedNumber =
    convertedValue !== 0 && convertedValue < APPROXIMATE_ZERO_THRESHOLD
      ? "≈0"
      : intl.formatNumber(convertedValue, { maximumFractionDigits });

  const formattedUnit = intl.formatMessage({ id: "digitalUnits" }, { unit: unitName });

  return `${formattedNumber} ${formattedUnit}`;
};

const FormattedDigitalUnit = ({ value, baseUnit = SI_UNITS.BYTE, maximumFractionDigits }: FormattedDigitalUnitProps) =>
  formatDigitalUnit({ value, baseUnit, maximumFractionDigits });

export default FormattedDigitalUnit;
