import { Selector } from "components/forms/common/fields";
import { ItemContent } from "components/Selector";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.OWNER;

const MlEditTaskFormOwnerField = ({ employees = [], isLoading = false }) => (
  <Selector
    name={FIELD_NAME}
    id="owner-selector"
    fullWidth
    required
    labelMessageId="owner"
    isLoading={isLoading}
    items={employees.map(({ id, name: employeeName }) => ({
      value: id,
      content: <ItemContent>{employeeName}</ItemContent>
    }))}
  />
);

export default MlEditTaskFormOwnerField;
