import { Box, FormControlLabel, Switch, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import ChartLegendToggle from "components/ChartLegendToggle";
import { SPACING_1 } from "utils/layouts";
import BreakdownBySelector from "./BreakdownBySelector";
import BreakdownTypeSelector from "./BreakdownTypeSelector";
import { ApplyFilterByCategoryToggleProps, HeadingProps } from "./types";

const ApplyFilterByCategoryToggle = ({ onChange, checked }: ApplyFilterByCategoryToggleProps) => (
  <FormControlLabel
    control={<Switch onChange={(e) => onChange(e.target.checked)} checked={checked} />}
    label={
      <Typography>
        <FormattedMessage id="applyFilterByCategory" />
      </Typography>
    }
    labelPlacement="start"
  />
);

const Heading = ({
  breakdownBy,
  onBreakdownChange,
  metaNames,
  breakdownType,
  onBreakdownTypeChange,
  applyFilterByCategory,
  onApplyFilterByCategoryChange,
  withLegend,
  onWithLegendChange,
}: HeadingProps) => (
  <Box display="flex" gap={SPACING_1} flexWrap="wrap">
    <BreakdownBySelector value={breakdownBy} onChange={onBreakdownChange} metaNames={metaNames} />
    <BreakdownTypeSelector value={breakdownType} onChange={onBreakdownTypeChange} />
    <ChartLegendToggle checked={withLegend} onChange={onWithLegendChange} />
    <ApplyFilterByCategoryToggle checked={applyFilterByCategory} onChange={onApplyFilterByCategoryChange} />
  </Box>
);

export default Heading;
