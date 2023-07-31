import React from "react";
import { FormattedMessage } from "react-intl";
import CloudLabel from "components/CloudLabel";
import TextWithDataTestId from "components/TextWithDataTestId";

const dataSource = () => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_data_source">
      <FormattedMessage id="dataSource" />
    </TextWithDataTestId>
  ),
  accessorKey: "cloud_account_name",
  cell: ({
    row: {
      original: { cloud_account_id: id, cloud_account_name: name, cloud_account_type: type }
    }
  }) => <CloudLabel id={id} name={name} type={type} />,
  footer: () => <FormattedMessage id="total" />
});

export default dataSource;
