import React, { useMemo } from "react";
import ExitToAppOutlinedIcon from "@mui/icons-material/ExitToAppOutlined";
import { Box } from "@mui/material";
import List from "@mui/material/List";
import ListItemText from "@mui/material/ListItemText";
import MenuItem from "@mui/material/MenuItem";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import DashedTypography from "components/DashedTypography";
import FormattedMoney from "components/FormattedMoney";
import IconButton from "components/IconButton";
import Popover from "components/Popover";
import ResourceCell from "components/ResourceCell";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import Tooltip from "components/Tooltip";
import WrapperCard from "components/WrapperCard";
import { useOrganizationPerspectives } from "hooks/useOrganizationPerspectives";
import { getLast30DaysResourcesUrl, getResourcesExpensesUrl, RESOURCE_PERSPECTIVES } from "urls";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { sliceByLimitWithEllipsis } from "utils/strings";
import { RESOURCE_ID_COLUMN_CELL_STYLE } from "utils/tables";

const PERSPECTIVE_NAME_SLICE_THRESHOLD = 30;

const PerspectiveMenuItem = ({ perspectiveName }) => {
  const navigate = useNavigate();

  const onClick = () => navigate(getResourcesExpensesUrl({ perspective: perspectiveName }));

  return perspectiveName.length > PERSPECTIVE_NAME_SLICE_THRESHOLD ? (
    <Tooltip key={perspectiveName} title={perspectiveName}>
      <MenuItem onClick={onClick}>
        <ListItemText primary={sliceByLimitWithEllipsis(perspectiveName, PERSPECTIVE_NAME_SLICE_THRESHOLD)} />
      </MenuItem>
    </Tooltip>
  ) : (
    <MenuItem key={perspectiveName} onClick={onClick}>
      <ListItemText primary={perspectiveName} />
    </MenuItem>
  );
};

const TopResourcesExpensesCard = ({ cleanExpenses, isLoading }) => {
  const navigate = useNavigate();

  const { validPerspectives } = useOrganizationPerspectives();
  const perspectiveNames = Object.keys(validPerspectives);
  const hasPerspectives = !isEmptyArray(perspectiveNames);

  const goToResources = () => navigate(getLast30DaysResourcesUrl());

  const tableData = useMemo(
    () =>
      cleanExpenses.map((cleanExpense) => ({
        ...cleanExpense,
        resource: [cleanExpense.cloud_resource_id, cleanExpense.cloud_resource_hash, cleanExpense.resource_name]
          .filter(Boolean)
          .join(" ")
      })),
    [cleanExpenses]
  );

  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="block_top_expenses_lbl_resource">
            <FormattedMessage id="resource" />
          </TextWithDataTestId>
        ),
        accessorKey: "resource",
        style: RESOURCE_ID_COLUMN_CELL_STYLE,
        cell: ({ row: { original, index } }) => (
          <ResourceCell
            disableActivityIcon
            disableConstraintViolationIcon
            rowData={original}
            dataTestIds={{ labelIds: { label: `block_top_expenses_link_resource_${index}` } }}
          />
        )
      },
      {
        header: (
          <TextWithDataTestId dataTestId="block_top_expenses_lbl_expenses">
            <FormattedMessage id="expenses" />
          </TextWithDataTestId>
        ),
        accessorKey: "cost",
        cell: ({ row: { original } }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={original.cost} />,
        defaultSort: "desc"
      }
    ],
    []
  );

  return (
    <WrapperCard
      needAlign
      title={
        <Box display="flex" alignItems="center">
          <Box mr={0.5}>
            <FormattedMessage id="topResourcesExpenses" />
          </Box>
          <Box display="flex" mr={hasPerspectives ? 0.5 : 0}>
            <IconButton
              icon={<ExitToAppOutlinedIcon />}
              tooltip={{
                show: true,
                messageId: "goToResources"
              }}
              onClick={goToResources}
              isLoading={isLoading}
              dataTestId="btn_go_to_resources"
            />
          </Box>
          {hasPerspectives && (
            <Popover
              label={
                <DashedTypography component="div">
                  <FormattedMessage id="perspectives" />
                </DashedTypography>
              }
              anchorOrigin={{
                vertical: "bottom",
                horizontal: "left"
              }}
              transformOrigin={{
                vertical: "top",
                horizontal: "left"
              }}
              menu={
                <List>
                  {[
                    ...perspectiveNames.map((name) => <PerspectiveMenuItem key={name} perspectiveName={name} />),
                    <MenuItem key="seeAllPerspectives" onClick={() => navigate(RESOURCE_PERSPECTIVES)}>
                      <ListItemText primary={<FormattedMessage id="seeAllPerspectives" />} />
                    </MenuItem>
                  ]}
                </List>
              }
            />
          )}
        </Box>
      }
      titleCaption={<FormattedMessage id="lastValueDays" values={{ value: 30 }} />}
      dataTestIds={{
        wrapper: "block_top_resources",
        title: "lbl_top_resources",
        titleCaption: "p_last_30_days"
      }}
      elevation={0}
    >
      {isLoading ? (
        <TableLoader columnsCounter={columns.length} showHeader />
      ) : (
        <Table data={tableData} columns={columns} localization={{ emptyMessageId: "noResources" }} />
      )}
    </WrapperCard>
  );
};

TopResourcesExpensesCard.propTypes = {
  cleanExpenses: PropTypes.array.isRequired,
  isLoading: PropTypes.bool
};

export default TopResourcesExpensesCard;
