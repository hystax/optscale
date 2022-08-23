import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  chip: {
    maxWidth: "100%"
  },
  defaultInfo: {
    color: theme.palette.info.contrastText,
    backgroundColor: theme.palette.info.main,
    "& .MuiChip-deleteIcon": {
      color: theme.palette.info.contrastText
    }
  },
  outlinedInfo: {
    border: `1px solid ${theme.palette.info.main}`,
    backgroundColor: "transparent"
  },
  defaultSuccess: {
    color: theme.palette.success.contrastText,
    backgroundColor: theme.palette.success.main,
    "& .MuiChip-deleteIcon": {
      color: theme.palette.success.contrastText
    }
  },
  outlinedSuccess: {
    border: `1px solid ${theme.palette.success.main}`,
    color: theme.palette.success.main,
    backgroundColor: "transparent"
  },
  defaultError: {
    color: theme.palette.error.contrastText,
    backgroundColor: theme.palette.error.main,
    "& .MuiChip-deleteIcon": {
      color: theme.palette.error.contrastText
    }
  },
  outlinedError: {
    border: `1px solid ${theme.palette.error.main}`,
    color: theme.palette.error.main,
    backgroundColor: "transparent"
  },
  defaultWarning: {
    color: theme.palette.warning.contrastText,
    backgroundColor: theme.palette.warning.main,
    "& .MuiChip-deleteIcon": {
      color: theme.palette.warning.contrastText
    }
  },
  outlinedWarning: {
    border: `1px solid ${theme.palette.warning.main}`,
    color: theme.palette.warning.main,
    backgroundColor: "transparent"
  },
  defaultPrimary: {
    color: theme.palette.primary.contrastText,
    backgroundColor: theme.palette.primary.main,
    "& .MuiChip-deleteIcon": {
      color: theme.palette.primary.contrastText
    }
  },
  outlinedPrimary: {
    border: `1px solid ${theme.palette.primary.main}`,
    color: theme.palette.primary.main,
    backgroundColor: "transparent"
  },
  uppercase: {
    textTransform: "uppercase"
  }
}));

export default useStyles;
