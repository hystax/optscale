// Hystax palette: https://cdn.hystax.com/Hystax/Hystax-Guideline-2020.pdf
// Material design color tool: https://material.io/resources/color/

import { common } from "@mui/material/colors";
import { createTheme, alpha, darken, lighten } from "@mui/material/styles";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { customResponsiveFontSizes } from "utils/fonts";
import { isEmpty as isEmptyObject } from "utils/objects";

const getLighten = (color, lightenAlpha = 0.2) => lighten(color, lightenAlpha);
const getDarken = (color, darkenAlpha = 0.3) => darken(color, darkenAlpha);

export const isMedia = (property) => property.startsWith("@media");

const applyPaletteSettings = (settings) => {
  const isEmptySetting = (name) => isEmptyObject(settings.palette?.[name] ?? {});

  const mergeIfSettingIsNotEmpty = (target, settingName) => ({
    ...target,
    ...(isEmptySetting(settingName) ? {} : settings.palette[settingName])
  });

  const primary = mergeIfSettingIsNotEmpty(
    {
      main: "#004C74"
    },
    "primary"
  );

  const info = mergeIfSettingIsNotEmpty(
    {
      main: "#5E6A7F",
      header: getLighten("#5E6A7F", 0.93)
    },
    "info"
  );

  const secondary = mergeIfSettingIsNotEmpty(
    {
      main: "#F58535",
      contrastText: getDarken(info.main, 0.8)
    },
    "secondary"
  );

  const success = mergeIfSettingIsNotEmpty(
    {
      main: "#007E00"
    },
    "success"
  );

  const error = mergeIfSettingIsNotEmpty(
    {
      main: "#B00020"
    },
    "error"
  );

  const warning = mergeIfSettingIsNotEmpty(
    {
      main: "#906B00"
    },
    "warning"
  );

  const text = mergeIfSettingIsNotEmpty(
    {
      primary: getDarken(info.main),
      secondary: primary.main
    },
    "text"
  );

  return {
    primary,
    secondary,
    info,
    success,
    error,
    warning,
    text
  };
};
const applyChartPaletteSettings = (settings) => {
  const isEmptySetting = (name) => isEmptyArray(settings.chartPalette?.[name] ?? []);

  const chart = isEmptySetting("chart")
    ? [
        "#4AB4EE",
        "#FFC348",
        "#30D5C8",
        "#9950B1",
        "#4A63EE",
        "#FF6648",
        "#30D575",
        "#B19950",
        "#834AEE",
        "#48E1FF",
        "#D53090",
        "#99B150"
      ]
    : settings.chartPalette.chart;

  const monoChart = isEmptySetting("monoChart") ? ["#4AB4EE"] : settings.chartPalette.monoChart;

  return {
    chart,
    monoChart
  };
};

const applyGoogleMapPaletteSettings = (basicColorsPalette) => [
  {
    elementType: "geometry",
    stylers: [
      {
        color: "#ffffff"
      }
    ]
  },
  {
    elementType: "labels.icon",
    stylers: [
      {
        visibility: "off"
      }
    ]
  },
  {
    elementType: "labels.text.fill",
    stylers: [
      {
        color: basicColorsPalette.info.main
      }
    ]
  },
  {
    elementType: "labels.text.stroke",
    stylers: [
      {
        visibility: "off"
      }
    ]
  },
  {
    featureType: "administrative",
    elementType: "geometry",
    stylers: [
      {
        visibility: "off"
      }
    ]
  },
  {
    featureType: "administrative.land_parcel",
    stylers: [
      {
        visibility: "off"
      }
    ]
  },
  {
    featureType: "administrative.neighborhood",
    stylers: [
      {
        visibility: "off"
      }
    ]
  },
  {
    featureType: "poi",
    stylers: [
      {
        visibility: "off"
      }
    ]
  },
  {
    featureType: "poi",
    elementType: "labels.text",
    stylers: [
      {
        visibility: "off"
      }
    ]
  },
  {
    featureType: "road",
    stylers: [
      {
        visibility: "off"
      }
    ]
  },
  {
    featureType: "transit",
    stylers: [
      {
        visibility: "off"
      }
    ]
  },
  {
    featureType: "water",
    elementType: "geometry",
    stylers: [
      {
        color: "#DEE1E5"
      }
    ]
  },
  {
    featureType: "water",
    elementType: "labels.text",
    stylers: [
      {
        visibility: "off"
      }
    ]
  }
];

export const getThemeSpacingCoefficient = (theme) => {
  const coefficient = theme.spacing(1).match(/[-]?[0-9]+\.?[0-9]*/g);

  if (coefficient !== null) {
    return Number(coefficient[0]);
  }

  return 0;
};

// Main theme config
const getThemeConfig = (settings = {}) => {
  const baseColorsPalette = applyPaletteSettings(settings);
  const { primary, secondary, info, success, error, warning, text } = baseColorsPalette;

  const { chart, monoChart } = applyChartPaletteSettings(settings);

  const googleMapPalette = applyGoogleMapPaletteSettings(baseColorsPalette);

  // Actions
  const ACTION_HOVER = getLighten(info.main, 0.9);
  const ACTION_ACTIVE = primary.main;
  const ACTION_SELECTED = secondary.main;

  // Misc
  const BACKGROUND = getLighten(info.main, 0.95);
  const SKELETON_COLOR = getLighten(info.main, 0.8);

  return Object.freeze({
    typography: {
      fontFamily: "'Ubuntu', sans-serif",
      mono: {
        fontFamily: "'Ubuntu Mono', monospace"
      }
    },
    components: {
      MuiAccordion: {
        styleOverrides: {
          root: {
            "&:before": {
              display: "none"
            }
          }
        }
      },
      MuiAccordionSummary: {
        styleOverrides: {
          content: {
            maxWidth: "100%",
            margin: 0,
            "&.Mui-expanded": {
              margin: 0
            }
          },
          root: {
            "&.Mui-expanded": {
              minHeight: "48px",
              color: secondary.contrastText,
              backgroundColor: ACTION_SELECTED
            }
          },
          expandIconWrapper: {
            "&.Mui-expanded": {
              color: secondary.contrastText
            }
          }
        }
      },
      MuiAutocomplete: {
        styleOverrides: {
          option: {
            "&.MuiAutocomplete-option": {
              color: secondary.contrastText,
              /* 
                When options are selected, Autocomplete does not add any Mui classes, 
                so we need to rely on the aria-selected element property instead.
              */
              "&[aria-selected='true']": {
                backgroundColor: ACTION_SELECTED,
                "&.Mui-focused": {
                  backgroundColor: ACTION_SELECTED
                }
              }
            }
          }
        }
      },
      MuiButton: {
        defaultProps: {
          size: "small",
          color: "info"
        },
        variants: [
          {
            props: { variant: "contained", color: "lightYellow" },
            style: ({ theme }) => ({
              color: theme.palette.lightYellow.contrastText,
              "&:hover": {
                backgroundColor: lighten(theme.palette.lightYellow.main, 0.08)
              }
            })
          },
          {
            props: { variant: "contained", color: "lightBlue" },
            style: ({ theme }) => ({
              color: theme.palette.lightBlue.contrastText,
              "&:hover": {
                backgroundColor: lighten(theme.palette.lightBlue.main, 0.08)
              }
            })
          },
          {
            props: { variant: "text", color: "info" },
            style: ({ theme }) => ({
              color: theme.palette.text.primary
            })
          }
        ]
      },
      MuiButtonGroup: {
        defaultProps: {
          color: "info"
        }
      },
      MuiCardHeader: {
        styleOverrides: {
          content: {
            overflow: "hidden"
          }
        }
      },
      MuiCheckbox: {
        defaultProps: {
          color: "secondary"
        },
        styleOverrides: {
          colorSecondary: {
            color: secondary.main
          }
        }
      },
      MuiCssBaseline: {
        styleOverrides: {
          "#root": { display: "flex", flexDirection: "column", minHeight: "100vh" }
        }
      },
      MuiDialogActions: {
        styleOverrides: {
          root: {
            justifyContent: "center"
          }
        }
      },
      MuiDialogTitle: {
        styleOverrides: {
          root: {
            textAlign: "center"
          }
        }
      },
      MuiFormControl: {
        defaultProps: {
          margin: "dense"
        }
      },
      MuiFormHelperText: {
        defaultProps: {
          margin: "dense"
        }
      },
      MuiIconButton: {
        defaultProps: {
          size: "small"
        },
        styleOverrides: {
          root: {
            marginLeft: 0,
            marginRight: 0,
            padding: 8,
            "&:hover": {
              backgroundColor: alpha(ACTION_HOVER, 0.5)
            }
          }
        }
      },
      MuiInputLabel: {
        defaultProps: {
          size: "small"
        }
      },
      MuiInputBase: {
        defaultProps: {
          size: "small"
        }
      },
      MuiLink: {
        defaultProps: {
          underline: "hover"
        },
        styleOverrides: {
          root: {
            fontWeight: "bold"
          }
        }
      },
      MuiSwitch: {
        defaultProps: {
          color: "secondary"
        }
      },
      MuiListItem: {
        defaultProps: {
          dense: true
        },
        styleOverrides: {
          dense: {
            paddingTop: "0.375rem",
            paddingBottom: "0.375rem"
          },
          root: {
            "&.Mui-selected": {
              color: secondary.contrastText
            },
            "&.Mui-focusVisible": {
              backgroundColor: getLighten(secondary.main),
              color: secondary.contrastText
            }
          }
        }
      },
      MuiListItemSecondaryAction: {
        styleOverrides: {
          root: {
            right: "0.2rem"
          }
        }
      },
      MuiMenuItem: {
        defaultProps: {
          dense: true
        },
        styleOverrides: {
          root: {
            // https://github.com/mui-org/material-ui/issues/29842
            "&.Mui-selected": {
              backgroundColor: ACTION_SELECTED,
              color: secondary.contrastText,
              "&.Mui-focusVisible": { background: ACTION_SELECTED },
              "&:hover": {
                backgroundColor: ACTION_SELECTED
              }
            }
          }
        }
      },
      MuiSkeleton: {
        styleOverrides: {
          root: {
            backgroundColor: SKELETON_COLOR
          }
        }
      },
      MuiStepLabel: {
        styleOverrides: {
          label: {
            color: text.primary
          },
          labelContainer: {
            color: text.primary
          }
        }
      },
      MuiTab: {
        styleOverrides: {
          root: {
            minHeight: "3rem"
          }
        }
      },
      MuiTable: {
        defaultProps: {
          size: "small"
        }
      },
      MuiTableSortLabel: {
        styleOverrides: {
          root: {
            "&:hover": {
              color: text.primary,
              "& svg": {
                color: primary.main
              }
            },
            "&.Mui-active": {
              color: primary.main
            }
          }
        }
      },
      MuiAlert: {
        styleOverrides: {
          action: {
            paddingTop: 0
          }
        }
      },
      MuiTabs: {
        styleOverrides: {
          root: {
            minHeight: "2rem"
          }
        }
      },
      MuiTextField: {
        defaultProps: {
          size: "small"
        }
      },
      MuiToolbar: {
        defaultProps: {
          variant: "dense"
        },
        styleOverrides: {
          dense: {
            paddingRight: 0
          }
        }
      },
      MuiTypography: {
        defaultProps: {
          variant: "body2"
        }
      },
      MuiUseMediaQuery: {
        defaultProps: {
          noSsr: true
        }
      }
    },
    palette: {
      action: {
        hover: ACTION_HOVER,
        active: ACTION_ACTIVE,
        selected: ACTION_SELECTED
      },
      primary,
      secondary,
      info,
      success,
      error,
      warning,
      common,
      background: {
        default: BACKGROUND
      },
      text,
      lightYellow: {
        main: "#FFC348"
      },
      lightBlue: {
        main: "#4AB4EE",
        contrastText: common.white
      },
      chart,
      monoChart,
      googleMap: googleMapPalette,
      json: {
        default: text.primary,
        error: error.main,
        background: BACKGROUND,
        background_warning: BACKGROUND,
        string: text.primary,
        number: text.primary,
        colon: text.primary,
        keys: text.primary,
        keys_whiteSpace: text.primary,
        primitive: text.primary
      }
    }
  });
};

const PDF_THEME = {
  fontSizes: {
    summaryBig: 20,
    summarySmall: 10,
    h1: 17,
    h2: 16,
    text: 12,
    footerNote: 10
  },
  colors: {
    // TODO: Make this color configurable, get PRIMARY (`getLighten(PRIMARY)`) from `theme`
    link: getLighten("#004C74")
  },
  logoWidth: 120
};

// TODO: applyChartPaletteSettings needs to be rewritten, adding one one chart palette affects multiple files,
// hard to support and maintain.
export const RI_SP_CHART_PALETTE = ["#9950B1", "#4AB4EE", "#FFC348", "#30D5C8"];

export default (settings = {}) => customResponsiveFontSizes(createTheme(getThemeConfig(settings)), settings);

export { PDF_THEME };
