import React from "react";
import Grid from "@mui/material/Grid";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import ActionBar from "components/ActionBar";
import ClusterTypesTable from "components/ClusterTypesTable";
import PageContentWrapper from "components/PageContentWrapper";
import WrapperCard from "components/WrapperCard";
import { DOCS_HYSTAX_CLUSTERS } from "urls";
import { SPACING_2 } from "utils/layouts";

const actionBarDefinition = {
  goBack: true,
  title: {
    messageId: "clusterTypesTitle",
    dataTestId: "lbl_cluster_types"
  }
};

const ExplanationMessage = () => (
  <Typography data-test-id="p_clusters_list">
    <FormattedMessage
      id="clusterTypesDescription"
      values={{
        link: (chunks) => (
          <Link data-test-id="link_read_more" href={DOCS_HYSTAX_CLUSTERS} target="_blank" rel="noopener">
            {chunks}
          </Link>
        )
      }}
    />
  </Typography>
);

const ClusterTypes = ({ clusterTypes, onUpdatePriority, isLoading = false }) => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <WrapperCard>
        <Grid container spacing={SPACING_2}>
          <Grid item xs={12}>
            <ExplanationMessage />
          </Grid>
          <Grid item xs={12}>
            <ClusterTypesTable clusterTypes={clusterTypes} onUpdatePriority={onUpdatePriority} isLoading={isLoading} />
          </Grid>
        </Grid>
      </WrapperCard>
    </PageContentWrapper>
  </>
);

ClusterTypes.propTypes = {
  clusterTypes: PropTypes.array.isRequired,
  onUpdatePriority: PropTypes.func,
  isLoading: PropTypes.bool
};

export default ClusterTypes;
