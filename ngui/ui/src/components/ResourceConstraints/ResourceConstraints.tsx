import Grid from "@mui/material/Grid";
import Link from "@mui/material/Link";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import EnabledConstraints from "components/EnabledConstraints";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import ResourceLink from "components/ResourceLink";
import ResourceConstraintContainer from "containers/ResourceConstraintContainer";
import ResourceLimitHitsContainer from "containers/ResourceLimitHitsContainer";
import { DOCS_HYSTAX_RESOURCE_CONSTRAINTS, CLUSTER_TYPES } from "urls";
import { RESOURCE_PAGE_TABS } from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import useStyles from "./ResourceConstraints.styles";

const linkRender = (chunks) => (
  <Link href={DOCS_HYSTAX_RESOURCE_CONSTRAINTS} data-test-id="link_help" target="_blank" rel="noopener">
    {chunks}
  </Link>
);

const BillingOnly = () => (
  <Grid item xs={12}>
    <InlineSeverityAlert
      messageId="resourceConstraintsBillingOnlyDescription"
      messageValues={{
        link: linkRender
      }}
    />
  </Grid>
);

const CommonConstraints = ({ poolId, resourceId, constraints, poolPolicies, isLoading, employeeId }) => {
  const { classes } = useStyles();
  return (
    <EnabledConstraints
      render={(type) => (
        <div className={classes.constraintWrapper}>
          <ResourceConstraintContainer
            poolId={poolId}
            resourceId={resourceId}
            constraint={constraints[type]}
            poolPolicy={poolPolicies[type]}
            isLoading={isLoading}
            constraintType={type}
            employeeId={employeeId}
          />
        </div>
      )}
    />
  );
};

const ResourceConstraints = ({
  resourceId,
  poolId,
  constraints,
  poolPolicies,
  employeeId,
  clusterId,
  isLoading,
  billingOnly = false,
  isResourceActive
}) => {
  const renderCommonConstraintsContent = () => (
    <Grid container spacing={SPACING_2}>
      <Grid item xs={12}>
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
      </Grid>
      {isResourceActive && (
        <Grid item xs={12} data-test-id="p_info">
          <InlineSeverityAlert
            messageId="resourceConstraintsDescription"
            messageValues={{
              link: linkRender
            }}
          />
        </Grid>
      )}
      <Grid item xs={12}>
        <ResourceLimitHitsContainer resourceId={resourceId} />
      </Grid>
    </Grid>
  );

  const renderClusterDependentConstraintsContent = () => (
    <Grid item xs={12}>
      <InlineSeverityAlert
        messageId="resourceIsPartOfClusterPleaseCheckClustersPage"
        messageDataTestId="p_cluster_part"
        messageValues={{
          link: (chunks) => (
            <ResourceLink resourceId={clusterId} tabName={RESOURCE_PAGE_TABS.CONSTRAINTS} dataTestId="link_cluster">
              {chunks}
            </ResourceLink>
          ),
          pageLink: (chunks) => (
            <Link to={CLUSTER_TYPES} component={RouterLink}>
              {chunks}
            </Link>
          )
        }}
      />
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
        <InlineSeverityAlert
          messageId="resourceTrackingStatus"
          messageDataTestId="p_tracking_status"
          messageValues={{
            status: <FormattedMessage id={billingOnly ? "billingOnly" : "active"} />,
            strong: (chunks) => <strong>{chunks}</strong>
          }}
        />
      </Grid>
      <Grid item xs={12}>
        {renderResourceConstraintContent()}
      </Grid>
    </Grid>
  );
};

export default ResourceConstraints;
