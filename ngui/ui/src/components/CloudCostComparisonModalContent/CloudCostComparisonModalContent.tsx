import { useMemo } from "react";
import PlaylistRemoveOutlinedIcon from "@mui/icons-material/PlaylistRemoveOutlined";
import { Box, Typography } from "@mui/material";
import { FormattedMessage, useIntl } from "react-intl";
import Button from "components/Button";
import CloudLabel from "components/CloudLabel";
import { useMoneyFormatter } from "components/FormattedMoney";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import IconButton from "components/IconButton";
import Table from "components/Table";
import Tooltip from "components/Tooltip";
import { useSelectedSizes, useSelectionActions } from "reducers/cloudCostComparisonSelectedSizes/hooks";
import { isEmptyArray } from "utils/arrays";
import { FORMATTED_MONEY_TYPES } from "utils/constants";

const ComparisonTable = ({ sizes }) => {
  const intl = useIntl();
  const moneyFormatter = useMoneyFormatter();
  const { removeSize } = useSelectionActions();

  const columns = useMemo(
    () => [
      {
        header: "",
        id: "size",
        cell: ({ row }) => (
          <Box display="flex" alignItems="center">
            <CloudLabel name={row.original.name} type={row.original.cloud_type} disableLink />
            <Tooltip title={<FormattedMessage id="removeFromComparison" />}>
              <IconButton onClick={() => removeSize(row.original)} icon={<PlaylistRemoveOutlinedIcon />} />
            </Tooltip>
          </Box>
        ),
        enableSorting: false,
      },
      {
        header: intl.formatMessage({ id: "cpu" }),
        accessorKey: "cpu",
        cell: ({ row }) => row.original.cpu,
        enableSorting: false,
      },
      {
        header: intl.formatMessage({ id: "ram" }),
        accessorKey: "ram",
        cell: ({ row }) => row.original.ram,
        enableSorting: false,
      },
      {
        header: intl.formatMessage({ id: "cost" }),
        accessorKey: "cost",
        cell: ({ row }) =>
          intl.formatMessage(
            { id: "valuePerHour" },
            {
              value: moneyFormatter(FORMATTED_MONEY_TYPES.TINY, row.original.cost, {
                format: row.original.currency,
              }),
            }
          ),
        defaultSort: "desc",
      },
      {
        header: intl.formatMessage({ id: "location" }),
        accessorKey: "location",
        cell: ({ row }) => row.original.location,
        enableSorting: false,
      },
      {
        header: intl.formatMessage({ id: "instanceFamily" }),
        accessorKey: "instance_family",
        cell: ({ row }) => row.original.instance_family,
        enableSorting: false,
      },
    ],
    [intl, moneyFormatter, removeSize]
  );

  return (
    <Table
      columns={columns}
      data={sizes}
      counters={{
        show: false,
      }}
    />
  );
};

const CloudCostComparisonModalContent = ({ onClose }) => {
  const selectedSizes = useSelectedSizes();

  return (
    <>
      {isEmptyArray(selectedSizes) ? (
        <Typography>
          <FormattedMessage id="selectSizesToCompare" />
        </Typography>
      ) : (
        <ComparisonTable sizes={selectedSizes} />
      )}
      <FormButtonsWrapper>
        <Button messageId="close" color="primary" dataTestId="btn_cancel" onClick={onClose} />
      </FormButtonsWrapper>
    </>
  );
};

export default CloudCostComparisonModalContent;
