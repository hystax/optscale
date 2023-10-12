import React, { useState, useEffect, useMemo } from "react";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import ActionBar from "components/ActionBar";
import ButtonGroup from "components/ButtonGroup";
import OrganizationsOverviewTable from "components/OrganizationsOverviewTable";
import PageContentWrapper from "components/PageContentWrapper";
import { ORGANIZATIONS_OVERVIEW_FILTERS } from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import { getQueryParams, updateQueryParams } from "utils/network";

const actionBarDefinition = {
  title: {
    messageId: "organizationsOverview",
    dataTestId: "lbl_orgs_overview"
  }
};

const OrganizationsOverview = ({ data, isLoading = false }) => {
  const { filterBy } = getQueryParams();

  const [activeFilter, setActiveFilter] = useState(
    Object.values(ORGANIZATIONS_OVERVIEW_FILTERS).includes(filterBy) ? filterBy : ORGANIZATIONS_OVERVIEW_FILTERS.ALL
  );

  useEffect(() => {
    updateQueryParams({ filterBy: activeFilter });
  }, [activeFilter]);

  const updatedData = useMemo(
    () =>
      data.map((organization) => {
        const exceededPools = [];
        const exceededForecasts = [];
        const exceededOrganizationIds = new Set();

        const { pools = [] } = organization;
        const { children = [], ...rootPool } = pools[0];
        const rootPoolWithChildren = [rootPool, ...children];

        rootPoolWithChildren.forEach((child) => {
          const { cost = 0, limit: childLimit = 0, forecast = 0 } = child;

          if (cost > childLimit) {
            exceededPools.push(child);
            exceededOrganizationIds.add(child.organization_id);
          }
          if (forecast > childLimit) {
            exceededForecasts.push(child);
            exceededOrganizationIds.add(child.organization_id);
          }
        });
        return {
          ...organization,
          limit: rootPool.limit,
          exceededPools,
          exceededForecasts,
          exceededOrganizationIds
        };
      }),
    [data]
  );

  const [tableData, setTableData] = useState(updatedData);

  useEffect(() => {
    const filteredData = (filter) =>
      ({
        [ORGANIZATIONS_OVERVIEW_FILTERS.REQUIRING_ATTENTION]: updatedData.filter((organization) =>
          organization.exceededOrganizationIds.has(organization.id)
        ),
        [ORGANIZATIONS_OVERVIEW_FILTERS.ALL_FINE]: updatedData.filter(
          (organization) => !organization.exceededOrganizationIds.has(organization.id)
        )
      }[filter] || updatedData);

    setTableData(filteredData(activeFilter));
  }, [activeFilter, updatedData]);

  const buttonsGroupDefinition = [
    {
      id: ORGANIZATIONS_OVERVIEW_FILTERS.ALL,
      messageId: ORGANIZATIONS_OVERVIEW_FILTERS.ALL,
      action: () => setActiveFilter(ORGANIZATIONS_OVERVIEW_FILTERS.ALL),
      dataTestId: "filter_all"
    },
    {
      id: ORGANIZATIONS_OVERVIEW_FILTERS.REQUIRING_ATTENTION,
      messageId: ORGANIZATIONS_OVERVIEW_FILTERS.REQUIRING_ATTENTION,
      action: () => setActiveFilter(ORGANIZATIONS_OVERVIEW_FILTERS.REQUIRING_ATTENTION),
      dataTestId: "filter_requiring_attention"
    },
    {
      id: ORGANIZATIONS_OVERVIEW_FILTERS.ALL_FINE,
      messageId: ORGANIZATIONS_OVERVIEW_FILTERS.ALL_FINE,
      action: () => setActiveFilter(ORGANIZATIONS_OVERVIEW_FILTERS.ALL_FINE),
      dataTestId: "filter_all_fine"
    }
  ];

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Grid container spacing={SPACING_2}>
          <Grid item xs={12}>
            <ButtonGroup
              buttons={buttonsGroupDefinition}
              activeButtonIndex={buttonsGroupDefinition.findIndex((button) => button.id === activeFilter)}
            />
          </Grid>
          <Grid item xs={12}>
            <OrganizationsOverviewTable data={tableData} total={data.length} isLoading={isLoading} />
          </Grid>
        </Grid>
      </PageContentWrapper>
    </>
  );
};

OrganizationsOverview.propTypes = {
  data: PropTypes.array.isRequired,
  isLoading: PropTypes.bool
};

export default OrganizationsOverview;
