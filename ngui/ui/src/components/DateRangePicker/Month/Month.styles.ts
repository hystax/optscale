import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  root: {
    width: 290
  },
  weekDaysContainer: {
    marginTop: 10,
    paddingLeft: 30,
    paddingRight: 30
  },
  daysContainer: {
    marginTop: 15
  }
}));

export default useStyles;
