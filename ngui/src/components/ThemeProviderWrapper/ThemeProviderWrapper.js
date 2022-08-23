import React from "react";
import createCache from "@emotion/cache";
import { CacheProvider } from "@emotion/react";
import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider } from "@mui/material/styles";
import PropTypes from "prop-types";
import { useThemeSettingsOptions } from "hooks/useThemeSettingsOptions";
import getTheme from "theme";

const muiCache = createCache({
  key: "mui",
  prepend: true
});

const ThemeProviderWrapper = ({ children }) => {
  const themeSettings = useThemeSettingsOptions();

  const theme = getTheme(themeSettings);

  return (
    <CacheProvider value={muiCache}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </CacheProvider>
  );
};

ThemeProviderWrapper.propTypes = {
  children: PropTypes.node.isRequired
};

export default ThemeProviderWrapper;
