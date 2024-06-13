import { Selector } from "components/forms/common/fields";
import { ItemContentWithDataSourceIcon } from "components/Selector";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.REGION;

const LABEL_ID = "region";

const RegionField = ({ regions, isLoading = false }) => (
  <Selector
    name={FIELD_NAME}
    id="region-selector"
    fullWidth
    required
    labelMessageId={LABEL_ID}
    isLoading={isLoading}
    items={regions.map(({ name, cloud_type: dataSourceType }) => ({
      value: name,
      content: <ItemContentWithDataSourceIcon dataSourceType={dataSourceType}>{name}</ItemContentWithDataSourceIcon>
    }))}
  />
);

export default RegionField;
