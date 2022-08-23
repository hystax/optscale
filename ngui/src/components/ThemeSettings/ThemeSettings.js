import React from "react";
import { Grid } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import ChartPaletteSettingsForm from "components/ChartPaletteSettingsForm";
import PaletteSettingsForm from "components/PaletteSettingsForm";
import TabsWrapper from "components/TabsWrapper";
import TypographySettingsForm from "components/TypographySettingsForm";
import WrapperCard from "components/WrapperCard";
import OrganizationThemeSettingsContainer from "containers/OrganizationThemeSettingsContainer";

const TypographySettings = () => {
  const theme = useTheme();

  const variants = ["body1", "body2", "subtitle1", "subtitle2", "h1", "h2", "h3", "h4", "h5", "h6"];

  return (
    <Grid container spacing={2}>
      {variants.map((variant) => (
        <Grid item xs={12} sm={6} md={6} lg={4} key={variant}>
          <WrapperCard needAlign>
            <OrganizationThemeSettingsContainer>
              {(onUpdate) => (
                <TypographySettingsForm onUpdate={onUpdate} variant={variant} options={theme.typography[variant]} />
              )}
            </OrganizationThemeSettingsContainer>
          </WrapperCard>
        </Grid>
      ))}
    </Grid>
  );
};

const PaletteSettings = () => {
  const theme = useTheme();

  const colors = ["text", "primary", "secondary", "info", "warning", "error", "success"];

  return (
    <Grid container spacing={2}>
      {colors.map((color) => (
        <Grid item xs={12} sm={6} md={6} lg={4} key={color}>
          <WrapperCard needAlign>
            <OrganizationThemeSettingsContainer>
              {(onUpdate) => <PaletteSettingsForm onUpdate={onUpdate} color={color} options={theme.palette[color]} />}
            </OrganizationThemeSettingsContainer>
          </WrapperCard>
        </Grid>
      ))}
    </Grid>
  );
};

const ChartPaletteSettings = () => {
  const theme = useTheme();

  const chartPalettes = ["chart", "monoChart"];

  return (
    <Grid container spacing={2}>
      {chartPalettes.map((chartPalette) => (
        <Grid item xs={12} sm={6} md={6} lg={4} key={chartPalette}>
          <WrapperCard needAlign>
            <OrganizationThemeSettingsContainer>
              {(onUpdate) => (
                <ChartPaletteSettingsForm onUpdate={onUpdate} palette={chartPalette} options={theme.palette[chartPalette]} />
              )}
            </OrganizationThemeSettingsContainer>
          </WrapperCard>
        </Grid>
      ))}
    </Grid>
  );
};

const ThemeSettings = () => {
  const tabs = [
    {
      title: "typography",
      node: <TypographySettings />
    },
    {
      title: "palette",
      node: <PaletteSettings />
    },
    {
      title: "chartPalette",
      node: <ChartPaletteSettings />
    }
  ];

  return (
    <TabsWrapper
      withWrapperCard={false}
      tabsProps={{
        tabs,
        defaultTab: "typography",
        name: "theme-settings"
      }}
    />
  );
};

export default ThemeSettings;
