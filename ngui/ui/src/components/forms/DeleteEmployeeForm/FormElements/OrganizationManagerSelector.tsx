import { Selector } from "components/forms/common/fields";
import { ItemContent } from "components/Selector";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.ORGANIZATION_MANAGER;

const OrganizationManagerSelector = ({ organizationManagersWhoSuitableForAssignment }) => (
  <Selector
    id="organization-manager-selector"
    name={FIELD_NAME}
    required
    labelMessageId="organizationManager"
    items={organizationManagersWhoSuitableForAssignment.map(({ name, value }) => ({
      value,
      content: <ItemContent>{name}</ItemContent>
    }))}
  />
);

export default OrganizationManagerSelector;
