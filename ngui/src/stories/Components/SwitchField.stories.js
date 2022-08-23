import React from "react";
import { boolean, text } from "@storybook/addon-knobs";
import PropTypes from "prop-types";
import { useForm } from "react-hook-form";
import QuestionMark from "components/QuestionMark";
import SwitchField from "components/SwitchField";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/SwitchField`
};

const Component = ({ labelMessageId, endAdornment }) => {
  const { control } = useForm();
  return (
    <SwitchField
      name="name"
      defaultValue={false}
      labelMessageId={labelMessageId}
      control={control}
      endAdornment={endAdornment}
    />
  );
};

export const withKnobs = () => (
  <Component
    labelMessageId={text("labelMessageId", "name")}
    endAdornment={
      boolean("render endAdornment", false) ? (
        <QuestionMark
          messageId="costAndUsageReportDetectionTooltip"
          messageValues={{
            break: <br />
          }}
        />
      ) : null
    }
  />
);

Component.propTypes = {
  defaultValue: PropTypes.bool.isRequired,
  labelMessageId: PropTypes.string.isRequired,
  endAdornment: PropTypes.node
};
