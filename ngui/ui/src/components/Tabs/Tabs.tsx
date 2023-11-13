import MuiTabs from "@mui/material/Tabs";
import useStyles from "./Tabs.styles";

const Tabs = ({ children, variant = "scrollable", indicatorColor = "secondary", textColor = "primary", ...rest }) => {
  const { classes } = useStyles();

  const isScrollable = variant === "scrollable";

  return (
    <MuiTabs
      variant={variant}
      textColor={textColor}
      indicatorColor={indicatorColor}
      scrollButtons={isScrollable ?? "auto"}
      allowScrollButtonsMobile
      TabScrollButtonProps={{
        classes: {
          disabled: isScrollable ? classes.hiddenTabScrollButton : ""
        }
      }}
      {...rest}
    >
      {children}
    </MuiTabs>
  );
};

export default Tabs;
