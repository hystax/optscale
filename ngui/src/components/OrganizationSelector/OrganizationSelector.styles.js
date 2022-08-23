import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  organizationSelector: {
    "&.MuiFormControl-root": {
      "& label": {
        color: theme.palette.primary.contrastText
      },
      "& div": {
        color: theme.palette.primary.contrastText,
        "&.Mui-focused": {
          "& fieldset": {
            borderColor: theme.palette.primary.contrastText
          }
        }
      },
      "& svg": {
        color: theme.palette.primary.contrastText
      },
      "& fieldset": {
        borderColor: theme.palette.primary.contrastText
      },
      "&:hover fieldset": {
        borderColor: theme.palette.primary.contrastText
      }
    }
  }
}));

export default useStyles;
