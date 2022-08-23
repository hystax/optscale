import React from "react";
import Grid from "@mui/material/Grid";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import EnabledConstraints from "components/EnabledConstraints";
import KeyValueLabel from "components/KeyValueLabel";
import ResourceLink from "components/ResourceLink";
import ResourceConstraintContainer from "containers/ResourceConstraintContainer";
import ResourceLimitHitsContainer from "containers/ResourceLimitHitsContainer";
import { DOCS_HYSTAX_RESOURCE_CONSTRAINTS, CLUSTER_TYPES } from "urls";
import { RESOURCE_PAGE_TABS } from "utils/constants";
import { SPACING_2 } from "utils/layouts";

const GetMoreHelp = () => (
  <Typography>
    <FormattedMessage
      id="linkedText"
      values={{
        text: <FormattedMessage id="getMoreHelp" />,
        link: (chunks) => (
          <Link href={DOCS_HYSTAX_RESOURCE_CONSTRAINTS} data-test-id="link_help" target="_blank" rel="noopener">
            {chunks}
          </Link>
        )
      }}
    />
  </Typography>
);

const BillingOnly = () => (
  <Grid item xs={12}>
    <Typography variant="body2">
      <FormattedMessage id="resourceConstraintsBillingOnlyDescription" />
    </Typography>
    <GetMoreHelp />
  </Grid>
);

const CommonConstraints = ({ poolId, resourceId, constraints, poolPolicies, isLoading, employeeId }) => (
  <>
    <Grid item xs={12} data-test-id="p_info">
      <Typography variant="body2">
        <FormattedMessage id="resourceConstraintsDescription1" />
      </Typography>
      <Typography variant="body2">
        <FormattedMessage id="resourceConstraintsDescription2" />
      </Typography>
      <GetMoreHelp />
    </Grid>
    <EnabledConstraints
      render={(type) => (
        <Grid item>
          <ResourceConstraintContainer
            poolId={poolId}
            resourceId={resourceId}
            constraint={constraints[type]}
            poolPolicy={poolPolicies[type]}
            isLoading={isLoading}
            constraintType={type}
            employeeId={employeeId}
          />
        </Grid>
      )}
    />
  </>
);

const ResourceConstraints = ({
  resourceId,
  poolId,
  constraints,
  poolPolicies,
  employeeId,
  clusterId,
  isLoading,
  billingOnly = false
}) => {
  const renderCommonConstraintsContent = () => (
    <>
      {billingOnly ? (
        <BillingOnly />
      ) : (
        <CommonConstraints
          poolId={poolId}
          resourceId={resourceId}
          constraints={constraints}
          poolPolicies={poolPolicies}
          isLoading={isLoading}
          employeeId={employeeId}
        />
      )}
      <Grid item xs={12}>
        <ResourceLimitHitsContainer resourceId={resourceId} />
      </Grid>
    </>
  );

  const renderClusterDependentConstraintsContent = () => (
    <Grid item xs={12}>
      <Typography data-test-id="p_cluster_part">
        <FormattedMessage
          id="resourceIsPartOfCluster"
          values={{
            link: (chunks) => (
              <ResourceLink resourceId={clusterId} tabName={RESOURCE_PAGE_TABS.CONSTRAINTS} dataTestId="link_cluster">
                {chunks}
              </ResourceLink>
            )
          }}
        />{" "}
        <FormattedMessage
          id="checkClusterPage"
          values={{
            link: (chunks) => (
              <Link to={CLUSTER_TYPES} component={RouterLink}>
                {chunks}
              </Link>
            )
          }}
        />
      </Typography>
    </Grid>
  );

  const renderResourceConstraintContent = () => {
    // if clusterId exists => this resource is a sub resource of a cluster
    if (clusterId) {
      return renderClusterDependentConstraintsContent();
    }
    return renderCommonConstraintsContent();
  };

  return (
    <Grid container direction="row" justifyContent="flex-start" spacing={SPACING_2}>
      <Grid item xs={12}>
        <KeyValueLabel
          data-test-id="p_tracking_status"
          messageId="resourceTrackingStatus"
          value={<FormattedMessage id={billingOnly ? "billingOnly" : "active"} />}
        />
      </Grid>
      {renderResourceConstraintContent()}
    </Grid>
  );
};

ResourceConstraints.propTypes = {
  poolId: PropTypes.string,
  constraints: PropTypes.object,
  poolPolicies: PropTypes.object,
  resourceId: PropTypes.string,
  employeeId: PropTypes.string,
  billingOnly: PropTypes.bool,
  isLoading: PropTypes.bool,
  clusterId: PropTypes.string
};

export default ResourceConstraints;
