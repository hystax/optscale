import { useState, useRef, useEffect } from "react";
import { useIsDownMediaQuery } from "hooks/useMediaQueries";
import { useResizeObserver } from "hooks/useResizeObserver";

export const COLLAPSE_MODE = "collapse";
export const HIDE_MODE = "hide";

export const useHideActionsForSmallScreens = ({
  wrapperRef, // this wrapper detects resize and it's vector (inc/dec)
  titleRef, // next two refs are for collision detection
  buttonsRef,
  itemsLength, // length of displaying items
  breakpoint = "",
  mode = COLLAPSE_MODE,
  enabled = true // need to disable this hook in case of actionbars without mobile view (Environments page, for example)
}) => {
  const [hiddenElementsLength, setHiddenElementsLength] = useState(0);
  const { width: wrapperWidth = 0 } = useResizeObserver(wrapperRef);
  const lastWidth = useRef(0);

  const alreadyShowedOneItem = useRef(false);
  const isMobile = useIsDownMediaQuery(breakpoint || "md");

  useEffect(() => {
    if (!enabled) {
      return;
    }

    // in COLLAPSE_MODE it's all or nothing hidden
    // this "mode" is actually needed only in one place: table action bar, due to there is no header, only buttons
    // TODO: mode should be removed after https://datatrendstech.atlassian.net/browse/OS-3554
    if (mode === COLLAPSE_MODE) {
      if (isMobile && hiddenElementsLength !== itemsLength) {
        setHiddenElementsLength(itemsLength);
      } else if (!isMobile && hiddenElementsLength !== 0) {
        setHiddenElementsLength(0);
      }
      return;
    }

    const { current: buttonsElement } = buttonsRef;
    const { current: titleElement } = titleRef;

    // in regular mode tracking space between title and buttons (but only after refs inited)
    if (!(buttonsElement && titleElement)) {
      return;
    }

    const isOverflow = buttonsElement.getBoundingClientRect().left - titleElement.getBoundingClientRect().right < 1;

    if (isOverflow && hiddenElementsLength < itemsLength) {
      // if overflow (title and buttons have no space between) and we can hide something — increasing hidden items
      setHiddenElementsLength(hiddenElementsLength + 1);
    } else if (!isOverflow && hiddenElementsLength !== 0 && !alreadyShowedOneItem.current) {
      // but if there is no overflow we can decrease hidden items
      // but we can decrease them only one by one for each wrapper width
      // or there will be cycle "hide element" -> no overflow -> "show element" -> overflow -> ...repeat
      // that's why there is a flag, to prevent second "show element" in cycle
      alreadyShowedOneItem.current = true;
      setHiddenElementsLength(hiddenElementsLength - 1);
    }

    // dropping flag if wrapper width changed (but we do not need to drop it for decreasing wrapper width)
    if (lastWidth.current < wrapperWidth) {
      alreadyShowedOneItem.current = false;
    }

    lastWidth.current = wrapperWidth;
  }, [buttonsRef, titleRef, hiddenElementsLength, itemsLength, wrapperWidth, isMobile, breakpoint, enabled, mode]);

  return {
    hiddenElementsLength
  };
};
