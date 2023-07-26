import React from "react";
import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";

const buttonLink = ({ headerDataTestId, accessorKey, onClick }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="name" />
    </TextWithDataTestId>
  ),
  accessorKey,
  cell: (cellData) => {
    const { cell } = cellData;

    return (
      <Link
        component="button"
        style={{
          textAlign: "left"
        }}
        variant="body2"
        onClick={() => onClick(cellData)}
      >
        <FormattedMessage id={cell.getValue()} />
      </Link>
    );
  }
});

export default buttonLink;
