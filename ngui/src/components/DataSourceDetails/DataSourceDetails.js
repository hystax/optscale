import React from "react";
import { Stack } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import SummaryList from "components/SummaryList";
import { ALIBABA_CNR, AWS_CNR, AZURE_CNR, GCP_CNR, KUBERNETES_CNR } from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import { K8sHelp } from "./Help";
import { AlibabaProperties, AwsProperties, AzureProperties, GcpProperties, K8sProperties } from "./Properties";

const DataSourceDetails = ({ id, accountId, type, config = {} }) => {
  const Properties = {
    [AWS_CNR]: AwsProperties,
    [AZURE_CNR]: AzureProperties,
    [GCP_CNR]: GcpProperties,
    [ALIBABA_CNR]: AlibabaProperties,
    [KUBERNETES_CNR]: K8sProperties
  }[type];

  const Help = {
    [KUBERNETES_CNR]: K8sHelp
  }[type];

  return (
    <Stack spacing={SPACING_2}>
      {Properties && (
        <div>
          <SummaryList
            titleMessage={<FormattedMessage id="properties" />}
            items={<Properties config={config} accountId={accountId} id={id} />}
          />
        </div>
      )}
      {Help && (
        <div>
          <Help />
        </div>
      )}
    </Stack>
  );
};

DataSourceDetails.propTypes = {
  type: PropTypes.oneOf([AWS_CNR, AZURE_CNR, GCP_CNR, ALIBABA_CNR, KUBERNETES_CNR]),
  config: PropTypes.object,
  accountId: PropTypes.string,
  id: PropTypes.string
};

export default DataSourceDetails;
