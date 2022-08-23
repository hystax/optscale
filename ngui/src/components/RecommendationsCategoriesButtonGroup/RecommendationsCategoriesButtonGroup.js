import React from "react";
import Skeleton from "@mui/material/Skeleton";
import PropTypes from "prop-types";
import { useIntl } from "react-intl";
import ButtonGroup from "components/ButtonGroup";
import { CATEGORIES, SUPPORTED_CATEGORIES } from "components/RelevantRecommendations/constants";

const formatButtonMessage = (name, count) => `${name} (${count})`;

const RecommendationsCategoriesButtonGroup = ({ categoriesSizes, isLoading, category, onClick }) => {
  const intl = useIntl();

  const buttonsGroup = SUPPORTED_CATEGORIES.map((categoryName) => {
    const buttonName = intl.formatMessage({ id: CATEGORIES[categoryName] });
    const recommendationsCount = categoriesSizes[categoryName];

    return {
      id: categoryName,
      messageText: formatButtonMessage(buttonName, recommendationsCount),
      dataTestId: `category_${categoryName}`,
      action: () => onClick(categoryName)
    };
  });

  const buttons = (
    <ButtonGroup buttons={buttonsGroup} activeButtonIndex={buttonsGroup.findIndex((button) => button.id === category)} />
  );

  return isLoading ? <Skeleton>{buttons}</Skeleton> : buttons;
};

RecommendationsCategoriesButtonGroup.propTypes = {
  category: PropTypes.oneOf(SUPPORTED_CATEGORIES).isRequired,
  onClick: PropTypes.func.isRequired,
  categoriesSizes: PropTypes.object.isRequired,
  isLoading: PropTypes.bool
};

export default RecommendationsCategoriesButtonGroup;
