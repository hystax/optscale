import React, { useState } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import { FormControl } from "@mui/material";
import PropTypes from "prop-types";
import { v4 as uuidv4 } from "uuid";
import Button from "components/Button";
import UpdateEnvironmentPropertiesFormContainer from "containers/UpdateEnvironmentPropertiesFormContainer";

const CreateEnvironmentProperties = ({ environmentId, existingProperties }) => {
  const [createFormContainers, setCreateFormContainers] = useState([]);

  const removeContainer = (containerId) =>
    setCreateFormContainers((currentContainer) => currentContainer.filter(({ id }) => id !== containerId));

  const addContainer = () => {
    setCreateFormContainers((currentContainers) => {
      const containerId = uuidv4();
      return [
        ...currentContainers,
        {
          id: containerId,
          container: (
            <UpdateEnvironmentPropertiesFormContainer
              key={containerId}
              environmentId={environmentId}
              defaultPropertyName=""
              defaultPropertyValue=""
              onSuccess={() => removeContainer(containerId)}
              onCancel={() => removeContainer(containerId)}
              existingProperties={existingProperties}
            />
          )
        }
      ];
    });
  };

  return (
    <>
      {createFormContainers.map(({ container }) => container)}
      <FormControl fullWidth>
        <Button
          dashedBorder
          startIcon={<AddOutlinedIcon />}
          messageId="addProperty"
          size="medium"
          color="primary"
          onClick={addContainer}
        />
      </FormControl>
    </>
  );
};

CreateEnvironmentProperties.propTypes = {
  environmentId: PropTypes.string.isRequired,
  existingProperties: PropTypes.object.isRequired
};

export default CreateEnvironmentProperties;
