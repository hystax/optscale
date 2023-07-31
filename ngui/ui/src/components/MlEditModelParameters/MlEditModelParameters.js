import React from "react";
import { Stack } from "@mui/material";
import PropTypes from "prop-types";
import ContentBackdropLoader from "components/ContentBackdropLoader";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import { SPACING_2 } from "utils/layouts";
import MlModelParametersTable from "./MlModelParametersTable";

const MlEditModelParameters = ({ parameters, onAttachChange, isLoading = false, isUpdateLoading = false }) => (
  <Stack spacing={SPACING_2}>
    <ContentBackdropLoader isLoading={isUpdateLoading}>
      <MlModelParametersTable parameters={parameters} isLoading={isLoading} onAttachChange={onAttachChange} />
    </ContentBackdropLoader>
    <InlineSeverityAlert messageId="mlModelSpecificParametersDescription" />
  </Stack>
);

MlEditModelParameters.propTypes = {
  parameters: PropTypes.array.isRequired,
  onAttachChange: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  isUpdateLoading: PropTypes.bool
};

export default MlEditModelParameters;
