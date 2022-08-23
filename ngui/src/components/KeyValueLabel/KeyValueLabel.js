import React, { forwardRef } from "react";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage, FormattedNumber } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import useStyles from "./KeyValueLabel.styles";

const HYPHEN = "hyphen";
const COLON = "colon";
const SPACE = "space";

const getPlaceholder = (type) =>
  ({
    [HYPHEN]: "-"
  }[type]);

const getSeparator = (type) =>
  ({
    [HYPHEN]: <>&nbsp;-&nbsp;</>,
    [COLON]: <>:&nbsp;</>,
    [SPACE]: <>&nbsp;</>
  }[type]);

const KeyValueLabel = forwardRef(
  (
    {
      value,
      messageId,
      text,
      renderKey,
      separator = COLON,
      variant,
      placeholder = HYPHEN,
      isBoldValue = true,
      typographyProps = {},
      dataTestIds = {},
      ...rest
    },
    ref
  ) => {
    const { classes, cx } = useStyles();

    const renderNode = () => (value || value === 0 ? value : getPlaceholder(placeholder));

    const renderValue = () => {
      const valueElement = typeof value === "function" ? value() : renderNode();
      if (isBoldValue) {
        return <strong>{valueElement}</strong>;
      }
      return valueElement;
    };

    const renderTextKey = () => (messageId ? <FormattedMessage key={messageId} id={messageId} /> : text);

    const renderKeyComponent = () => (renderKey ? renderKey() : renderTextKey());

    const { typography: typographyDataTestId, key: keyDataTestId, value: valueDataTestId } = dataTestIds;

    const keyRendered = keyDataTestId ? <span data-test-id={keyDataTestId}>{renderKeyComponent()}</span> : renderKeyComponent();
    const valueRendered = valueDataTestId ? <span data-test-id={valueDataTestId}>{renderValue()}</span> : renderValue();

    const { classes: typographyClasses, ...restTypographyProps } = typographyProps;

    const mergedTypographyRootAndClasses = {
      ...classes,
      ...typographyClasses,
      root: cx(typographyClasses?.root, classes.root)
    };

    return (
      <Typography
        ref={ref}
        classes={mergedTypographyRootAndClasses}
        noWrap
        data-test-id={typographyDataTestId}
        component="div"
        variant={variant}
        {...restTypographyProps}
        {...rest}
      >
        <div
          style={{
            display: "flex"
          }}
        >
          {keyRendered}
          {getSeparator(separator)}
        </div>
        <div>{valueRendered}</div>
      </Typography>
    );
  }
);

KeyValueLabel.propTypes = {
  value: PropTypes.oneOfType([
    PropTypes.number,
    PropTypes.array,
    PropTypes.string,
    PropTypes.func,
    PropTypes.node,
    PropTypes.shape({
      type: PropTypes.oneOf([FormattedMessage, FormattedNumber, FormattedMoney])
    })
  ]),
  messageId: PropTypes.string,
  text: PropTypes.node,
  dataTestIds: PropTypes.shape({
    typography: PropTypes.string,
    key: PropTypes.string,
    value: PropTypes.string
  }),
  typographyProps: PropTypes.object,
  renderKey: PropTypes.func,
  separator: PropTypes.oneOf([COLON, HYPHEN, SPACE]),
  variant: PropTypes.string,
  isBoldValue: PropTypes.bool,
  placeholder: PropTypes.oneOf([HYPHEN])
};

export default KeyValueLabel;
