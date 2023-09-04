import React, { useState } from "react";
import Select from "@atlaskit/select";
import PropTypes from "prop-types";
import IssueAttachment from "components/IssueAttachment";
import { getEnvironmentDisplayedName } from "utils/getEnvironmentDisplayName";

const IssueAttachmentsDetails = ({
  attachedEnvironments,
  isAllowedToManageAttachments = false,
  onSuccessDetachEnvironment,
  onSuccessReleaseEnvironment
}) => {
  const [selectedEnvironment, setSelectedEnvironment] = useState(attachedEnvironments[0]);

  const onChange = (item) => setSelectedEnvironment(item);
  return (
    <div>
      <div style={{ marginBottom: "8px" }}>
        <label htmlFor="environment-select">{`Associated environments (${attachedEnvironments.length})`}</label>
        <Select
          value={selectedEnvironment}
          options={attachedEnvironments}
          getOptionValue={(environment) => environment.id}
          getOptionLabel={(environment) => getEnvironmentDisplayedName(environment)}
          onChange={onChange}
          placeholder="Choose Environment"
          inputId="environment-select"
        />
      </div>
      <IssueAttachment
        environment={selectedEnvironment}
        isAllowedToManageAttachment={isAllowedToManageAttachments}
        onSuccessDetachEnvironment={onSuccessDetachEnvironment}
        onSuccessReleaseEnvironment={onSuccessReleaseEnvironment}
      />
    </div>
  );
};

IssueAttachmentsDetails.propTypes = {
  attachedEnvironments: PropTypes.array.isRequired,
  isAllowedToManageAttachments: PropTypes.bool,
  onSuccessDetachEnvironment: PropTypes.func,
  onSuccessReleaseEnvironment: PropTypes.func
};

export default IssueAttachmentsDetails;
