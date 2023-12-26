import React from "react";
import { Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import DatasetName from "components/DatasetName/DatasetName";
import TextWithDataTestId from "components/TextWithDataTestId";

const leaderboardCriteriaDataset = ({ nameAccessor, pathAccessor, deletedAccessor }) => ({
  id: "dataset",
  accessorFn: (originalRow) => [originalRow[nameAccessor], originalRow[pathAccessor]].join(" "),
  enableSorting: false,
  header: (
    <TextWithDataTestId dataTestId="lbl_dataset">
      <FormattedMessage id="dataset" />
    </TextWithDataTestId>
  ),
  cell: ({ row: { original } }) => {
    const { [nameAccessor]: name, [pathAccessor]: path, [deletedAccessor]: deleted } = original;

    return (
      <CaptionedCell caption={path}>
        <Typography noWrap>
          <DatasetName name={name} deleted={deleted} />
        </Typography>
      </CaptionedCell>
    );
  }
});

export default leaderboardCriteriaDataset;
