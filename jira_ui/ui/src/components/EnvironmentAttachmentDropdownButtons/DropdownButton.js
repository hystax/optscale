import React from "react";
import { LoadingButton } from "@atlaskit/button";
import DropdownMenu from "@atlaskit/dropdown-menu";
import LinkIcon from "@atlaskit/icon/glyph/link";
import PropTypes from "prop-types";

const DropdownButton = ({ children, triggerLabel, isLoading = false }) => (
  <DropdownMenu
    appearance="tall"
    shouldFlip
    shouldRenderToParent
    trigger={({ triggerRef, ...props }) => (
      <LoadingButton {...props} isLoading={isLoading} iconBefore={<LinkIcon label="Link icon" />} ref={triggerRef}>
        {triggerLabel}
      </LoadingButton>
    )}
  >
    {children}
  </DropdownMenu>
);

DropdownButton.propTypes = {
  children: PropTypes.node.isRequired,
  triggerLabel: PropTypes.string.isRequired,
  isLoading: PropTypes.bool
};

export default DropdownButton;
