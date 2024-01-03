import React from "react";
import { Box, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import DatasetName from "components/DatasetName/DatasetName";
import LabelChip from "components/LabelChip";
import TextWithDataTestId from "components/TextWithDataTestId";
import { SPACING_1 } from "utils/layouts";

const dataset = ({ id, accessorFn, accessorKey }) => ({
  id,
  accessorFn,
  accessorKey,
  header: (
    <TextWithDataTestId dataTestId="lbl_dataset">
      <FormattedMessage id="dataset" />
    </TextWithDataTestId>
  ),
  searchFn: (_, filterValue, { row }) => {
    const search = filterValue.toLocaleLowerCase();

    const { dataset: rowDataset } = row.original;

    const { name, path, labels = [] } = rowDataset;

    return [name, path, labels.join(" ")].some((str) => str.toLocaleLowerCase().includes(search));
  },
  cell: ({ row: { original } }) => {
    const { dataset: rowDataset } = original;

    const { name, deleted, path, labels = [] } = rowDataset;

    return (
      <>
        <Typography noWrap>{<DatasetName name={name} deleted={deleted} />}</Typography>
        <Typography gutterBottom>{path}</Typography>
        <Box display="flex" gap={SPACING_1} flexWrap="wrap">
          {labels.map((label) => (
            <LabelChip key={label} label={label} />
          ))}
        </Box>
      </>
    );
  }
});

export default dataset;
