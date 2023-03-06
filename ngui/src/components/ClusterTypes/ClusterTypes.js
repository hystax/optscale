import React from "react";
import Grid from "@mui/material/Grid";
import Link from "@mui/material/Link";
import PropTypes from "prop-types";
import ActionBar from "components/ActionBar";
import ClusterTypesTable from "components/ClusterTypesTable";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import PageContentWrapper from "components/PageContentWrapper";
import { DOCS_HYSTAX_CLUSTERS } from "urls";
import { SPACING_2 } from "utils/layouts";

const actionBarDefinition = {
  title: {
    messageId: "clusterTypesTitle",
    dataTestId: "lbl_cluster_types"
  }
};

const ExplanationMessage = () => (
  <InlineSeverityAlert
    messageId="clusterTypesDescription"
    messageDataTestId="p_clusters_list"
    messageValues={{
      link: (chunks) => (
        <Link data-test-id="link_read_more" href={DOCS_HYSTAX_CLUSTERS} target="_blank" rel="noopener">
          {chunks}
        </Link>
      )
    }}
  />
);

const ClusterTypes = ({ clusterTypes, onUpdatePriority, isLoading = false }) => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <Grid container spacing={SPACING_2}>
        <Grid item xs={12}>
          <ClusterTypesTable clusterTypes={clusterTypes} onUpdatePriority={onUpdatePriority} isLoading={isLoading} />
        </Grid>
        <Grid item xs={12}>
          <ExplanationMessage />
        </Grid>
      </Grid>
    </PageContentWrapper>
  </>
);

ClusterTypes.propTypes = {
  clusterTypes: PropTypes.array.isRequired,
  onUpdatePriority: PropTypes.func,
  isLoading: PropTypes.bool
};

export default ClusterTypes;
