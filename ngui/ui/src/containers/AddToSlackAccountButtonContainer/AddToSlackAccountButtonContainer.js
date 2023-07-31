import React from "react";
import ButtonLoader from "components/ButtonLoader";
import SlackIcon from "icons/SlackIcon";
import SlackInstallationPathService from "services/SlackInstallationPathService";

const AddToSlackAccountButtonContainer = () => {
  const { useGet } = SlackInstallationPathService();

  const { isLoading, url } = useGet();

  return (
    <ButtonLoader
      isLoading={isLoading}
      startIcon={<SlackIcon />}
      color="primary"
      variant="outlined"
      href={url}
      messageId="addToSlack"
    />
  );
};

export default AddToSlackAccountButtonContainer;
