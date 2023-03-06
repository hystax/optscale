import React from "react";
import { capitalize } from "@mui/material";
import Grid from "@mui/material/Grid";
import { useTheme } from "@mui/material/styles";
import WrapperCard from "components/WrapperCard";
import { KINDS } from "stories";

export default {
  title: `${KINDS.MARKETING}/Palette`
};

const ColorCard = ({ colorName, colorDefinition }) => {
  const theme = useTheme();
  const {
    palette: { getContrastText }
  } = theme;

  return (
    <WrapperCard title={colorName}>
      <div
        style={{
          width: "300px",
          border: "1px solid black",
          padding: "4px"
        }}
      >
        {Object.entries(colorDefinition).map(([variant, value]) => (
          <div
            key={variant}
            style={{
              backgroundColor: value,
              color: getContrastText(value),
              padding: "15px"
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between"
              }}
            >
              <span>{variant}</span>
              <span>{value}</span>
            </div>
          </div>
        ))}
      </div>
    </WrapperCard>
  );
};

const Palette = ({ colorsDefinition }) => (
  <Grid container spacing={3}>
    {Object.entries(colorsDefinition).map(([colorName, colorDefinition]) => (
      <Grid key={colorName} item>
        <ColorCard colorName={capitalize(colorName)} colorDefinition={colorDefinition} />
      </Grid>
    ))}
  </Grid>
);

export const basicPalette = () => {
  const theme = useTheme();
  return <Palette colorsDefinition={theme.palette} />;
};

const AdditionalColorsPalette = () => {
  const theme = useTheme();

  const {
    palette: { action, divider }
  } = theme;

  return (
    <Palette
      colorsDefinition={{
        action: {
          active: action.active,
          disabled: action.disabled,
          disabledBackground: action.disabledBackground,
          focus: action.focus,
          hover: action.hover,
          selected: action.selected
        },
        divider: { divider }
      }}
    />
  );
};

export const additionalColorsPalette = () => <AdditionalColorsPalette />;

export const chartsPalette = () => {
  const theme = useTheme();

  return (
    <Palette
      colorsDefinition={{ "Chart Palette": theme.palette.chart, "Monochromatic Chart Palette": theme.palette.monoChart }}
    />
  );
};
