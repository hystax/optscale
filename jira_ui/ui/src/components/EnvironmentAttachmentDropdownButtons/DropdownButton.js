import React, { useEffect, useRef, useState } from "react";
import { LoadingButton } from "@atlaskit/button";
import DropdownMenu from "@atlaskit/dropdown-menu";
import LinkIcon from "@atlaskit/icon/glyph/link";
import PropTypes from "prop-types";

const DropdownButton = ({ children, triggerLabel, isLoading = false, tableRef, setMarginToFitDropdownMenu }) => {
  const [isOpen, setIsOpen] = useState(false);

  const dropdownMenuRef = useRef();

  useEffect(() => {
    if (isOpen && tableRef.current && dropdownMenuRef.current) {
      const interval = setInterval(() => {
        const dropdownMenuRectangle = dropdownMenuRef.current.getBoundingClientRect();
        const tableRectangle = tableRef.current.getBoundingClientRect();

        const isDropdownMenuFitIntoTable = tableRectangle.bottom >= dropdownMenuRectangle.bottom;

        setMarginToFitDropdownMenu(isDropdownMenuFitIntoTable ? 0 : dropdownMenuRectangle.bottom - tableRectangle.bottom);
      }, 1000 / 24);

      return () => clearInterval(interval);
    }

    setMarginToFitDropdownMenu(0);

    return undefined;
  }, [isOpen, setMarginToFitDropdownMenu, tableRef]);

  return (
    <DropdownMenu
      shouldRenderToParent
      shouldFlip={false}
      isOpen={isOpen}
      onOpenChange={(args) => {
        setIsOpen(args.isOpen);
      }}
      placement="bottom-end"
      trigger={({ triggerRef, ...props }) => (
        <LoadingButton {...props} isLoading={isLoading} iconBefore={<LinkIcon label="Link icon" />} ref={triggerRef}>
          {triggerLabel}
        </LoadingButton>
      )}
    >
      <div ref={dropdownMenuRef}>{children}</div>
    </DropdownMenu>
  );
};

DropdownButton.propTypes = {
  children: PropTypes.node.isRequired,
  triggerLabel: PropTypes.string.isRequired,
  isLoading: PropTypes.bool,
  tableRef: PropTypes.oneOfType([PropTypes.func, PropTypes.shape({ current: PropTypes.instanceOf(Element) })]).isRequired,
  setMarginToFitDropdownMenu: PropTypes.func.isRequired
};

export default DropdownButton;
