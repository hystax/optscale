import MuiSkeleton from "@mui/material/Skeleton";
import useStyles from "./Skeleton.styles";

const Skeleton = ({ children, fullWidth, ...rest }) => {
  const { classes } = useStyles();

  const skeletonClasses = fullWidth ? classes.fullWidth : "";

  return (
    <MuiSkeleton className={skeletonClasses} {...rest}>
      {children}
    </MuiSkeleton>
  );
};

export default Skeleton;
