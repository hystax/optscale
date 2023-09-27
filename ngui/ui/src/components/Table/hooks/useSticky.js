import { useEffect } from "react";

export const useSticky = ({ headerRef, stickySettings }) => {
  const { scrollWrapperDOMId, stickyHeader } = stickySettings;

  useEffect(() => {
    const wrapperElement = document.getElementById(scrollWrapperDOMId);

    if (headerRef && headerRef.current && wrapperElement) {
      if (stickyHeader) {
        const tableHeader = headerRef.current;

        const moveThElements = () => {
          const wrapperRect = wrapperElement.getBoundingClientRect();
          const tableHeaderRect = tableHeader.getBoundingClientRect();

          const thElements = Array.from(tableHeader.querySelectorAll("th"));

          const distanceFromHeaderToWrapper = tableHeaderRect.y - wrapperRect.y;
          const isTableHeaderAboveAvailableSpace = distanceFromHeaderToWrapper < 0;

          thElements.forEach((th) => {
            // eslint-disable-next-line no-param-reassign
            th.style.transform = `translateY(${isTableHeaderAboveAvailableSpace ? -distanceFromHeaderToWrapper : 0}px)`;
          });
        };

        /**
         * Trigger move of the th elements to cover the case when
         * the table header is already scrolled out beyond the wrapper
         */
        moveThElements();

        wrapperElement.addEventListener("scroll", moveThElements);

        return () => {
          wrapperElement.removeEventListener("scroll", moveThElements);
        };
      }
    }

    return undefined;
  }, [headerRef, scrollWrapperDOMId, stickyHeader]);

  return {
    stickyHeaderStyles: stickyHeader
      ? {
          backgroundColor: "white"
        }
      : {},
    stickyTableStyles: stickyHeader
      ? {
          borderCollapse: "separate"
        }
      : {}
  };
};
