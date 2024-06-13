import { Selector } from "components/forms/common/fields";
import { ItemContent } from "components/Selector";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.NEW_DEFAULT_SSH_KEY;

const NewDefaultKeySelector = ({ keysToSelect }) => (
  <Selector
    name={FIELD_NAME}
    id="ssh-key-selector"
    required
    labelMessageId="newDefaultSshKey"
    items={keysToSelect.map(({ id, name, fingerprint }) => ({
      value: id,
      content: <ItemContent>{`${name} (${fingerprint})`}</ItemContent>
    }))}
  />
);

export default NewDefaultKeySelector;
