import Link from "@mui/material/Link";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import ClusterTypesTable from "components/ClusterTypesTable";
import PageContentDescription from "components/PageContentDescription/PageContentDescription";
import PageContentWrapper from "components/PageContentWrapper";
import { DOCS_HYSTAX_CLUSTERS, RESOURCES } from "urls";

const actionBarDefinition = {
  breadcrumbs: [
    <Link key={1} to={RESOURCES} component={RouterLink}>
      <FormattedMessage id="resources" />
    </Link>,
  ],
  title: {
    text: <FormattedMessage id="clusterTypesTitle" />,
    dataTestId: "lbl_cluster_types",
  },
};

const ClusterTypes = ({ clusterTypes, onUpdatePriority, isLoading = false }) => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <ClusterTypesTable clusterTypes={clusterTypes} onUpdatePriority={onUpdatePriority} isLoading={isLoading} />
      <PageContentDescription
        position="bottom"
        alertProps={{
          messageId: "clusterTypesDescription",
          messageDataTestId: "p_clusters_list",
          messageValues: {
            link: (chunks) => (
              <Link data-test-id="link_read_more" href={DOCS_HYSTAX_CLUSTERS} target="_blank" rel="noopener">
                {chunks}
              </Link>
            ),
          },
        }}
      />
    </PageContentWrapper>
  </>
);

export default ClusterTypes;
