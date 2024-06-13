import { Selector } from "components/forms/common/fields";
import { ItemContent } from "components/Selector";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.TASK;

const LABEL_ID = "task";

const TaskField = ({ tasks, isLoading = false }) => (
  <Selector
    name={FIELD_NAME}
    id="task-selector"
    fullWidth
    required
    labelMessageId={LABEL_ID}
    isLoading={isLoading}
    items={tasks.map(({ id, name }) => ({
      value: id,
      content: <ItemContent>{name}</ItemContent>
    }))}
  />
);

export default TaskField;
