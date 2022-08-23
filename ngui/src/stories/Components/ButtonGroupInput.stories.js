import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import ButtonGroupInput from "components/ButtonGroupInput";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/ButtonGroupInput`
};

const AWS_ROOT_ACCOUNT = "aws";
const AZURE_SUBSCRIPTION = "azure";

const Input = () => {
  const [activeButtonIndex, setActiveButtonIndex] = useState(0);
  const [helperText, setHelperText] = useState(AWS_ROOT_ACCOUNT);

  const buttonsGroup = [
    {
      id: AWS_ROOT_ACCOUNT,
      messageId: AWS_ROOT_ACCOUNT,
      action: () => {
        setActiveButtonIndex(0);
        setHelperText(AWS_ROOT_ACCOUNT);
      }
    },
    {
      id: AZURE_SUBSCRIPTION,
      messageId: AZURE_SUBSCRIPTION,
      disabled: true,
      tooltip: "comingSoon"
    }
  ];

  return (
    <ButtonGroupInput
      labelText={<FormattedMessage id="connectionType" />}
      helperText={<FormattedMessage id={helperText} />}
      buttons={buttonsGroup}
      activeButtonIndex={activeButtonIndex}
      fullWidth
    />
  );
};

export const basic = () => {
  return <Input />;
};
