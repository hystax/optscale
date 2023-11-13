import Box from "@mui/material/Box";

const InfoRow = ({ title, icon, value }) => (
  <Box fontSize={15} display="flex" alignItems="center" mb={1}>
    {`${title}:`}
    <Box fontWeight="bold" ml={1} display="flex" alignItems="center">
      {icon}
      {value}
    </Box>
  </Box>
);

export default InfoRow;
