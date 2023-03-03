import React from "react";
import PropTypes from "prop-types";
import { useIntl } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel";

const RecommendationSaving = ({ saving }) => {
  const intlFormatter = useIntl();

  const monthTranslation = intlFormatter.formatMessage({ id: "month" }).toLowerCase();
  const perMonthTranslation = intlFormatter.formatMessage({ id: "perX" }, { x: monthTranslation }).toLowerCase();

  return (
    <KeyValueLabel
      messageId="savings"
      isBoldValue={false}
      value={() => (
        <>
          <strong>
            <FormattedMoney value={saving} />
          </strong>
          &nbsp;
          {perMonthTranslation}
        </>
      )}
    />
  );
};

RecommendationSaving.propTypes = {
  saving: PropTypes.number.isRequired
};

export default RecommendationSaving;
