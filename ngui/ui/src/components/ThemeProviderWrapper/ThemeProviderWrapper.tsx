import createCache from "@emotion/cache";
import { CacheProvider } from "@emotion/react";
import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider } from "@mui/material/styles";
import { TssCacheProvider } from "tss-react";
import { useThemeSettingsOptions } from "hooks/useThemeSettingsOptions";
import getTheme from "theme";

const muiCache = createCache({
  key: "mui",
  prepend: true
});

const tssCache = createCache({
  key: "tss"
});

const ThemeProviderWrapper = ({ children }) => {
  const themeSettings = useThemeSettingsOptions();

  const theme = getTheme(themeSettings);

  return (
    <CacheProvider value={muiCache}>
      <TssCacheProvider value={tssCache}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          {children}
        </ThemeProvider>
      </TssCacheProvider>
    </CacheProvider>
  );
};

export default ThemeProviderWrapper;
