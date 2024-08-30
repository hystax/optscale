import { FormattedMessage } from "react-intl";
import { RadioGroup } from "components/forms/common/fields";
import { AWS_ROOT_CONNECT_CUR_VERSION, AWS_ROOT_CONNECT_CUR_VERSION_MESSAGE_ID } from "utils/constants";

export const FIELD_NAMES = Object.freeze({
  CUR_VERSION: "curVersion"
});

const AwsRootExportType = () => (
  <RadioGroup
    name={FIELD_NAMES.CUR_VERSION}
    defaultValue={String(AWS_ROOT_CONNECT_CUR_VERSION.CUR_2)}
    labelMessageId="exportType"
    radioButtons={[
      {
        value: String(AWS_ROOT_CONNECT_CUR_VERSION.CUR_2),
        label: <FormattedMessage id={AWS_ROOT_CONNECT_CUR_VERSION_MESSAGE_ID[AWS_ROOT_CONNECT_CUR_VERSION.CUR_2]} />
      },
      {
        value: String(AWS_ROOT_CONNECT_CUR_VERSION.CUR_1),
        label: <FormattedMessage id={AWS_ROOT_CONNECT_CUR_VERSION_MESSAGE_ID[AWS_ROOT_CONNECT_CUR_VERSION.CUR_1]} />
      }
    ]}
  />
);

export default AwsRootExportType;
