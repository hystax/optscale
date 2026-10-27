import React from "react";
import CalendarTodayOutlinedIcon from "@mui/icons-material/CalendarTodayOutlined";
import CloseIcon from "@mui/icons-material/Close";
import { Box, Button, Popover, IconButton } from "@mui/material";
import { FormattedMessage, useIntl } from "react-intl";
import IntervalTimePicker from "components/IntervalTimePicker";
import { EN_FORMAT, format } from "utils/datetime";

export type RangeValue = {
  from?: number;
  to?: number;
};

type RangeFilterProps = {
  label: React.ReactNode;
  buttonIcon?: React.ReactNode;
  onChange?: (range: RangeValue) => void;
  appliedRange: RangeValue;
};

type SelectionStateButtonProps = {
  appliedRange: RangeValue;
  onClick: (event: React.MouseEvent<HTMLButtonElement>) => void;
  id: string;
  label: React.ReactNode;
  icon?: React.ReactNode;
  selectionLabel: () => React.ReactNode;
};

const formatDate = (date: number) => format(date, EN_FORMAT);

const SelectionStateButton = ({ appliedRange, label, selectionLabel, onClick, id, icon }: SelectionStateButtonProps) => (
  <Button
    aria-describedby={id}
    variant={appliedRange.from || appliedRange.to ? "contained" : "outlined"}
    onClick={onClick}
    color="primary"
    startIcon={icon}
  >
    {label} ({selectionLabel()})
  </Button>
);

const RangeFilter: React.FC<RangeFilterProps> = ({
  label,
  buttonIcon = <CalendarTodayOutlinedIcon />,
  onChange,
  appliedRange,
}) => {
  const intl = useIntl();

  const [anchorEl, setAnchorEl] = React.useState<HTMLButtonElement | null>(null);
  const [selectedRange, setSelectedRange] = React.useState<RangeValue>({
    from: undefined,
    to: undefined,
  });

  const popoverId = React.useId();
  const open = Boolean(anchorEl);
  const id = open ? `range-filter-${popoverId}` : `range-filter-${popoverId}-closed`;

  const handleOpen = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
    setSelectedRange(appliedRange);
  };

  const handleCancel = () => {
    setAnchorEl(null);
    setSelectedRange(appliedRange);
  };

  const handleApply = () => {
    setAnchorEl(null);
    onChange?.(selectedRange);
  };

  const handleFromChange = (value: Date) => {
    setSelectedRange((prev) => ({
      ...prev,
      from: +value,
    }));
  };

  const handleToChange = (value: Date) => {
    setSelectedRange((prev) => ({
      ...prev,
      to: +value,
    }));
  };

  const handleResetFrom = () => {
    setSelectedRange((prev) => ({
      ...prev,
      from: undefined,
    }));
  };

  const handleResetTo = () => {
    setSelectedRange((prev) => ({
      ...prev,
      to: undefined,
    }));
  };

  const hasChanges = JSON.stringify(selectedRange) !== JSON.stringify(appliedRange);

  return (
    <div>
      <SelectionStateButton
        appliedRange={appliedRange}
        label={label}
        selectionLabel={() => {
          const { from, to } = appliedRange;

          if (from && to) {
            return `${formatDate(from)} - ${formatDate(to)}`;
          }

          if (from) {
            return `${intl.formatMessage({ id: "from" })}: ${formatDate(from)}`;
          }

          if (to) {
            return `${intl.formatMessage({ id: "to" })}: ${formatDate(to)}`;
          }

          return intl.formatMessage({ id: "any" });
        }}
        onClick={handleOpen}
        id={id}
        icon={buttonIcon}
      />
      <Popover
        id={id}
        open={open}
        anchorEl={anchorEl}
        onClose={handleCancel}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "left",
        }}
      >
        <Box sx={{ width: "400px", p: 2 }}>
          <Box sx={{ display: "flex", gap: 1, alignItems: "center", mb: 2 }}>
            <Box sx={{ width: "100%" }}>
              <IntervalTimePicker
                name="from"
                value={selectedRange.from}
                onApply={handleFromChange}
                format={EN_FORMAT}
                fullWidth
                notSetMessageId="notSet"
                labelMessageId="from"
              />
            </Box>
            <Box>
              <IconButton size="small" onClick={handleResetFrom}>
                <CloseIcon fontSize="small" />
              </IconButton>
            </Box>
          </Box>
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
              <Box sx={{ width: "100%" }}>
                <IntervalTimePicker
                  name="to"
                  value={selectedRange.to}
                  onApply={handleToChange}
                  format={EN_FORMAT}
                  fullWidth
                  notSetMessageId="notSet"
                  labelMessageId="to"
                />
              </Box>
              <Box>
                <IconButton size="small" onClick={handleResetTo}>
                  <CloseIcon fontSize="small" />
                </IconButton>
              </Box>
            </Box>
          </Box>
          <Box sx={{ display: "flex", justifyContent: "flex-end", gap: 1, pt: 1 }}>
            <Button onClick={handleCancel} variant="outlined">
              <FormattedMessage id="cancel" />
            </Button>
            <Button onClick={handleApply} variant="contained" disabled={!hasChanges} color="primary">
              <FormattedMessage id="apply" />
            </Button>
          </Box>
        </Box>
      </Popover>
    </div>
  );
};

export default RangeFilter;
