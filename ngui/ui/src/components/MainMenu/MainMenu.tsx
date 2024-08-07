import { useEffect } from "react";
import { List } from "@mui/material";
import MenuGroupWrapper from "components/MenuGroupWrapper";
import MenuItem from "components/MenuItem";
import ModeWrapper from "components/ModeWrapper";
import { PRODUCT_TOUR, useProductTour, PRODUCT_TOUR_IDS } from "components/Tour";
import { useOptScaleMode } from "hooks/useOptScaleMode";

const SimpleItem = ({ menuItem }) => {
  const optScaleMode = useOptScaleMode();

  return (
    <ModeWrapper mode={menuItem.mode}>
      <MenuItem
        className={menuItem.className}
        dataProductTourId={menuItem.dataProductTourId}
        link={menuItem.route.link}
        messageId={
          typeof menuItem.messageId === "function"
            ? menuItem.messageId({
                mode: optScaleMode
              })
            : menuItem.messageId
        }
        isRootPath={menuItem.isRootPath}
        isActive={menuItem.isActive}
        icon={menuItem.icon}
        dataTestId={menuItem.dataTestId}
      />
    </ModeWrapper>
  );
};

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
        {menu.map(({ items, menuSectionTitle, id, mode }) => (
          <ModeWrapper key={id} mode={mode}>
            <MenuGroupWrapper id={id} menuSectionTitle={menuSectionTitle} keepExpanded={isProductTourOpen}>
              {items.map((item) => (
                <SimpleItem key={item.route.link} menuItem={item} />
              ))}
            </MenuGroupWrapper>
          </ModeWrapper>
        ))}
      </List>
    </>
  );
};

export default MainMenu;
