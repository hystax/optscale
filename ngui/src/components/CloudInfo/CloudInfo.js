import React from "react";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import KeyValueLabel from "components/KeyValueLabel";
import { useDataSources } from "hooks/useDataSources";
import { AWS_CNR, KUBERNETES_CNR } from "utils/constants";
import { getTimeDistance } from "utils/datetime";

const getAwsAccountType = (isLinked) => (isLinked ? "linked" : "root");

const AwsSpecificInfo = ({ linked }) => (
  <ListItem>
    <ListItemText
      primary={<KeyValueLabel value={<FormattedMessage id={getAwsAccountType(linked)} />} messageId="awsAccountType" />}
    />
  </ListItem>
);

const KubernetesSpecificInfo = ({ url, port, user }) => (
  <>
    <ListItem>
      <ListItemText
        primary={<KeyValueLabel value={url} messageId="url" dataTestIds={{ key: "p_url", value: "value_url" }} />}
      />
    </ListItem>
    <ListItem>
      <ListItemText
        primary={<KeyValueLabel value={port} messageId="port" dataTestIds={{ key: "p_port", value: "value_port" }} />}
      />
    </ListItem>
    <ListItem>
      <ListItemText
        primary={<KeyValueLabel value={user} messageId="user" dataTestIds={{ key: "p_user", value: "value_user" }} />}
      />
    </ListItem>
  </>
);

const getRenderCloudSpecificInfoFunction = (type) =>
  ({
    [AWS_CNR]: ({ linked }) => <AwsSpecificInfo linked={linked || false} />,
    [KUBERNETES_CNR]: ({ url, port, user }) => <KubernetesSpecificInfo user={user} url={url} port={port} />
  }[type]);

const CloudInfo = ({ accountId, lastImportAt, type, config = {} }) => {
  const renderCloudSpecificInfo = getRenderCloudSpecificInfoFunction(type);

  const {
    cloudInfoMessageId,
    dataTestIds: { infoKey: infoKeyDataTestId, infoValue: infoValueDataTestId }
  } = useDataSources(type);
  const dataSourceInfoDataTestIds = { key: infoKeyDataTestId, value: infoValueDataTestId };

  return (
    <List>
      {accountId && cloudInfoMessageId ? (
        <ListItem>
          <ListItemText
            primary={<KeyValueLabel value={accountId} messageId={cloudInfoMessageId} dataTestIds={dataSourceInfoDataTestIds} />}
          />
        </ListItem>
      ) : null}
      {typeof renderCloudSpecificInfo === "function" && renderCloudSpecificInfo(config)}
      <ListItem>
        <ListItemText
          primary={
            <KeyValueLabel
              value={
                <FormattedMessage
                  id={!lastImportAt ? "never" : "valueAgo"}
                  values={{
                    value: lastImportAt ? getTimeDistance(lastImportAt) : null
                  }}
                />
              }
              messageId="lastBillingReportProcessed"
              dataTestIds={{ key: "p_report", value: "value_report" }}
            />
          }
        />
      </ListItem>
    </List>
  );
};

AwsSpecificInfo.propTypes = {
  linked: PropTypes.bool.isRequired
};

CloudInfo.propTypes = {
  type: PropTypes.string.isRequired,
  lastImportAt: PropTypes.number.isRequired,
  config: PropTypes.object.isRequired,
  accountId: PropTypes.string
};

export default CloudInfo;
