import React, { useEffect } from "react";
import { List } from "@mui/material";
import PropTypes from "prop-types";
import MenuGroupWrapper from "components/MenuGroupWrapper";
import MenuItem from "components/MenuItem";
import { PRODUCT_TOUR, useProductTour, PRODUCT_TOUR_IDS } from "components/Tour";

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
  const { isOpen: isProductTourOpen, stepId: productTourStepId } = useProductTour(PRODUCT_TOUR);

  useEffect(() => {
    if (!productTourStepId || !isProductTourOpen) {
      return;
    }

    const targetElement = document.querySelector(`[data-product-tour-id='${productTourStepId}']`);
    const menuDrawer = document.querySelector(`[data-product-tour-id='${PRODUCT_TOUR_IDS.MENU_DRAWER}']`);
    if (!targetElement || !menuDrawer) {
      console.warn("Product tour did not found target elements for scroll");
      return;
    }
    const windowHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
    const elementTop = targetElement.getBoundingClientRect().top;
    // trying to scroll menu to place target element as close to screen center, as possible
    menuDrawer.scrollTop -= windowHeight / 2 - elementTop;
  }, [productTourStepId, isProductTourOpen]);

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
