import Ajv from "ajv";
import { perspectiveSchema } from "schemas";
import { intl } from "translations/react-intl-config";
import { COST_MODEL_MONEY_MAXIMUM_FRACTION_DIGITS } from "./constants";
import { isWhitespaceString } from "./strings";

export const isNumber = (value) => typeof value === "number" && !Number.isNaN(Number(value));

export const isPositiveNumberOrZero = (number) => !Number.isNaN(number) && number >= 0;

export const isWholeNumber = (value) => value % 1 !== 0 || value < 0;

export const isNumberInRange = (value, from, to) => from <= value && value <= to;

export const getMaxLengthValidationDefinition = (inputName, maxLength) => ({
  value: maxLength,
  message: intl.formatMessage({ id: "maxLength" }, { inputName: intl.formatMessage({ id: inputName }), max: maxLength })
});

export const costModelValueMaxFractionDigitsValidation = (value) => {
  const [, fractionDigits = ""] = value.split(".");
  return fractionDigits.length > COST_MODEL_MONEY_MAXIMUM_FRACTION_DIGITS
    ? intl.formatMessage({ id: "maxFractionDigits" }, { max: COST_MODEL_MONEY_MAXIMUM_FRACTION_DIGITS })
    : true;
};

export const positiveInteger = (value) => {
  const valueAsNumber = Number(value);
  return Number.isInteger(valueAsNumber) && valueAsNumber > 0 ? true : intl.formatMessage({ id: "positiveInteger" });
};

export const positiveIntegerOrZero = (value) => {
  const valueAsNumber = Number(value);
  return Number.isInteger(valueAsNumber) && valueAsNumber >= 0 ? true : intl.formatMessage({ id: "positiveIntegerOrZero" });
};

export const positiveNumber = (value) =>
  !Number.isNaN(value) && value > 0 ? true : intl.formatMessage({ id: "positiveNumber" });

export const notOnlyWhiteSpaces = (value) =>
  !isWhitespaceString(value) ? true : intl.formatMessage({ id: "notOnlyWhitespaces" });

export const lessOrEqual = (threshold) => (value) =>
  value <= threshold ? true : intl.formatMessage({ id: "lessOrEqual" }, { max: threshold });

export const validJson = (value) => {
  try {
    JSON.parse(value);
    return true;
  } catch {
    return "invalidJsonFile";
  }
};

export const validateSchema = (data, schema, options = {}) => {
  const ajv = new Ajv(options);
  const validate = ajv.compile(schema);
  const isValid = validate(data);

  return [isValid, validate.errors];
};

export const validatePerspectiveSchema = (data, options = {}) => validateSchema(data, perspectiveSchema, options);

export const isRunsetTemplateEnvironmentVariable = (inputName) => (value) =>
  /^[A-Z0-9_]+$/.test(value)
    ? true
    : intl.formatMessage(
        {
          id: "inputMustContainOnlyUppercaseLatinLettersNumberOrUnderscore"
        },
        {
          inputName
        }
      );

export const doNotBeginWithNumber = (inputName) => (value) =>
  /^[^0-9]/.test(value) ? true : intl.formatMessage({ id: "inputMustNotBeginWithNumbers" }, { inputName });
