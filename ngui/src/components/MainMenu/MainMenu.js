import React from "react";
import { List } from "@mui/material";
import PropTypes from "prop-types";
import MenuGroupWrapper from "components/MenuGroupWrapper";
import MenuItem from "components/MenuItem";
import { PRODUCT_TOUR, useProductTour } from "components/Tour";

const simpleItem = (menuItem) => (
  <MenuItem
    key={menuItem.key}
    className={menuItem.className}
    dataProductTourId={menuItem.dataProductTourId}
    link={menuItem.route.link}
    messageId={menuItem.messageId}
    isRootPath={menuItem.isRootPath}
    isActive={menuItem.isActive}
    icon={menuItem.icon}
    dataTestId={menuItem.dataTestId}
  />
);

const MainMenu = ({ menu }) => {
  const { isOpen: isProductTourOpen } = useProductTour(PRODUCT_TOUR);

  return (
    <>
      <List component="nav" sx={{ padding: 0 }}>
        {menu.map(({ items, menuSectionTitle, menuSectionBadge, id }) => (
          <MenuGroupWrapper
            id={id}
            key={id}
            menuSectionTitle={menuSectionTitle}
            menuSectionBadge={menuSectionBadge}
            keepExpanded={isProductTourOpen}
          >
            {items.map((item) => simpleItem(item))}
          </MenuGroupWrapper>
        ))}
      </List>
    </>
  );
};

MainMenu.propTypes = {
  menu: PropTypes.array.isRequired
};

export default MainMenu;
