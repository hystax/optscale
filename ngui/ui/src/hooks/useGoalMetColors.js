import { useTheme } from "@mui/material/styles";

export const useGoalMetColors = () => {
  const theme = useTheme();

  return {
    goalMet: theme.palette.success.light,
    goalNotMet: theme.palette.warning.light
  };
};
