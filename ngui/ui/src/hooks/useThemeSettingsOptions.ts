import { getUnit } from "@mui/material/styles/cssUtils";
import { isMedia } from "theme";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { isObject } from "utils/objects";
import { useOrganizationThemeSettings } from "./useOrganizationThemeSettings";

const validateObject = (obj, validator) => {
  if (!isObject(obj)) {
    return {};
  }
  return Object.fromEntries(Object.entries(obj).filter(([key, value]) => validator([key, value])));
};

const isAllowedFontUnit = (unit) => ["rem", "em", "px"].includes(unit);

const validateTypography = (variant) =>
  validateObject(variant, ([property, value]) => {
    const isMediaProperty = isMedia(property);

    const isAllowedProperty = ["fontFamily", "fontSize", "fontWeight", "lineHeight"].includes(property) || isMediaProperty;
    if (!isAllowedProperty) {
      return false;
    }

    if (["fontSize"].includes(property) || isMediaProperty) {
      const unit = getUnit(isMediaProperty ? value.fontSize : value);
      if (!isAllowedFontUnit(unit)) {
        return false;
      }
    }

    if (["fontWeight", "lineHeight"].includes(property)) {
      if (Number.isNaN(parseFloat(value))) {
        return false;
      }
    }

    return true;
  });

const useTypographySettings = () => {
  const { typography = {} } = useOrganizationThemeSettings();

  const {
    body1 = {},
    body2 = {},
    subtitle1 = {},
    subtitle2 = {},
    h1 = {},
    h2 = {},
    h3 = {},
    h4 = {},
    h5 = {},
    h6 = {}
  } = typography;

  const typographyVariantSettings = {
    body1: validateTypography(body1),
    body2: validateTypography(body2),
    subtitle1: validateTypography(subtitle1),
    subtitle2: validateTypography(subtitle2),
    h1: validateTypography(h1),
    h2: validateTypography(h2),
    h3: validateTypography(h3),
    h4: validateTypography(h4),
    h5: validateTypography(h5),
    h6: validateTypography(h6)
  };

  return typographyVariantSettings;
};

const validateColorValue = (color) => {
  // "#000000"
  if (color.startsWith("#")) {
    return color;
  }

  // 'rgb()', 'rgba()', 'hsl()', 'hsla()'
  const marker = color.indexOf("(");
  const type = color.substring(0, marker);

  if (["rgb", "rgba", "hsl", "hsla", "color"].includes(type)) {
    return color;
  }

  return false;
};

const validateCommonPaletteColors = (color) =>
  validateObject(
    color,
    ([colorType, colorValue]) => ["main", "light", "dark", "contrastText"].includes(colorType) && validateColorValue(colorValue)
  );

const validateTextPaletteColors = (color) =>
  validateObject(
    color,
    ([colorType, colorValue]) => ["disabled", "primary", "secondary"].includes(colorType) && validateColorValue(colorValue)
  );

const usePaletteSettings = () => {
  const { palette = {} } = useOrganizationThemeSettings();
  const { text = {}, primary = {}, secondary = {}, info = {}, warning = {}, error = {}, success = {} } = palette;

  const paletteSettings = {
    text: validateTextPaletteColors(text),
    primary: validateCommonPaletteColors(primary),
    secondary: validateCommonPaletteColors(secondary),
    info: validateCommonPaletteColors(info),
    warning: validateCommonPaletteColors(warning),
    error: validateCommonPaletteColors(error),
    success: validateCommonPaletteColors(success)
  };

  return paletteSettings;
};

const useChartPaletteSettings = () => {
  const { chartPalette = {} } = useOrganizationThemeSettings();
  const { chart = [], monoChart = [] } = chartPalette;

  const chartPaletteSettings = Object.fromEntries(
    [
      ["chart", chart],
      ["monoChart", monoChart]
    ].map(([name, colors]) => [
      name,
      Array.isArray(colors) && !isEmptyArray(colors) && colors.every(validateColorValue) ? colors : []
    ])
  );

  return chartPaletteSettings;
};

export const useThemeSettingsOptions = () => {
  const typographySettings = useTypographySettings();
  const paletteSettings = usePaletteSettings();
  const chartPaletteSettings = useChartPaletteSettings();

  return {
    typography: typographySettings,
    palette: paletteSettings,
    chartPalette: chartPaletteSettings
  };
};
