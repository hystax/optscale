import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Checkbox } from "components/forms/common/fields";
import { FINOPS } from "urls";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.SUBSCRIBE_TO_NEWSLETTER;

const SubscribeToNewsletterCheckbox = () => (
  <Checkbox
    name={FIELD_NAME}
    label={
      <FormattedMessage
        id="subscribeMeToTheMonthlyNewsletter"
        values={{
          link: (chunks) => (
            <Link data-test-id="link_parameters_library" href={FINOPS} target="_blank" rel="noopener">
              {chunks}
            </Link>
          )
        }}
      />
    }
  />
);

export default SubscribeToNewsletterCheckbox;
