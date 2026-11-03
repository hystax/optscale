import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import { FormControl } from "@mui/material";
import Button from "components/Button";

type AddRowButtonProps = {
  messageId: string;
  onClick: () => void;
  dataTestId: string;
};

// Dashed full-width button that appends a row to a field array
const AddRowButton = ({ messageId, onClick, dataTestId }: AddRowButtonProps) => (
  <FormControl fullWidth>
    <Button
      dashedBorder
      startIcon={<AddOutlinedIcon />}
      messageId={messageId}
      size="small"
      color="primary"
      onClick={onClick}
      dataTestId={dataTestId}
    />
  </FormControl>
);

export default AddRowButton;
