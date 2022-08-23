import React from "react";
import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import CloudResourceId from "components/CloudResourceId";
import TextWithDataTestId from "components/TextWithDataTestId";
import { RESOURCE_ID_COLUMN_CELL_STYLE } from "utils/tables";

const resource = ({ headerDataTestId, accessor = "cloud_resource_id" }) => ({
  Header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="resource" />
    </TextWithDataTestId>
  ),
  accessor,
  style: RESOURCE_ID_COLUMN_CELL_STYLE,
  Cell: ({
    row: {
      original: { resource_name: name, resource_id: id, cloud_resource_id: cloudId }
    }
  }) => (
    <CaptionedCell caption={name}>
      <CloudResourceId resourceId={id} cloudResourceId={cloudId} />
    </CaptionedCell>
  )
});

export default resource;
