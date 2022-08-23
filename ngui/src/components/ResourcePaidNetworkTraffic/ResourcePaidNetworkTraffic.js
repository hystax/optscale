import React from "react";
import { Grid, Typography } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import DashedTypography from "components/DashedTypography";
import Skeleton from "components/Skeleton";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TrafficExpensesMap from "components/TrafficExpensesMap";
import TrafficFromToLabel from "components/TrafficFromToLabel";
import WrapperCard from "components/WrapperCard";
import { TABLE_SELECTION_STATE, useTrafficExpenses } from "hooks/useTrafficExpenses";
import { SPACING_1 } from "utils/layouts";
import { REGION_EXPENSES_HEIGHT } from "utils/maps";

const ResourcePaidNetworkTraffic = ({ trafficExpenses, isLoading }) => {
  const { markers, onMapClick, tableData, tableSelectionState, columns, defaultZoom, defaultCenter, onFilterClear } =
    useTrafficExpenses(trafficExpenses);

  const title = (
    <Typography component="span">
      {tableSelectionState.state === TABLE_SELECTION_STATE.NOTHING_SELECTED ? (
        <FormattedMessage id="allNetworkTrafficExpenses" />
      ) : (
        <>
          <TrafficFromToLabel from={tableSelectionState.labels.from} to={tableSelectionState.labels.to} />
          <DashedTypography sx={{ marginLeft: 1 }} onClick={onFilterClear} component="span" dataTestId="lbl_clear_filter">
            <FormattedMessage id="clearFilter" />
          </DashedTypography>
        </>
      )}
    </Typography>
  );

  return (
    <Grid container spacing={SPACING_1}>
      <Grid item xs={12}>
        {isLoading ? (
          <Skeleton variant="rectangular" height={REGION_EXPENSES_HEIGHT} />
        ) : (
          <TrafficExpensesMap
            markers={markers}
            defaultZoom={defaultZoom}
            defaultCenter={defaultCenter}
            onMapClick={onMapClick}
          />
        )}
      </Grid>
      <Grid item xs={12}>
        <WrapperCard title={title}>
          {isLoading ? (
            <TableLoader columnsCounter={columns.length} showHeader />
          ) : (
            <Table
              data={tableData}
              columns={columns}
              localization={{
                emptyMessageId: "noTrafficExpenses"
              }}
            />
          )}
        </WrapperCard>
      </Grid>
    </Grid>
  );
};

ResourcePaidNetworkTraffic.propTypes = {
  trafficExpenses: PropTypes.array.isRequired,
  isLoading: PropTypes.bool
};

export default ResourcePaidNetworkTraffic;
