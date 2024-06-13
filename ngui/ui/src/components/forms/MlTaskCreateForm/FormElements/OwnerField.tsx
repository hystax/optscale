import { Selector } from "components/forms/common/fields";
import { ItemContent } from "components/Selector";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.OWNER;

const MlTaskCreateFormOwnerField = ({ employees = [], isLoading = false }) => (
  <Selector
    name={FIELD_NAME}
    id="owner-selector"
    fullWidth
    required
    labelMessageId="owner"
    isLoading={isLoading}
    items={employees.map((employee) => ({
      value: employee.id,
      content: <ItemContent>{employee.name}</ItemContent>
    }))}
  />
);

export default MlTaskCreateFormOwnerField;
