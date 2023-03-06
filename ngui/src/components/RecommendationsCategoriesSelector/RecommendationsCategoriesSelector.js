import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage, useIntl } from "react-intl";
import LinearSelector from "components/LinearSelector";
import { CATEGORIES, SUPPORTED_CATEGORIES } from "components/RelevantRecommendations/constants";
import TypographyLoader from "components/TypographyLoader";
import { LINEAR_SELECTOR_ITEMS_TYPES } from "utils/constants";

const RecommendationsCategoriesSelector = ({ value, onChange, categoriesSizes, isLoading }) => {
  const intl = useIntl();

  if (isLoading) {
    return <TypographyLoader />;
  }

  // creating items from supported categories
  const items = SUPPORTED_CATEGORIES.map((categoryName) => {
    const buttonName = intl.formatMessage({ id: CATEGORIES[categoryName] });
    const recommendationsCount = categoriesSizes[categoryName];

    return {
      displayedName: `${buttonName} (${recommendationsCount})`,
      name: categoryName,
      value: categoryName,
      type: LINEAR_SELECTOR_ITEMS_TYPES.TEXT,
      dataTestId: `category_${categoryName}`
    };
  });

  // selected item by value
  const itemSelected = items.find(({ value: itemVal }) => value === itemVal);

  return <LinearSelector label={<FormattedMessage id="category" />} value={itemSelected} onChange={onChange} items={items} />;
};

RecommendationsCategoriesSelector.propTypes = {
  value: PropTypes.any.isRequired,
  onChange: PropTypes.func.isRequired,
  categoriesSizes: PropTypes.object.isRequired,
  isLoading: PropTypes.bool
};

export default RecommendationsCategoriesSelector;
