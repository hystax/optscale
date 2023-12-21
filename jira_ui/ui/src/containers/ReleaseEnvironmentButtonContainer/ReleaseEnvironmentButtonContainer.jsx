import React, { useState } from "react";
import { LoadingButton } from "@atlaskit/button";
import UnlockIcon from "@atlaskit/icon/glyph/unlock";
import PropTypes from "prop-types";
import makeRequest from "utils/makeRequest";

const ReleaseEnvironmentButtonContainer = ({ activeBooking, onSuccess }) => {
  const [isLoading, setIsLoading] = useState(false);

  const onClick = () => {
    setIsLoading(true);
    makeRequest({
      url: `/jira_bus/v2/shareable_book/${activeBooking.id}`,
      options: { method: "PATCH" }
    }).then(({ error }) => {
      setIsLoading(false);
      if (!error && typeof onSuccess === "function") {
        onSuccess();
      }
    });
  };

  return (
    <LoadingButton iconBefore={<UnlockIcon label="Release icon" />} onClick={onClick} isLoading={isLoading}>
      Release environment
    </LoadingButton>
  );
};

ReleaseEnvironmentButtonContainer.propTypes = {
  activeBooking: PropTypes.object.isRequired,
  onSuccess: PropTypes.func.isRequired
};

export default ReleaseEnvironmentButtonContainer;
