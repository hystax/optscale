import { type ReactNode } from "react";
import { ListSubheader } from "@mui/material";

type TitleProps = {
  children?: ReactNode;
};

const Title = ({ children }: TitleProps) => <ListSubheader>{children}</ListSubheader>;

// https://mui.com/material-ui/react-select/#grouping
Title.muiSkipListHighlight = true;

export default Title;
