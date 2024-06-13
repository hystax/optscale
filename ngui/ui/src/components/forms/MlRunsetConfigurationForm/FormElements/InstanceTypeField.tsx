import { Selector } from "components/forms/common/fields";
import { ItemContentWithDataSourceIcon } from "components/Selector";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.INSTANCE_TYPE;

const LABEL_ID = "instanceType";

const InstanceTypeField = ({ instanceTypes, isLoading = false }) => (
  <Selector
    name={FIELD_NAME}
    id="instance-type-selector"
    fullWidth
    required
    labelMessageId={LABEL_ID}
    isLoading={isLoading}
    items={instanceTypes.map(({ name, cloud_type: dataSourceType }) => ({
      value: name,
      content: <ItemContentWithDataSourceIcon dataSourceType={dataSourceType}>{name}</ItemContentWithDataSourceIcon>
    }))}
  />
);

export default InstanceTypeField;
