import React from "react";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import ActionBar from "components/ActionBar";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import K8sRightsizingTable from "components/K8sRightsizingTable";
import PageContentWrapper from "components/PageContentWrapper";
import { SPACING_2 } from "utils/layouts";

const K8sRightsizing = ({ actionBarDefinition, namespaces, isLoading = false, tableActionBarDefinition }) => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <Grid container spacing={SPACING_2}>
        <Grid item xs={12}>
          <K8sRightsizingTable
            namespaces={namespaces}
            isLoading={isLoading}
            tableActionBarDefinition={tableActionBarDefinition}
          />
        </Grid>
        <Grid item>
          <InlineSeverityAlert messageId="k8sRightsizingDescription" />
        </Grid>
      </Grid>
    </PageContentWrapper>
  </>
);
K8sRightsizing.propTypes = {
  actionBarDefinition: PropTypes.object.isRequired,
  namespaces: PropTypes.array.isRequired,
  isLoading: PropTypes.bool,
  tableActionBarDefinition: PropTypes.object
};

export default K8sRightsizing;
