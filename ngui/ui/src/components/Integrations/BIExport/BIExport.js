import React from "react";
import HiveIcon from "@mui/icons-material/Hive";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import TextBlock from "components/TextBlock";
import { BI_EXPORTS } from "urls";
import Integration from "../Integration";
import Title from "../Title";

export const BI_EXPORT = "biExport";

const BIExport = ({ isLoading, exportsCount }) => (
  <Integration
    id={BI_EXPORT}
    title={<Title icon={<HiveIcon color="primary" />} label={<FormattedMessage id="biExportTitle" />} />}
    button={<Button messageId="seeBIExports" color="primary" link={BI_EXPORTS} />}
    blocks={[
      <TextBlock key="description1" messageId="biExportsDescription" />,
      <TextBlock
        isLoading={isLoading}
        key="description2"
        messageId="numberOfBIExports"
        values={{
          number: exportsCount,
          strong: (chunks) => <strong>{chunks}</strong>
        }}
      />
    ]}
  />
);

export default BIExport;
