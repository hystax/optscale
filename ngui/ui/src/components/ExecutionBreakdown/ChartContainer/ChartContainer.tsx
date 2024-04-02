import MoreVertIcon from "@mui/icons-material/MoreVert";
import { Box } from "@mui/material";
import IconButton from "components/IconButton";
import MenuItem from "components/MenuItem";
import Popover from "components/Popover";
import SubTitle from "components/SubTitle";
import { useMlBreakdownLines } from "hooks/useMlBreakdownLines";
import Chart from "../Chart";
import { CHART_MARGIN_STYLES } from "../Chart/Chart";
import ChartDataSelector from "../ChartDataSelector";

const CHART_X_MARGINS = {
  mr: { xs: 0, md: `${CHART_MARGIN_STYLES.right}px` },
  ml: { xs: 0, md: `${CHART_MARGIN_STYLES.left}px` }
};

const BREAKDOWN_BY_QUERY_PARAMETER = "breakdownBy";
export const getChartQueryParam = (index) =>
  index === 0 ? BREAKDOWN_BY_QUERY_PARAMETER : `${BREAKDOWN_BY_QUERY_PARAMETER}_${index}`;

const ChartContainer = ({
  domain,
  milestonesGroupedByTimeTuples,
  highlightedStage,
  milestonesLine,
  colorsMap,
  breakdownConfig,
  breakdown,
  id,
  onRemove,
  onClone,
  onRename,
  selectedBreakdowns,
  onSelectedBreakdownsChange,
  name,
  showMilestones
}) => {
  const breakdownLines = useMlBreakdownLines({
    breakdown,
    breakdownConfig,
    selectedBreakdowns
  });

  return (
    <>
      <Box
        sx={{
          ...CHART_X_MARGINS,
          display: "flex",
          flexDirection: "row",
          justifyContent: "flex-start",
          alignItems: "center"
        }}
      >
        <SubTitle>{name}</SubTitle>
        <Popover
          renderMenu={({ closeHandler }) => (
            <>
              <MenuItem
                tabIndex={1}
                onClick={() => {
                  onRename(id);
                  closeHandler();
                }}
                messageId="rename"
              />
              <MenuItem
                tabIndex={1}
                onClick={() => {
                  onClone(id);
                  closeHandler();
                }}
                messageId="clone"
              />
              {typeof onRemove === "function" && (
                <MenuItem
                  tabIndex={1}
                  onClick={() => {
                    onRemove(id);
                    closeHandler();
                  }}
                  messageId="remove"
                />
              )}
            </>
          )}
          label={<IconButton icon={<MoreVertIcon />} />}
        />
      </Box>
      <Chart
        showMilestones={showMilestones}
        domain={domain}
        milestonesGroupedByTimeTuples={milestonesGroupedByTimeTuples}
        highlightedStage={highlightedStage}
        breakdownLines={breakdownLines}
        milestonesLine={milestonesLine}
        colors={({ id: colorId }) => colorsMap[colorId]}
      />
      <Box sx={CHART_X_MARGINS}>
        <ChartDataSelector
          selectedBreakdowns={selectedBreakdowns}
          colorsMap={colorsMap}
          breakdownConfig={breakdownConfig}
          onChange={onSelectedBreakdownsChange}
        />
      </Box>
    </>
  );
};

export default ChartContainer;
