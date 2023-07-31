import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  organizationSelector: {
    "&.MuiFormControl-root": {
      "& label": {
        color: theme.palette.primary.main
      },
      "& div": {
        color: theme.palette.primary.main,
        "&.Mui-focused": {
          "& fieldset": {
            borderColor: theme.palette.primary.main
          }
        }
      },
      "& svg": {
        color: theme.palette.primary.main
      },
      "& fieldset": {
        borderColor: theme.palette.primary.main
      },
      "&:hover fieldset": {
        borderColor: theme.palette.primary.main
      }
    }
  }
}));

export default useStyles;
