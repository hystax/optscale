import { forwardRef } from "react";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import useStyles from "./KeyValueLabel.styles";

const HYPHEN = "hyphen";
const COLON = "colon";
const SPACE = "space";

const getPlaceholder = (type) =>
  ({
    [HYPHEN]: "-"
  })[type];

const getSeparator = (type) =>
  ({
    [HYPHEN]: <>&nbsp;-&nbsp;</>,
    [COLON]: <>:&nbsp;</>,
    [SPACE]: <>&nbsp;</>
  })[type];

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
      flexWrap = "wrap",
      ...rest
    },
    ref
  ) => {
    const { classes, cx } = useStyles({ flexWrap });

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

    const { classes: typographyClasses, keyStyle = {}, valueStyle = {}, ...restTypographyProps } = typographyProps;

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
            display: "flex",
            ...keyStyle
          }}
        >
          {keyRendered}
          {getSeparator(separator)}
        </div>
        <div
          style={{
            ...valueStyle
          }}
        >
          {valueRendered}
        </div>
      </Typography>
    );
  }
);

export default KeyValueLabel;
