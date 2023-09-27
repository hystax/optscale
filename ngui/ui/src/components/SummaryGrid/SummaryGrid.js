import React from "react";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import { FormattedNumber, FormattedMessage } from "react-intl";
import { v4 as uuidv4 } from "uuid";
import FormattedDigitalUnit from "components/FormattedDigitalUnit";
import FormattedMoney from "components/FormattedMoney";
import SummaryCard from "components/SummaryCard";
import SummaryCardExtended from "components/SummaryCardExtended";
import Tooltip from "components/Tooltip";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { SUMMARY_CARD_TYPES, SUMMARY_VALUE_COMPONENT_TYPES, FORMATTED_MONEY_TYPES } from "utils/constants";
import { SPACING_2 } from "utils/layouts";

const getValueComponentSettings = (type, CustomComponent) => ({
  component: {
    [SUMMARY_VALUE_COMPONENT_TYPES.FormattedNumber]: FormattedNumber,
    [SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney]: ({ value, ...rest }) => {
      const { currency = "USD" } = useOrganizationInfo();

      return (
        <Tooltip title={<FormattedNumber format={currency} value={value} />}>
          <span>
            <FormattedMoney {...rest} value={value} type={FORMATTED_MONEY_TYPES.COMPACT} />
          </span>
        </Tooltip>
      );
    },
    [SUMMARY_VALUE_COMPONENT_TYPES.FormattedMessage]: FormattedMessage,
    [SUMMARY_VALUE_COMPONENT_TYPES.FormattedDigitalUnit]: FormattedDigitalUnit,
    [SUMMARY_VALUE_COMPONENT_TYPES.Custom]: CustomComponent
  }[type],
  computedProps: {
    FormattedMoney: {}
  }[type]
});

const renderSummaryCard = ({
  value,
  valueComponentType,
  valueComponentProps,
  captionMessageId,
  caption,
  rawCaption,
  CustomValueComponent = null,
  isLoading,
  color,
  help,
  button,
  dataTestIds,
  icon,
  pdfId,
  backdrop
}) => {
  const { component: ValueComponent } = getValueComponentSettings(valueComponentType, CustomValueComponent);

  return (
    <SummaryCard
      value={ValueComponent ? <ValueComponent {...valueComponentProps} /> : value}
      icon={icon}
      rawValue={valueComponentProps?.value}
      caption={caption ?? <FormattedMessage id={captionMessageId} />}
      rawCaption={rawCaption ?? captionMessageId}
      isLoading={isLoading}
      color={color}
      help={help}
      button={button}
      dataTestIds={dataTestIds}
      pdfId={pdfId}
      backdrop={backdrop}
    />
  );
};

const renderExtendedSummaryCard = ({
  value,
  valueComponentType,
  valueComponentProps,
  CustomValueComponent = null,
  captionMessageId,
  caption,
  relativeValue,
  relativeValueComponentType,
  relativeValueComponentProps,
  CustomRelativeValueComponent = null,
  relativeValueCaptionMessageId,
  isLoading,
  color,
  help,
  button,
  dataTestIds,
  icon,
  backdrop
}) => {
  const { component: ValueComponent, computedProps: computedValueComponentProps = {} } = getValueComponentSettings(
    valueComponentType,
    CustomValueComponent
  );

  const { component: RelativeValueComponent, computedProps: computedRelativeValueComponentProps = {} } =
    getValueComponentSettings(relativeValueComponentType, CustomRelativeValueComponent);

  return (
    <SummaryCardExtended
      value={ValueComponent ? <ValueComponent {...computedValueComponentProps} {...valueComponentProps} /> : value}
      relativeValue={
        RelativeValueComponent ? (
          <RelativeValueComponent {...computedRelativeValueComponentProps} {...relativeValueComponentProps} />
        ) : (
          relativeValue
        )
      }
      caption={caption ?? <FormattedMessage id={captionMessageId} />}
      relativeValueCaption={<FormattedMessage id={relativeValueCaptionMessageId} />}
      icon={icon}
      isLoading={isLoading}
      color={color}
      help={help}
      button={button}
      dataTestIds={dataTestIds}
      backdrop={backdrop}
    />
  );
};

const getCardRenderer = (cardType) =>
  ({
    [SUMMARY_CARD_TYPES.BASIC]: renderSummaryCard,
    [SUMMARY_CARD_TYPES.EXTENDED]: renderExtendedSummaryCard
  }[cardType]);

const SummaryGrid = ({ summaryData }) => {
  const renderSummary = () =>
    summaryData.map(({ key, renderCondition, type = SUMMARY_CARD_TYPES.BASIC, isLoading, ...rest }) => {
      const shouldRender = renderCondition ? renderCondition() || isLoading : true;
      const renderCard = getCardRenderer(type);
      return renderCard && shouldRender ? (
        <Grid item key={key || uuidv4()}>
          {renderCard({ isLoading, ...rest })}
        </Grid>
      ) : null;
    });

  return (
    <Grid container item spacing={SPACING_2}>
      {renderSummary()}
    </Grid>
  );
};

const supportedValueComponents = [
  SUMMARY_VALUE_COMPONENT_TYPES.FormattedNumber,
  SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
  SUMMARY_VALUE_COMPONENT_TYPES.FormattedMessage,
  SUMMARY_VALUE_COMPONENT_TYPES.Custom
];

const basicCardProps = PropTypes.shape({
  key: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  type: PropTypes.oneOf([SUMMARY_CARD_TYPES.BASIC, SUMMARY_CARD_TYPES.EXTENDED]),
  value: PropTypes.oneOfType([PropTypes.number, PropTypes.string, PropTypes.node]),
  valueComponentType: PropTypes.oneOf(supportedValueComponents),
  CustomValueComponent: PropTypes.elementType,
  valueComponentProps: PropTypes.object,
  caption: PropTypes.node,
  captionMessageId: PropTypes.string,
  isLoading: PropTypes.bool,
  renderCondition: PropTypes.func,
  color: PropTypes.string,
  help: PropTypes.object,
  button: PropTypes.object,
  dataTestIds: PropTypes.object
});

const extendedCardProps = PropTypes.shape({
  key: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  type: PropTypes.oneOf([SUMMARY_CARD_TYPES.BASIC, SUMMARY_CARD_TYPES.EXTENDED]),
  value: PropTypes.oneOfType([PropTypes.number, PropTypes.string, PropTypes.node]),
  valueComponentType: PropTypes.oneOf(supportedValueComponents),
  CustomValueComponent: PropTypes.elementType,
  valueComponentProps: PropTypes.object,
  relativeValue: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
  relativeValueComponentType: PropTypes.oneOf(supportedValueComponents),
  relativeValueComponentProps: PropTypes.object,
  CustomRelativeValueComponent: PropTypes.elementType,
  captionMessageId: PropTypes.string.isRequired,
  isLoading: PropTypes.bool,
  renderCondition: PropTypes.func,
  color: PropTypes.string,
  help: PropTypes.object,
  button: PropTypes.object,
  dataTestIds: PropTypes.object
});

SummaryGrid.propTypes = {
  summaryData: PropTypes.arrayOf(PropTypes.oneOfType([basicCardProps, extendedCardProps]))
};

export default SummaryGrid;
