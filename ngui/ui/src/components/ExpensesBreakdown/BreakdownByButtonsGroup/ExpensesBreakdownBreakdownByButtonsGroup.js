import React from "react";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import ButtonGroup from "components/ButtonGroup";
import Hidden from "components/Hidden";
import Selector from "components/Selector";
import { POOL_DETAILS, CLOUD_DETAILS, OWNER_DETAILS, EXPENSES_FILTERBY_TYPES, KUBERNETES_CNR } from "utils/constants";

const filters = [
  { id: EXPENSES_FILTERBY_TYPES.SERVICE, messageId: "service", forTypes: [CLOUD_DETAILS], excludeFor: [KUBERNETES_CNR] },
  {
    id: EXPENSES_FILTERBY_TYPES.REGION,
    messageId: "region",
    forTypes: [CLOUD_DETAILS],
    excludeFor: [KUBERNETES_CNR]
  },
  { id: EXPENSES_FILTERBY_TYPES.NODE, messageId: "node", forTypes: [CLOUD_DETAILS], showOnlyFor: [KUBERNETES_CNR] },
  { id: EXPENSES_FILTERBY_TYPES.NAMESPACE, messageId: "namespace", forTypes: [CLOUD_DETAILS], showOnlyFor: [KUBERNETES_CNR] },
  { id: EXPENSES_FILTERBY_TYPES.POOL, messageId: "pool", forTypes: [POOL_DETAILS, CLOUD_DETAILS, OWNER_DETAILS] },
  { id: EXPENSES_FILTERBY_TYPES.CLOUD, messageId: "source", forTypes: [POOL_DETAILS, OWNER_DETAILS] },
  { id: EXPENSES_FILTERBY_TYPES.EMPLOYEE, messageId: "owner", forTypes: [POOL_DETAILS, CLOUD_DETAILS] },
  { id: EXPENSES_FILTERBY_TYPES.RESOURCE_TYPE, messageId: "resourceType", forTypes: [CLOUD_DETAILS] }
];

const getButtonsGroup = (type, onClick, dataSourceType) =>
  filters
    .filter(({ forTypes }) => forTypes.includes(type)) // only filters for type
    .filter(({ showOnlyFor }) => !showOnlyFor || showOnlyFor?.includes(dataSourceType)) // only specific filters (i guess it could be refactored to be more readable)
    .filter(({ excludeFor }) => !excludeFor || !excludeFor?.includes(dataSourceType))
    .map((f) => ({ action: () => onClick(f.id), ...f })); // adding action

const getActiveButtonIndex = (buttonsGroup, filterBy) => {
  const index = buttonsGroup.indexOf(buttonsGroup.find((button) => button.id === filterBy));
  return index === -1 ? 0 : index;
};

const ExpensesBreakdownBreakdownByButtonsGroup = ({ type, onClick, filterBy, dataSourceType }) => {
  const buttonsGroup = getButtonsGroup(type, onClick, dataSourceType);
  const activeButtonIndex = getActiveButtonIndex(buttonsGroup, filterBy);

  return (
    <>
      <Hidden mode="up" breakpoint="sm">
        <Selector
          sx={{ display: { xs: "inherit", sm: "none" } }}
          data={{
            selected: buttonsGroup[activeButtonIndex === -1 ? 0 : activeButtonIndex].id,
            items: buttonsGroup.map((button) => ({
              name: <FormattedMessage id={button.messageId} />,
              value: button.id
            }))
          }}
          labelId="breakdownBy"
          onChange={(buttonId) => {
            buttonsGroup.find((button) => button.id === buttonId).action();
          }}
        />
      </Hidden>
      <Hidden mode="down" breakpoint="sm">
        <Typography component="span">
          <FormattedMessage id="breakdownBy" />{" "}
        </Typography>
        <ButtonGroup buttons={buttonsGroup} activeButtonIndex={activeButtonIndex} />
      </Hidden>
    </>
  );
};

ExpensesBreakdownBreakdownByButtonsGroup.propTypes = {
  type: PropTypes.oneOf([POOL_DETAILS, CLOUD_DETAILS, OWNER_DETAILS]),
  filterBy: PropTypes.string.isRequired,
  onClick: PropTypes.func,
  dataSourceType: PropTypes.string
};

export default ExpensesBreakdownBreakdownByButtonsGroup;
