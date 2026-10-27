import { useIntl } from "react-intl";
import { Selector } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";
import { ItemContent } from "components/Selector";
import { useCurrentEmployee } from "hooks/coreData/useCurrentEmployee";
import { FIELD_NAMES } from "../constants";

type OwnerSelectorProps = {
  owners: { id: string; name: string }[];
  isLoading?: boolean;
  isReadOnly?: boolean;
  helpMessageId?: string;
};

const FIELD_NAME = FIELD_NAMES.OWNER;

const OwnerSelector = ({ owners, isLoading = false, isReadOnly = false, helpMessageId }: OwnerSelectorProps) => {
  const intl = useIntl();

  const currentEmployee = useCurrentEmployee();

  return (
    <Selector
      name={FIELD_NAME}
      id="pool-owner-selector"
      labelMessageId="defaultResourceOwner"
      fullWidth
      isLoading={isLoading}
      required
      readOnly={isReadOnly}
      items={[
        ...owners.filter((owner) => owner.id === currentEmployee.id),
        ...owners
          .filter((owner) => owner.id !== currentEmployee.id)
          .sort(({ name: nameA }, { name: nameB }) => nameA.localeCompare(nameB)),
      ].map((owner) => ({
        value: owner.id,
        content: (
          <ItemContent>
            {owner.id === currentEmployee.id ? `${owner.name} (${intl.formatMessage({ id: "you" })})` : owner.name}
          </ItemContent>
        ),
      }))}
      endAdornment={helpMessageId && <QuestionMark messageId={helpMessageId} dataTestId="qmark_default_owner" />}
    />
  );
};

export default OwnerSelector;
