import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  card: {
    width: "20rem"
  },
  cardContent: {
    overflow: "hidden",
    padding: 0,
    "&:last-child": {
      paddingBottom: 0
    }
  }
}));

export default useStyles;
