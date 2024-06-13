import { Selector } from "components/forms/common/fields";
import { ItemContent } from "components/Selector";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.OWNER;

const OwnerSelector = ({ owners, isLoading = false, isReadOnly = false }) => (
  <Selector
    name={FIELD_NAME}
    id="pool-owner-selector"
    labelMessageId="defaultResourceOwner"
    fullWidth
    isLoading={isLoading}
    readOnly={isReadOnly}
    items={owners.map((owner) => ({
      value: owner.id,
      content: <ItemContent>{owner.name}</ItemContent>
    }))}
  />
);

export default OwnerSelector;
