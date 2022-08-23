import { responsiveFontSizes } from "@mui/material/styles";
import { isEmpty as isEmptyObject } from "./objects";

export const MAP_MARKER_FONT_SIZE_IN_PX = 11;

/**
 * Converts rem to px
 *
 * @param { number } rem - rem
 *
 * @see https://material-ui.com/customization/typography/#html-font-size
 *
 * @returns px
 */

// TODO - rewrite this.
// 1. We need a dynamic value
// 2. htmlFontSize cannot be used here - it is inversely proportional to font size
// https://datatrendstech.atlassian.net/browse/NGUI-1587
export const remToPx = (rem) => {
  const coefficient = 16;
  return rem * coefficient;
};

const applyTypographySettings = (themeInput, settings) => {
  const theme = { ...themeInput };

  const isEmptySetting = (name) => isEmptyObject(settings.typography?.[name] ?? {});

  const mergeIfSettingIsNotEmpty = (target, settingName) => ({
    ...target,
    ...(isEmptySetting(settingName) ? {} : settings.typography[settingName])
  });

  theme.typography.body1 = mergeIfSettingIsNotEmpty(theme.typography.body1, "body1");
  theme.typography.body2 = mergeIfSettingIsNotEmpty(theme.typography.body2, "body2");
  theme.typography.subtitle1 = mergeIfSettingIsNotEmpty(theme.typography.subtitle1, "subtitle1");
  theme.typography.subtitle2 = mergeIfSettingIsNotEmpty(theme.typography.subtitle2, "subtitle2");
  theme.typography.h1 = mergeIfSettingIsNotEmpty(theme.typography.h1, "h1");
  theme.typography.h2 = mergeIfSettingIsNotEmpty(theme.typography.h2, "h2");
  theme.typography.h3 = mergeIfSettingIsNotEmpty(theme.typography.h3, "h3");
  theme.typography.h4 = mergeIfSettingIsNotEmpty(theme.typography.h4, "h4");
  theme.typography.h5 = mergeIfSettingIsNotEmpty(theme.typography.h5, "h5");
  theme.typography.h6 = mergeIfSettingIsNotEmpty(theme.typography.h6, "h6");

  return theme;
};

const generateResponsiveFontSizes = (themeInput) => {
  const theme = responsiveFontSizes(themeInput, {
    breakpoints: ["xs", "sm", "md", "lg", "xl"],
    variants: ["h1", "h2", "h3", "h4", "h5", "h6"]
  });

  const getUpBreakpoint = (breakpoint) => theme.breakpoints.up(breakpoint);

  const upXsBreakpoint = getUpBreakpoint("xs");
  const upLgBreakpoint = getUpBreakpoint("lg");
  const upXlBreakpoint = getUpBreakpoint("xl");

  theme.typography.subtitle1 = {
    ...theme.typography.subtitle1,
    [upXsBreakpoint]: {
      fontSize: "0.85rem"
    },
    [upLgBreakpoint]: {
      fontSize: "0.92rem"
    },
    [upXlBreakpoint]: {
      fontSize: "1rem"
    }
  };

  theme.typography.subtitle2 = {
    ...theme.typography.subtitle2,
    [upXsBreakpoint]: {
      fontSize: "0.75rem"
    },
    [upLgBreakpoint]: {
      fontSize: "0.8125rem"
    },
    [upXlBreakpoint]: {
      fontSize: "0.875rem"
    }
  };

  theme.typography.body1 = {
    ...theme.typography.body1,
    [upXsBreakpoint]: {
      fontSize: "0.85rem"
    },
    [upLgBreakpoint]: {
      fontSize: "0.92rem"
    },
    [upXlBreakpoint]: {
      fontSize: "1rem"
    }
  };

  theme.typography.body2 = {
    ...theme.typography.body2,
    [upXsBreakpoint]: {
      fontSize: "0.75rem"
    },
    [upLgBreakpoint]: {
      fontSize: "0.8125rem"
    },
    [upXlBreakpoint]: {
      fontSize: "0.875rem"
    }
  };

  return theme;
};

export const customResponsiveFontSizes = (themeInput, settings) =>
  applyTypographySettings(generateResponsiveFontSizes(themeInput), settings);
