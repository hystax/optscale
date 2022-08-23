import React from "react";
import { Typography } from "@mui/material";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import ActionBar from "components/ActionBar";
import K8sRightsizingTable from "components/K8sRightsizingTable";
import PageContentWrapper from "components/PageContentWrapper";
import RelativeDateTimePicker from "components/RelativeDateTimePicker";
import WrapperCard from "components/WrapperCard";
import { SPACING_2 } from "utils/layouts";

const K8sRightsizing = ({ actionBarDefinition, namespaces, applyFilter, definedRanges, isLoading = false }) => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <WrapperCard>
        <Grid container spacing={SPACING_2} justifyContent={"space-between"}>
          <Grid item>
            <Typography>
              <FormattedMessage id={"k8sRightsizingDescription"} />
            </Typography>
          </Grid>
          <Grid item>
            <RelativeDateTimePicker onChange={applyFilter} definedRanges={definedRanges} />
          </Grid>
          <Grid item xs={12}>
            <K8sRightsizingTable namespaces={namespaces} isLoading={isLoading} />
          </Grid>
        </Grid>
      </WrapperCard>
    </PageContentWrapper>
  </>
);

K8sRightsizing.propTypes = {
  actionBarDefinition: PropTypes.object.isRequired,
  namespaces: PropTypes.array.isRequired,
  applyFilter: PropTypes.func.isRequired,
  definedRanges: PropTypes.array.isRequired,
  isLoading: PropTypes.bool
};

export default K8sRightsizing;
