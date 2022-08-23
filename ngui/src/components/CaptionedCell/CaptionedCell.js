import React from "react";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import CellCaption from "components/CellCaption";
import { isObject } from "utils/objects";

const Caption = ({ caption, tooltipText, enableTextCopy, copyTextDataTestIds }) => (
  <CellCaption
    text={caption}
    tooltipText={tooltipText}
    enableCaptionTextCopy={enableTextCopy}
    copyTextDataTestIds={copyTextDataTestIds}
  />
);

const CaptionGridItem = ({ node, caption, ...rest }) => <Grid item>{node ?? <Caption caption={caption} {...rest} />}</Grid>;

const renderCaptionGridItem = (caption, rest) => {
  if (Array.isArray(caption)) {
    return caption.map(({ key, ...captionProps }) => <CaptionGridItem key={key} {...captionProps} />);
  }
  if (isObject(caption)) {
    return <CaptionGridItem {...caption} />;
  }
  return <CaptionGridItem caption={caption} {...rest} />;
};

const CaptionedCell = ({ children, caption, ...rest }) => (
  <Grid container direction="column">
    <Grid item>{children}</Grid>
    {caption && renderCaptionGridItem(caption, rest)}
  </Grid>
);

const commonProps = {
  caption: PropTypes.string,
  tooltipText: PropTypes.string,
  enableTextCopy: PropTypes.bool,
  copyTextDataTestIds: PropTypes.object
};

const objectProps = { key: PropTypes.string.isRequired, node: PropTypes.node, ...commonProps };

CaptionedCell.propTypes = {
  children: PropTypes.node.isRequired,
  ...commonProps,
  caption: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.shape({
      ...objectProps
    }),
    PropTypes.arrayOf(
      PropTypes.shape({
        ...objectProps
      })
    )
  ])
};

export default CaptionedCell;
