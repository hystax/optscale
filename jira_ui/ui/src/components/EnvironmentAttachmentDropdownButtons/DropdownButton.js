import React from "react";
import DropdownMenu from "@atlaskit/dropdown-menu";
import LinkIcon from "@atlaskit/icon/glyph/link";
import PropTypes from "prop-types";

const DropdownButton = ({ children, trigger, isLoading = false }) => (
  <DropdownMenu
    trigger={trigger}
    triggerType="button"
    isMenuFixed
    appearance="tall"
    shouldFlip
    shouldFitContainer
    boundariesElement="viewport"
    triggerButtonProps={{
      isLoading,
      iconBefore: <LinkIcon label="Link icon" />
    }}
  >
    {children}
  </DropdownMenu>
);

DropdownButton.propTypes = {
  children: PropTypes.node.isRequired,
  trigger: PropTypes.string.isRequired,
  isLoading: PropTypes.bool
};

export default DropdownButton;
