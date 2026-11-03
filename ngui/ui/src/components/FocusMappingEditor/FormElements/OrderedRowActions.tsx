import ArrowDownwardOutlinedIcon from "@mui/icons-material/ArrowDownwardOutlined";
import ArrowUpwardOutlinedIcon from "@mui/icons-material/ArrowUpwardOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import { Box, FormControl } from "@mui/material";
import IconButton from "components/IconButton";
import { SPACING_5 } from "utils/layouts";

type OrderedRowActionsProps = {
  // Path of the row in the form values, used for the test ids, e.g. "focusMapping.cost.chain.0"
  rowName: string;
  index: number;
  rowsCount: number;
  onMove: (from: number, to: number) => void;
  onRemove: (index: number) => void;
  isRemoveDisabled?: boolean;
};

// Move up, move down and delete buttons of a row of an ordered field array. They are centered on the height of an input
// with the same form control margin, so a helper text or an error under an input of the row does not move them
const OrderedRowActions = ({
  rowName,
  index,
  rowsCount,
  onMove,
  onRemove,
  isRemoveDisabled = false,
}: OrderedRowActionsProps) => (
  <FormControl sx={{ flexShrink: 0 }}>
    <Box display="flex" alignItems="center" height={(theme) => theme.spacing(SPACING_5)}>
      <IconButton
        icon={<ArrowUpwardOutlinedIcon />}
        disabled={index === 0}
        onClick={() => onMove(index, index - 1)}
        tooltip={{ show: true, messageId: "moveUp" }}
        dataTestId={`btn_${rowName}_move_up`}
      />
      <IconButton
        icon={<ArrowDownwardOutlinedIcon />}
        disabled={index === rowsCount - 1}
        onClick={() => onMove(index, index + 1)}
        tooltip={{ show: true, messageId: "moveDown" }}
        dataTestId={`btn_${rowName}_move_down`}
      />
      <IconButton
        color="error"
        icon={<DeleteOutlinedIcon />}
        disabled={isRemoveDisabled}
        onClick={() => onRemove(index)}
        tooltip={{ show: true, messageId: "delete" }}
        dataTestId={`btn_${rowName}_delete`}
      />
    </Box>
  </FormControl>
);

export default OrderedRowActions;
