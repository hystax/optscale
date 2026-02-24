import { Alert } from "@mui/material";
import { StatusAlertProps } from "../types";

const StatusAlert = ({ children, color }: StatusAlertProps) => (
  <Alert
    icon={false}
    sx={{
      borderRadius: 0,
      paddingTop: 0,
      paddingBottom: 0,
      backgroundColor: (theme) => theme.palette[color].main,
      color: (theme) => theme.palette[color].contrastText,
      "& .MuiAlert-message": {
        width: "100%",
      },
    }}
  >
    {children}
  </Alert>
);

export default StatusAlert;
