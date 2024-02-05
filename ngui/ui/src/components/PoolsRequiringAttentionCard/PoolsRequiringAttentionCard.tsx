import { useState, useMemo } from "react";
import BarChartOutlinedIcon from "@mui/icons-material/BarChartOutlined";
import ExitToAppOutlinedIcon from "@mui/icons-material/ExitToAppOutlined";
import StorageOutlinedIcon from "@mui/icons-material/StorageOutlined";
import { Stack } from "@mui/material";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import Button from "components/Button";
import IconButton from "components/IconButton";
import PoolLabel from "components/PoolLabel";
import { expenses, poolForecast } from "components/PoolsTable/columns";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TabsWrapper from "components/TabsWrapper";
import TextWithDataTestId from "components/TextWithDataTestId";
import WrapperCard from "components/WrapperCard";
import { useIsAllowed } from "hooks/useAllowedActions";
import PoolLimitIcon from "icons/PoolLimitIcon";
import { POOLS, getThisMonthPoolExpensesUrl, getThisMonthResourcesByPoolUrl } from "urls";
import { SPACING_2 } from "utils/layouts";
import useStyles from "./PoolsRequiringAttentionCard.styles";

const SetRootPoolLimit = () => {
  const { classes } = useStyles();

  const isManageResourcesAllowed = useIsAllowed({
    requiredActions: ["MANAGE_POOLS"]
  });

  return (
    <div className={classes.wrapper}>
      <PoolLimitIcon data-test-id="img_set_pool_limit" className={classes.icon} />
      <Typography paragraph align="center" gutterBottom data-test-id="p_set_pool_limit">
        <FormattedMessage id={isManageResourcesAllowed ? "poolsBackdropMessage" : "poolsContactManagerBackdropMessage"} />
      </Typography>
      {isManageResourcesAllowed && (
        <div>
          <Button
            size="medium"
            variant="contained"
            color="success"
            link={POOLS}
            messageId="setPoolLimit"
            dataTestId="btn_set_pool_limit"
          />
        </div>
      )}
    </div>
  );
};

const PoolsTable = ({ pools, sortColumn }) => {
  const tableData = useMemo(() => pools, [pools]);
  const navigate = useNavigate();

  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_name">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        accessorKey: "name",
        cell: ({
          row: {
            original: { name, purpose }
          }
        }) => <PoolLabel disableLink name={name} type={purpose} />
      },
      expenses({ defaultSort: sortColumn === "cost" ? "desc" : undefined }),
      poolForecast({ defaultSort: sortColumn === "forecast" ? "desc" : undefined }),
      {
        id: "actions",
        header: <FormattedMessage id="actions" />,
        enableSorting: false,
        cell: ({
          row: {
            original: { id }
          }
        }) => (
          <>
            <IconButton
              key="seeResourceList"
              onClick={() => navigate(getThisMonthResourcesByPoolUrl(id))}
              icon={<StorageOutlinedIcon fontSize="small" />}
              tooltip={{ show: true, value: <FormattedMessage id="seeResourceList" /> }}
            />
            <IconButton
              key="seeInCostExplorer"
              onClick={() => navigate(getThisMonthPoolExpensesUrl(id))}
              icon={<BarChartOutlinedIcon fontSize="small" />}
              tooltip={{ show: true, value: <FormattedMessage id="seeInCostExplorer" /> }}
            />
          </>
        )
      }
    ],
    [navigate, sortColumn]
  );

  return (
    <Table
      columns={columns}
      enableSearchQueryParam={false}
      enablePaginationQueryParam={false}
      data={tableData}
      pageSize={5}
      counters={{ showCounters: true, hideTotal: false, hideDisplayed: true }}
    />
  );
};

const Tabs = ({ withExceededLimit, withForecastedOverspend }) => {
  const [activeTab, setActiveTab] = useState();

  const tabs = [
    {
      title: "exceededLimit",
      dataTestId: "tab_exceeded_limit",
      node: <PoolsTable pools={withExceededLimit} sortColumn="cost" />
    },
    {
      title: "forecastedOverspend",
      dataTestId: "tab_forecasted_overspend",
      node: <PoolsTable pools={withForecastedOverspend} sortColumn="forecast" />
    }
  ];

  return (
    <Stack spacing={SPACING_2}>
      <div>
        <TabsWrapper
          tabsProps={{
            tabs,
            defaultTab: "exceededLimit",
            name: "pools",
            activeTab,
            shouldhaveQueryParam: false,
            handleChange: (event, value) => {
              setActiveTab(value);
            }
          }}
        />
      </div>
    </Stack>
  );
};

const PoolsRequiringAttentionCard = ({ withExceededLimit, withForecastedOverspend, isLoading, rootPoolLimitUnset }) => {
  const navigate = useNavigate();

  const goToPools = () => navigate(POOLS);

  const renderContent = () =>
    rootPoolLimitUnset ? (
      <SetRootPoolLimit />
    ) : (
      <Tabs withExceededLimit={withExceededLimit} withForecastedOverspend={withForecastedOverspend} />
    );

  return (
    <WrapperCard
      needAlign
      title={<FormattedMessage id="poolsRequiringAttention" />}
      titleButton={{
        type: "icon",
        tooltip: {
          title: <FormattedMessage id="goToPools" />
        },
        buttonProps: {
          icon: <ExitToAppOutlinedIcon />,
          isLoading,
          onClick: goToPools,
          dataTestId: "btn_go_to_pools"
        }
      }}
      dataTestIds={{
        wrapper: "block_pools",
        title: "lbl_pools"
      }}
      elevation={0}
    >
      {isLoading ? <TableLoader showHeader /> : renderContent()}
    </WrapperCard>
  );
};

export default PoolsRequiringAttentionCard;
