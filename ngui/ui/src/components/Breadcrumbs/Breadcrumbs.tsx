import HorizontalRuleIcon from "@mui/icons-material/HorizontalRule";
import { Breadcrumbs as MuiBreadcrumbs } from "@mui/material";
import useStyles from "./Breadcrumbs.styles";

const Breadcrumbs = ({ children, withSlashAtTheEnd = false }) => {
  const { classes } = useStyles();

  return (
    <MuiBreadcrumbs
      classes={{
        separator: classes.separator
      }}
      separator={
        <HorizontalRuleIcon
          sx={{
            transform: "rotate(115deg)"
          }}
          color="info"
          fontSize="small"
        />
      }
    >
      {children}
      {withSlashAtTheEnd && <span />}
    </MuiBreadcrumbs>
  );
};

export default Breadcrumbs;
