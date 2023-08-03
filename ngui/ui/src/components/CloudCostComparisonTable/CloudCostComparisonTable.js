import React, { useEffect, useMemo } from "react";
import CompareOutlinedIcon from "@mui/icons-material/CompareOutlined";
import PlaylistRemoveOutlinedIcon from "@mui/icons-material/PlaylistRemoveOutlined";
import { Badge } from "@mui/material";
import Button from "components/Button";
import { CloudCostComparisonModal } from "components/SideModalManager/SideModals";
import Table from "components/Table";
import { useIsNebiusConnectionEnabled } from "hooks/useIsNebiusConnectionEnabled";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useSelectedSizes, useSelectionActions } from "reducers/cloudCostComparisonSelectedSizes/hooks";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { AWS_CNR, AZURE_CNR, NEBIUS } from "utils/constants";
import { cpu as cpuColumn, ram as ramColumn, flavors as flavorsColumn } from "./columns";

const CompareButton = () => {
  const selectedSizes = useSelectedSizes();
  const openSideModal = useOpenSideModal();

  return (
    <Badge badgeContent={selectedSizes.length} color="info">
      <Button
        messageId="compare"
        startIcon={<CompareOutlinedIcon />}
        variant="text"
        disabled={isEmptyArray(selectedSizes)}
        onClick={() => openSideModal(CloudCostComparisonModal)}
      />
    </Badge>
  );
};

const ClearSelectionButton = () => {
  const selectedSizes = useSelectedSizes();
  const { resetSelection } = useSelectionActions();

  return (
    <Button
      messageId="clearSelection"
      startIcon={<PlaylistRemoveOutlinedIcon />}
      variant="text"
      disabled={isEmptyArray(selectedSizes)}
      onClick={resetSelection}
    />
  );
};

const CloudCostComparisonTable = ({ relevantSizes, cloudProviders, errors }) => {
  const isNebiusConnectionEnabled = useIsNebiusConnectionEnabled();

  const { resetSelection } = useSelectionActions();

  useEffect(() => () => resetSelection(), [resetSelection]);

  const columns = useMemo(() => {
    const getSizesColumn = (cloudType) =>
      isEmptyArray(cloudProviders) || cloudProviders.includes(cloudType)
        ? flavorsColumn({
            cloudType,
            error: errors[cloudType]
          })
        : undefined;

    return [
      cpuColumn(),
      ramColumn(),
      getSizesColumn(AWS_CNR),
      getSizesColumn(AZURE_CNR),
      isNebiusConnectionEnabled ? getSizesColumn(NEBIUS) : undefined
    ].filter(Boolean);
  }, [cloudProviders, errors, isNebiusConnectionEnabled]);

  const tableData = useMemo(
    () =>
      relevantSizes.map(({ cpu, ram, ...cloudTypes }) => ({
        cpu,
        ram,
        ...Object.fromEntries(
          Object.entries(cloudTypes).map(([cloudType, sizes]) => [
            cloudType,
            sizes.map((size) => ({
              ...size,
              cloud_type: cloudType,
              cpu,
              ram,
              id: `${size.name}-${size.location}-${size.instance_family}-${size.cost}-${size.currency}`
            }))
          ])
        )
      })),
    [relevantSizes]
  );

  return (
    <Table
      actionBar={{
        show: true,
        definition: {
          /*
            Action bar doesn't support mobile view for "custom" items
            See OS-5925
          */
          hideItemsOnSmallScreens: false,
          items: [
            {
              key: "btn-compare",
              type: "custom",
              node: <CompareButton />
            },
            {
              key: "btn-clear-selection",
              type: "custom",
              node: <ClearSelectionButton />
            }
          ]
        }
      }}
      columns={columns}
      data={tableData}
      pageSize={50}
      localization={{ emptyMessageId: "noRelevantSizes" }}
    />
  );
};

export default CloudCostComparisonTable;
