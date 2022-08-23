import React, { useState, useMemo } from "react";
import ErrorIcon from "@mui/icons-material/Error";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import Tab from "@mui/material/Tab";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { useForm, Controller } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { useDispatch, useSelector } from "react-redux";
import { ASSIGN_RESOURCES, ASSIGN_RESOURCES_REQUEST } from "api/restapi/actionTypes";
import Accordion from "components/Accordion";
import ButtonLoader from "components/ButtonLoader";
import CloudLabel from "components/CloudLabel";
import CloudResourceId from "components/CloudResourceId";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import Icon from "components/Icon";
import PoolLabel from "components/PoolLabel";
import TabContent from "components/TabContent";
import Table from "components/Table";
import Tabs from "components/Tabs";
import TextWithDataTestId from "components/TextWithDataTestId";
import AvailablePoolSelectorContainer from "containers/AvailablePoolSelectorContainer";
import EmployeeSelectorContainer from "containers/EmployeeSelectorContainer";
import PoolOwnerSelectorContainer from "containers/PoolOwnerSelectorContainer";
import { useApiState } from "hooks/useApiState";
import { setActiveTab } from "reducers/resources/actionCreators";
import { intl } from "translations/react-intl-config";
import { getValuesByObjectKey, getLength, isEmpty } from "utils/arrays";
import { OWNED, MANAGED, RESTRICTED } from "utils/constants";
import { RESOURCE_ID_COLUMN_CELL_STYLE } from "utils/tables";
import useStyles from "./SplitResources.styles";

const TO_ME_TAB_ID = "split-resources-to-me-tab";
const TO_ME_TAB_CONTENT_ID = "split-resources-to-me-tabpanel";

const TO_SOMEONE_ELSE_TAB_ID = "split-resources-to-someone-else-tab";
const TO_SOMEONE_ELSE_TAB_CONTENT_ID = "split-resources-to-someone-else-tabpanel";

const SEND_REQUEST_TAB_ID = "split-resources-send-request-tab";
const SEND_REQUEST_TAB_CONTENT_ID = "split-resources-send-request-tabpanel";

const POOL_ID = "poolId";
const OWNER_ID = "ownerId";
const EMPLOYEE_ID = "employeeId";

const tabsA11yProps = {
  tabs: {
    "area-label": "split-resources-tabs"
  },
  toMe: {
    tab: {
      id: TO_ME_TAB_ID,
      "aria-controls": TO_ME_TAB_CONTENT_ID
    },
    tabContent: {
      id: TO_ME_TAB_CONTENT_ID,
      ariaLabelledby: TO_ME_TAB_ID
    }
  },
  toSomeoneElse: {
    tab: {
      id: TO_SOMEONE_ELSE_TAB_ID,
      "aria-controls": TO_SOMEONE_ELSE_TAB_CONTENT_ID
    },
    tabContent: {
      id: TO_SOMEONE_ELSE_TAB_CONTENT_ID,
      ariaLabelledby: TO_SOMEONE_ELSE_TAB_ID
    }
  },
  sendRequest: {
    tab: {
      id: SEND_REQUEST_TAB_ID,
      "aria-controls": SEND_REQUEST_TAB_CONTENT_ID
    },
    tabContent: {
      id: SEND_REQUEST_TAB_CONTENT_ID,
      ariaLabelledby: SEND_REQUEST_TAB_ID
    }
  }
};

const getActiveTransferIcon = (rowData) =>
  rowData.has_active_transfer ? (
    <Box display="flex">
      <CloudResourceId cloudResourceId={rowData.cloud_resource_id} />
      <Icon icon={ErrorIcon} color="warning" hasLeftMargin dataTestId="logo_transfer_state" />
    </Box>
  ) : (
    <CloudResourceId cloudResourceId={rowData.cloud_resource_id} />
  );

const getActiveTransferLegend = (resources) =>
  resources.some((item) => item.has_active_transfer) ? (
    <Box display="flex">
      <Icon icon={ErrorIcon} color="warning" hasRightMargin />
      <Typography data-test-id="p_transfer">
        {" - "}
        <FormattedMessage id="activeTransferRequestLegend" />
      </Typography>
    </Box>
  ) : null;

const renderPoolSelector = ({ splitGroup, permission, error, helperText }) => (
  <AvailablePoolSelectorContainer
    splitGroup={splitGroup}
    error={error}
    helperText={helperText}
    permission={permission}
    dataTestId="selector_pool"
  />
);
const renderPoolOwnerSelector = ({ splitGroup, excludeMyself, error, helperText }) => (
  <PoolOwnerSelectorContainer
    splitGroup={splitGroup}
    excludeMyself={excludeMyself}
    error={error}
    helperText={helperText}
    dataTestId="selector_owner"
  />
);
const renderEmployeeSelector = ({ splitGroup, excludeMyself, error, helperText }) => (
  <EmployeeSelectorContainer
    splitGroup={splitGroup}
    excludeMyself={excludeMyself}
    error={error}
    helperText={helperText}
    dataTestId="selector_user"
  />
);

const renderTable = (data, columns) =>
  data.length > 50 ? null : <Table data={data} columns={columns} localization={{ emptyMessageId: "noResources" }} />;

const AssignButtonLoader = ({ isLoading }) => (
  <ButtonLoader
    isLoading={isLoading}
    variant="contained"
    color="primary"
    messageId="assign"
    type="submit"
    dataTestId="btn_assign"
  />
);

const SplitResources = ({ data, assignResourcesOnSubmit, assignResourcesRequestOnSubmit }) => {
  const dispatch = useDispatch();
  const resourcesState = useSelector((state) => state.resources) || {};
  const { isLoading: assignResourcesIsLoading } = useApiState(ASSIGN_RESOURCES);
  const { isLoading: assignResourcesRequestIsLoading } = useApiState(ASSIGN_RESOURCES_REQUEST);
  const { classes } = useStyles();

  const {
    handleSubmit,
    control,
    reset,
    formState: { errors }
  } = useForm();

  const {
    owned: ownedResources = [],
    managed: managedResources = [],
    restricted: restrictedResources = []
  } = useMemo(() => data, [data]);

  const [expanded, setExpanded] = useState({
    [OWNED]: true,
    [MANAGED]: false,
    [RESTRICTED]: false
  });

  // One panel at a time is expanded
  const toggleExpanded = (panel) => {
    setExpanded({
      ...{
        ...expanded,
        ...{
          [OWNED]: false,
          [MANAGED]: false,
          [RESTRICTED]: false
        },
        [panel]: !expanded[panel]
      }
    });
  };

  const { [OWNED]: { tabIndex: ownedTabIndex = 0 } = {}, [MANAGED]: { tabIndex: managedTabIndex = 0 } = {} } = resourcesState;

  const changeTabValue = (value, splitGroup) => {
    reset();
    dispatch(setActiveTab(value, splitGroup));
  };

  const renderToMeTabContent = (resources, splitGroup) => {
    const resourceIds = getValuesByObjectKey(resources, "resource_id");
    return (
      <TabContent value={0} index={0} {...tabsA11yProps.toMe.tabContent}>
        <form onSubmit={handleSubmit(() => assignResourcesOnSubmit(splitGroup, resourceIds, false))} noValidate>
          <Controller
            name={POOL_ID}
            control={control}
            rules={{
              validate: () => (!resourcesState[splitGroup][POOL_ID] ? intl.formatMessage({ id: "thisFieldIsRequired" }) : true)
            }}
            defaultValue=""
            render={() =>
              renderPoolSelector({
                splitGroup,
                permission: ["MANAGE_RESOURCES", "MANAGE_OWN_RESOURCES"],
                error: !!errors[POOL_ID],
                helperText: errors[POOL_ID] && errors[POOL_ID].message
              })
            }
          />
          <FormButtonsWrapper withBottomMargin>
            <AssignButtonLoader isLoading={assignResourcesIsLoading} />
          </FormButtonsWrapper>
        </form>
      </TabContent>
    );
  };

  const renderToSomeoneElseTabContent = (resources, splitGroup) => {
    const resourceIds = getValuesByObjectKey(resources, "resource_id");
    return (
      <TabContent value={1} index={1} {...tabsA11yProps.toSomeoneElse.tabContent}>
        <form onSubmit={handleSubmit(() => assignResourcesOnSubmit(splitGroup, resourceIds, true))} noValidate>
          <Controller
            name={POOL_ID}
            control={control}
            defaultValue=""
            rules={{
              validate: () => (!resourcesState[splitGroup][POOL_ID] ? intl.formatMessage({ id: "thisFieldIsRequired" }) : true)
            }}
            render={() =>
              renderPoolSelector({
                splitGroup,
                permission: ["MANAGE_RESOURCES"],
                error: !!errors[POOL_ID],
                helperText: errors[POOL_ID] && errors[POOL_ID].message
              })
            }
          />
          <Controller
            name={OWNER_ID}
            control={control}
            defaultValue=""
            rules={{
              validate: () => (!resourcesState[splitGroup][OWNER_ID] ? intl.formatMessage({ id: "thisFieldIsRequired" }) : true)
            }}
            render={() =>
              renderPoolOwnerSelector({
                splitGroup,
                excludeMyself: true,
                error: !!errors[OWNER_ID],
                helperText: errors[OWNER_ID] && errors[OWNER_ID].message
              })
            }
          />
          <FormButtonsWrapper withBottomMargin>
            <AssignButtonLoader isLoading={assignResourcesIsLoading} />
          </FormButtonsWrapper>
        </form>
      </TabContent>
    );
  };

  const renderSendRequestTabContent = (resources, splitGroup) => {
    const resourceIds = getValuesByObjectKey(resources, "resource_id");
    return (
      <TabContent value={2} index={2} {...tabsA11yProps.sendRequest.tabContent}>
        <form onSubmit={handleSubmit(() => assignResourcesRequestOnSubmit(splitGroup, resourceIds))} noValidate>
          <Controller
            name={EMPLOYEE_ID}
            control={control}
            rules={{
              validate: () =>
                !resourcesState[splitGroup][EMPLOYEE_ID] ? intl.formatMessage({ id: "thisFieldIsRequired" }) : true
            }}
            defaultValue=""
            render={() =>
              renderEmployeeSelector({
                splitGroup,
                excludeMyself: true,
                error: !!errors[EMPLOYEE_ID],
                helperText: errors[EMPLOYEE_ID] && errors[EMPLOYEE_ID].message
              })
            }
          />
          <FormButtonsWrapper>
            <AssignButtonLoader isLoading={assignResourcesRequestIsLoading} />
          </FormButtonsWrapper>
        </form>
      </TabContent>
    );
  };

  const getTabs = (splitGroup) => {
    const TO_ME_TAB = "toMe";
    const TO_SOMEONE_ELSE = "toSomeoneElse";
    const SEND_REQUEST = "sendRequest";

    const tabs = {
      [TO_ME_TAB]: (
        <Tab
          value={0}
          key={0}
          {...tabsA11yProps.toMe.tab}
          label={<FormattedMessage id="toMe" />}
          className={classes.tab}
          data-test-id="tab_me"
        />
      ),
      [TO_SOMEONE_ELSE]: (
        <Tab
          value={1}
          key={1}
          {...tabsA11yProps.toSomeoneElse.tab}
          label={<FormattedMessage id="toSomeoneElse" />}
          className={classes.tab}
          data-test-id="tab_someone"
        />
      ),
      [SEND_REQUEST]: (
        <Tab
          value={2}
          key={2}
          {...tabsA11yProps.sendRequest.tab}
          label={<FormattedMessage id="sendRequest" />}
          className={classes.tab}
          data-test-id="tab_send_request"
        />
      )
    };
    return {
      [OWNED]: [tabs[TO_ME_TAB], tabs[TO_SOMEONE_ELSE], tabs[SEND_REQUEST]],
      [MANAGED]: [tabs[TO_ME_TAB], tabs[TO_SOMEONE_ELSE], tabs[SEND_REQUEST]]
    }[splitGroup];
  };

  const getTabContent = (tabIndex, resources, splitGroup) =>
    ({
      0: renderToMeTabContent(resources, splitGroup),
      1: renderToSomeoneElseTabContent(resources, splitGroup),
      2: renderSendRequestTabContent(resources, splitGroup)
    }[tabIndex]);

  const getPanelTabs = (tabIndex, splitGroup, resources) => (
    <>
      <Tabs
        {...tabsA11yProps.tabs}
        value={tabIndex}
        onChange={(event, value) => {
          changeTabValue(value, splitGroup);
        }}
      >
        {getTabs(splitGroup)}
      </Tabs>
      {getTabContent(tabIndex, resources, splitGroup)}
    </>
  );

  const ownedResourcesColumns = useMemo(
    () => [
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_id">
            <FormattedMessage id="id" />
          </TextWithDataTestId>
        ),
        accessor: "cloud_resource_id",
        defaultSort: "asc",
        style: RESOURCE_ID_COLUMN_CELL_STYLE,
        Cell: ({ row: { original } }) => getActiveTransferIcon(original)
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_name">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        accessor: "name"
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_cloud">
            <FormattedMessage id="dataSource" />
          </TextWithDataTestId>
        ),
        accessor: "cloud_account_name",
        Cell: ({ row: { original } }) => (
          <CloudLabel id={original.cloud_account_id} name={original.cloud_account_name} type={original.cloud_type} />
        )
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_pool">
            <FormattedMessage id="pool" />
          </TextWithDataTestId>
        ),
        accessor: "pool_name",
        Cell: ({ row: { original } }) => (
          <PoolLabel id={original.pool_id} name={original.pool_name} type={original.pool_purpose} />
        )
      }
    ],
    []
  );

  const renderOwnedPanel = (
    <Accordion
      expanded={expanded[OWNED]}
      onChange={() => toggleExpanded(OWNED)}
      disableExpandedSpacing
      headerDataTestId="sp_owned"
    >
      <Typography>
        <FormattedMessage id="owned" />
        {` (${getLength(ownedResources)})`}
      </Typography>
      {expanded[OWNED] ? (
        <Grid container direction="column" wrap="nowrap">
          <Grid item>{getPanelTabs(ownedTabIndex, OWNED, ownedResources)}</Grid>
          <Grid item>
            {getActiveTransferLegend(ownedResources)}
            {renderTable(ownedResources, ownedResourcesColumns)}
          </Grid>
        </Grid>
      ) : null}
    </Accordion>
  );

  const managedResourcesColumns = useMemo(
    () => [
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_id">
            <FormattedMessage id="id" />
          </TextWithDataTestId>
        ),
        accessor: "cloud_resource_id",
        defaultSort: "asc",
        style: RESOURCE_ID_COLUMN_CELL_STYLE,
        Cell: ({ row: { original } }) => getActiveTransferIcon(original)
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_name">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        accessor: "name"
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_cloud">
            <FormattedMessage id="dataSource" />
          </TextWithDataTestId>
        ),
        accessor: "cloud_account_name",
        Cell: ({ row: { original } }) => (
          <CloudLabel id={original.cloud_account_id} name={original.cloud_account_name} type={original.cloud_type} />
        )
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_pool">
            <FormattedMessage id="pool" />
          </TextWithDataTestId>
        ),
        accessor: "pool_name",
        Cell: ({ row: { original } }) => (
          <PoolLabel id={original.pool_id} name={original.pool_name} type={original.pool_purpose} />
        )
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_owner">
            <FormattedMessage id="owner" />
          </TextWithDataTestId>
        ),
        accessor: "owner_name"
      }
    ],
    []
  );

  const renderManagedPanel = (
    <Accordion
      expanded={expanded[MANAGED]}
      onChange={() => toggleExpanded(MANAGED)}
      disableExpandedSpacing
      headerDataTestId="sp_managed"
    >
      <Typography>
        <FormattedMessage id="managed" />
        {` (${getLength(managedResources)})`}
      </Typography>
      {expanded[MANAGED] ? (
        <Grid container direction="column" wrap="nowrap">
          <Grid item>{getPanelTabs(managedTabIndex, MANAGED, managedResources)}</Grid>
          <Grid item>
            {getActiveTransferLegend(managedResources)}
            {renderTable(managedResources, managedResourcesColumns)}
          </Grid>
        </Grid>
      ) : null}
    </Accordion>
  );

  const restrictedResourcesColumns = useMemo(
    () => [
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_id">
            <FormattedMessage id="id" />
          </TextWithDataTestId>
        ),
        accessor: "cloud_resource_id",
        defaultSort: "asc",
        style: RESOURCE_ID_COLUMN_CELL_STYLE,
        Cell: ({ row: { original } }) => getActiveTransferIcon(original)
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_name">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        accessor: "name"
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_cloud">
            <FormattedMessage id="dataSource" />
          </TextWithDataTestId>
        ),
        accessor: "cloud_account_name"
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_pool">
            <FormattedMessage id="pool" />
          </TextWithDataTestId>
        ),
        accessor: "pool_name"
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_owner">
            <FormattedMessage id="owner" />
          </TextWithDataTestId>
        ),
        accessor: "owner_name"
      }
    ],
    []
  );

  const renderRestrictedPanel = (
    <Accordion
      expanded={expanded[RESTRICTED]}
      onChange={() => toggleExpanded(RESTRICTED)}
      disableExpandedSpacing
      headerDataTestId="sp_restricted"
    >
      <Typography>
        <FormattedMessage id="restricted" />
        {` (${getLength(restrictedResources)})`}
      </Typography>
      {expanded[RESTRICTED] ? (
        <Grid container direction="column" wrap="nowrap">
          <Grid item>
            <Typography align="center" paragraph data-test-id="p_permissions">
              <FormattedMessage id="youDoNotHaveEnoughPermissions" />
            </Typography>
          </Grid>
          <Grid item>
            {getActiveTransferLegend(restrictedResources)}
            {renderTable(restrictedResources, restrictedResourcesColumns)}
          </Grid>
        </Grid>
      ) : null}
    </Accordion>
  );

  return (
    <>
      {!isEmpty(ownedResources) ? renderOwnedPanel : null}
      {!isEmpty(managedResources) ? renderManagedPanel : null}
      {!isEmpty(restrictedResources) ? renderRestrictedPanel : null}
    </>
  );
};

AssignButtonLoader.propTypes = {
  isLoading: PropTypes.bool
};

SplitResources.propTypes = {
  data: PropTypes.object.isRequired,
  assignResourcesOnSubmit: PropTypes.func.isRequired,
  assignResourcesRequestOnSubmit: PropTypes.func.isRequired
};

export default SplitResources;
