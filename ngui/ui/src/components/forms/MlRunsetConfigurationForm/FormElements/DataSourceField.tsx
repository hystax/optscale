import { Selector } from "components/forms/common/fields";
import { ItemContentWithDataSourceIcon } from "components/Selector";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.DATA_SOURCE;

const LABEL_ID = "dataSource";

const DataSourceField = ({ dataSources, isLoading = false }) => (
  <Selector
    name={FIELD_NAME}
    id="data-source-selector"
    fullWidth
    required
    labelMessageId={LABEL_ID}
    isLoading={isLoading}
    items={dataSources.map(({ id, name, type }) => ({
      value: id,
      content: <ItemContentWithDataSourceIcon dataSourceType={type}>{name}</ItemContentWithDataSourceIcon>
    }))}
  />
);

export default DataSourceField;
