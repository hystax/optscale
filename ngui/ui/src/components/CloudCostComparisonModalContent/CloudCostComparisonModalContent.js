import React, { useMemo } from "react";
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
import { isEmpty as isEmptyArray } from "utils/arrays";
import { FORMATTED_MONEY_TYPES } from "utils/constants";

const getSizeAccessor = (size) => size.id.replace(/\./g, "_");

const INDICATOR_ACCESSOR_KEY = "indicatorName";

const ComparisonTable = ({ sizes }) => {
  const intl = useIntl();
  const moneyFormatter = useMoneyFormatter();

  const { removeSize } = useSelectionActions();

  const columns = useMemo(
    () => [
      {
        header: "",
        accessorKey: INDICATOR_ACCESSOR_KEY,
        cell: ({ cell }) => <strong>{cell.getValue()}</strong>,
        enableSorting: false
      },
      ...sizes.map((size) => ({
        header: (
          <Box display="flex">
            <CloudLabel name={size.name} type={size.cloud_type} disableLink />
            <Tooltip title={<FormattedMessage id="removeFromComparison" />}>
              <IconButton onClick={() => removeSize(size)} icon={<PlaylistRemoveOutlinedIcon />} />
            </Tooltip>
          </Box>
        ),
        accessorKey: getSizeAccessor(size),
        enableSorting: false
      }))
    ],
    [removeSize, sizes]
  );

  const tableData = useMemo(() => {
    const getRowData = ({ indicatorMessageId, accessor }) => {
      const flavorData = Object.fromEntries(
        sizes.map((flavor) => [getSizeAccessor(flavor), typeof accessor === "function" ? accessor(flavor) : flavor[accessor]])
      );

      return {
        [INDICATOR_ACCESSOR_KEY]: intl.formatMessage({ id: indicatorMessageId }),
        ...flavorData
      };
    };

    return [
      getRowData({
        indicatorMessageId: "cpu",
        accessor: "cpu"
      }),
      getRowData({
        indicatorMessageId: "ram",
        accessor: "ram"
      }),
      getRowData({
        indicatorMessageId: "cost",
        accessor: (flavor) =>
          intl.formatMessage(
            { id: "valuePerHour" },
            {
              value: moneyFormatter(FORMATTED_MONEY_TYPES.TINY, flavor.cost, {
                format: flavor.currency,
                maximumFractionDigits: 20
              })
            }
          )
      }),
      getRowData({
        indicatorMessageId: "location",
        accessor: "location"
      }),
      getRowData({
        indicatorMessageId: "instanceFamily",
        accessor: "instance_family"
      })
    ];
  }, [intl, moneyFormatter, sizes]);

  return <Table columns={columns} data={tableData} />;
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
