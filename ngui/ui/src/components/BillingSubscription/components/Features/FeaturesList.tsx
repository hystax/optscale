import { styled } from "@mui/material/styles";

const FeaturesList = styled("ul")(({ theme }) => ({
  margin: 0,
  paddingInlineStart: theme.spacing(2),
  listStyleType: "'-  '",
  "& > li + li": {
    marginTop: theme.spacing(0.5),
  },
}));

export default FeaturesList;
