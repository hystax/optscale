import LanguageIcon from "@mui/icons-material/Language";
import Box from "@mui/material/Box";
import MuiMenuItem from "@mui/material/MenuItem";
import MuiSelect from "@mui/material/Select";
import { useLocaleContext } from "contexts/LocaleContext";
import { SUPPORTED_LOCALES } from "translations/localeManager";

const LanguageSwitcher = () => {
  const { locale, setLocale } = useLocaleContext();

  const handleChange = (event) => {
    setLocale(event.target.value);
  };

  return (
    <Box display="flex" alignItems="center">
      <LanguageIcon color="primary" sx={{ mr: 0.5, fontSize: "1.25rem" }} />
      <MuiSelect
        value={locale}
        onChange={handleChange}
        variant="standard"
        disableUnderline
        sx={{
          color: "primary.main",
          fontSize: "0.875rem",
          fontWeight: 500,
          "& .MuiSelect-select": {
            paddingTop: 0,
            paddingBottom: 0,
            paddingRight: "20px !important",
          },
          "& .MuiSvgIcon-root": {
            color: "primary.main",
            fontSize: "1.25rem",
          },
        }}
        data-test-id="select_language"
      >
        {Object.entries(SUPPORTED_LOCALES).map(([localeKey, label]) => (
          <MuiMenuItem key={localeKey} value={localeKey} data-test-id={`option_lang_${localeKey}`}>
            {label}
          </MuiMenuItem>
        ))}
      </MuiSelect>
    </Box>
  );
};

export default LanguageSwitcher;
