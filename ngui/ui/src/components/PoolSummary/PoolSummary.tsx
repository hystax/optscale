import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import { Divider, Stack, Box, Typography } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import Circle from "components/Circle";
import FormattedMoney from "components/FormattedMoney";
import KeyValueChartTooltipBody from "components/KeyValueChartTooltipBody";
import KeyValueLabel from "components/KeyValueLabel";
import PieChart from "components/PieChart";
import PoolExpenses from "components/PoolExpenses";
import PoolForecast from "components/PoolForecast";
import { EditPoolForm } from "components/PoolForm";
import PoolLabel from "components/PoolLabel";
import PoolTypeIcon from "components/PoolTypeIcon";
import { useToggle } from "hooks/useToggle";
import { isEmpty } from "utils/arrays";
import { getColorScale } from "utils/charts";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { SPACING_1, SPACING_2 } from "utils/layouts";

const renderTooltipBody = (sectionData) => {
  const {
    value,
    label,
    data: { purpose }
  } = sectionData;

  return <KeyValueChartTooltipBody value={value} text={<PoolLabel name={label} type={purpose} disableLink />} />;
};

const buildChartData = (pools) =>
  pools.map(({ name, cost, purpose }) => ({
    id: name,
    value: cost,
    purpose
  }));

const Chart = ({ poolPurpose, poolCost, childPools }) => {
  const theme = useTheme();
  const colorScale = getColorScale(theme.palette.chart);
  const childrenCost = childPools.reduce((result, { cost = 0 }) => result + cost, 0);
  const thisPoolCost = poolCost - childrenCost;
  return (
    <Stack spacing={SPACING_2} alignItems="center" direction="row">
      <div>
        <PieChart
          data={buildChartData([
            {
              name: <FormattedMessage id="(thisPool)" />,
              cost: thisPoolCost,
              purpose: poolPurpose
            },
            ...childPools
          ])}
          style={{ height: 30, width: 30 }}
          renderTooltipBody={renderTooltipBody}
        />
      </div>
      <div>
        <Box display="flex" alignItems="center">
          <Circle color={colorScale("root")} mr={1} />
          <PoolTypeIcon type={poolPurpose} hasRightMargin />
          <KeyValueLabel
            messageId="(thisPool)"
            value={<FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={thisPoolCost} />}
          />
        </Box>
        {childPools.map(({ id, name, purpose, cost = 0 }) => (
          <Box key={id} display="flex" alignItems="center">
            <Circle color={colorScale(id)} mr={1} />
            <KeyValueLabel
              key={id}
              renderKey={() => <PoolLabel name={name} type={purpose} disableLink />}
              value={<FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cost} />}
            />
          </Box>
        ))}
      </div>
    </Stack>
  );
};

const Summary = ({ name, purpose, limit, owner }) => (
  <>
    <KeyValueLabel messageId="name" value={<PoolLabel name={name} type={purpose} disableLink />} />
    <KeyValueLabel messageId="limit" value={<FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={limit} />} />
    <KeyValueLabel messageId="owner" value={owner} />
  </>
);

const PoolSummary = ({ pool, parentPool, childPools, onSuccess }) => {
  const { limit = 0, cost = 0, forecast = 0, name, purpose, default_owner_name: owner } = pool;
  const { unallocated_limit: unallocatedLimit = 0 } = parentPool;

  const [isEditMode, toggleIsEditMode] = useToggle(false);

  return (
    <Stack spacing={SPACING_2}>
      <div>
        {isEditMode ? (
          <EditPoolForm poolInfo={pool} unallocatedLimit={unallocatedLimit} onSuccess={onSuccess} onCancel={toggleIsEditMode} />
        ) : (
          <Stack spacing={SPACING_1}>
            <div>
              <Summary name={name} purpose={purpose} limit={limit} owner={owner} />
            </div>
            <div>
              <Button messageId="edit" onClick={toggleIsEditMode} startIcon={<EditOutlinedIcon />} />
            </div>
          </Stack>
        )}
      </div>
      <Divider />
      <Box display="flex" alignItems="center">
        <Typography>
          <FormattedMessage id="expensesThisMonth" />
        </Typography>
        &#58;&nbsp;
        <PoolExpenses limit={limit} cost={cost} />
      </Box>
      <Box display="flex" alignItems="center">
        <Typography>
          <FormattedMessage id="forecastThisMonth" />
        </Typography>
        &#58;&nbsp;
        <PoolForecast limit={limit} forecast={forecast} />
      </Box>
      {!isEmpty(childPools) && <Chart poolPurpose={purpose} poolCost={cost} childPools={childPools} />}
    </Stack>
  );
};

export default PoolSummary;
