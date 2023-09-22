import React from "react";
import { FormattedMessage } from "react-intl";
import CloudLabel from "components/CloudLabel";
import TextWithDataTestId from "components/TextWithDataTestId";

const dataSource = ({
  accessorKey = "cloud_account_name",
  dataSourceNameAccessor = "cloud_account_name",
  dataSourceIdAccessor = "cloud_account_id",
  dataSourceTypeAccessor = "cloud_account_type"
} = {}) => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_data_source">
      <FormattedMessage id="dataSource" />
    </TextWithDataTestId>
  ),
  accessorKey,
  cell: ({
    row: {
      original: { [dataSourceIdAccessor]: id, [dataSourceNameAccessor]: name, [dataSourceTypeAccessor]: type }
    }
  }) => <CloudLabel id={id} name={name} type={type} />,
  footer: () => <FormattedMessage id="total" />
});

export default dataSource;
