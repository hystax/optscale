import { useEffect, useState } from "react";
import { isEmpty } from "utils/objects";

/**
 * Returns new rectangle object with replaced left and top using coordinates
 * @param {Object} tooltipRect Object with left/top/width/height props
 * @param {Object} coordinates Object with left/top props
 * @returns {Object}
 */
const getUpdateTooltipRectCoordinates = (tooltipRect, coordinates) => ({
  width: tooltipRect.width,
  height: tooltipRect.height,
  ...coordinates
});

// this is gap between element and tooltip or tooltip and screen border
// bottom screen border also adds scrollHelpHeight, to display it correctly
const GAP = 20;

// positions of tooltip around target element
//             UP
//        ############
//   LEFT ############ RIGHT
//        ############
//            DOWN
const UP = 0;
const RIGHT = 1;
const DOWN = 2;
const LEFT = 3;
const NOT_SET = -1;

// how tooltip changes its position when there is no more place in current one
const POSITIONS_ORDER = [UP, RIGHT, DOWN, LEFT];

/**
 * Creating "positions queue". For example
 * 1. POSITIONS_ORDER is [UP, RIGHT, DOWN, LEFT]
 * 2. Current position is DOWN
 * 3. Queue is DOWN, LEFT] [UP, RIGHT
 * @param {number} current
 * @returns {number[]} Positions queue
 */
const getPositionsQueue = (current) => {
  const index = POSITIONS_ORDER.indexOf(current);

  const beforeIndex = POSITIONS_ORDER.slice(0, index);
  const afterIndex = POSITIONS_ORDER.slice(index);

  return afterIndex.concat(beforeIndex);
};

/**
 * Will return true if all pixels of element is offscreen
 * @param {object} targetElementRect
 * @param {number} screenWidth
 * @param {number} screenHeight
 * @returns {boolean}
 */
const getIsTargetElementOffscreen = (targetElementRect, screenWidth, screenHeight) => {
  const { top, left, width, height } = targetElementRect;
  return left + width < 0 || top + height < 0 || left > screenWidth || top > screenHeight;
};

/**
 * Does tooltip fits into screen with all possible gaps. Even one pixel over will return false
 * @param {Object} tooltipRect Tooltip rectangle object (top/left/width/height)
 * @param {number} screenWidth
 * @param {number} screenHeight
 * @param {number} scrollHelpHeight
 * @returns {boolean}
 */
// eslint-disable-next-line max-params
const isFitToScreen = (tooltipRect, screenWidth, screenHeight, scrollHelpHeight) => {
  const { top, left, width, height } = tooltipRect;
  return (
    left >= GAP && top >= GAP && left + width <= screenWidth - GAP && top + height <= screenHeight - GAP - scrollHelpHeight
  );
};

/**
 * Return position using by the x of the element relative to the center of the screen
 * @param {Object} targetElementRect Target element rectangle object (top/left/width/height)
 * @param {number} screenWidth
 * @returns {number}
 */
const getSimplePosition = (targetElementRect, screenWidth) => {
  const elementXCenter = targetElementRect.left + targetElementRect.width / 2;
  const screenXCenter = screenWidth / 2;

  return elementXCenter < screenXCenter ? RIGHT : LEFT;
};

/**
 * Return new position for tooltip for offscreen element
 * @param {number} currentPosition
 * @param {Object} targetElementRect Target element rectangle object (top/left/width/height)
 * @param {number} screenWidth
 * @param {number} screenHeight
 * @returns {number}
 */
// eslint-disable-next-line max-params
const updateOffscreenPosition = (currentPosition, targetElementRect, screenWidth, screenHeight) => {
  const { width, height, left, top } = targetElementRect;

  const isElementInScreenWidth = left + width > 0 && left < screenWidth;
  const isElementInScreenHeight = top + height > 0 && top < screenHeight;
  const elementUpToScreen = top + height < 0;
  const elementDownToScreen = top > screenHeight;
  const elementRightToScreen = left > screenWidth;
  const elementLeftToScreen = left + width < 0;

  if (elementUpToScreen && (currentPosition === UP || isElementInScreenWidth)) {
    return DOWN;
  }

  if (elementDownToScreen && (currentPosition === DOWN || isElementInScreenWidth)) {
    return UP;
  }

  if (elementRightToScreen && (currentPosition === RIGHT || isElementInScreenHeight)) {
    return LEFT;
  }

  if (elementLeftToScreen && (currentPosition === LEFT || isElementInScreenHeight)) {
    return RIGHT;
  }

  return currentPosition;
};

/**
 * Fits tooltip to screen using gaps
 * @param {Object} tooltipRect Tooltip rectangle object (top/left/width/height)
 * @param {number} screenWidth
 * @param {number} screenHeight
 * @param {number} scrollHelpHeight
 * @returns {Object} object with left and top props, which is fitted to screen with GAP and scrollHelpHeight
 */
// eslint-disable-next-line max-params
const fitToScreen = (tooltipRect, screenWidth, screenHeight, scrollHelpHeight) => {
  const { left, top, width, height } = tooltipRect;
  let newLeft = left;
  if (left < GAP) {
    newLeft = GAP;
  }
  if (left + width + GAP > screenWidth) {
    newLeft = screenWidth - width - GAP;
  }

  let newTop = top;
  if (top < GAP) {
    newTop = GAP;
  }
  if (top + height + GAP + scrollHelpHeight > screenHeight) {
    newTop = screenHeight - height - GAP - scrollHelpHeight;
  }

  return { left: newLeft, top: newTop };
};

/**
 * Calculates tooltip position near target element.
 * This position is "dirty" — it must not fit to screen most of the time
 * @param {number} position One of UP/LEFT/RIGHT/TOP
 * @param {Object} targetElementRect Target element rectangle object (top/left/width/height)
 * @param {*} tooltipRect Tooltip rectangle object (top/left/width/height)
 * @returns {Object} Coordinates of tooltip — object with left/top props
 */
const calculateTooltipCoords = (position, targetElementRect, tooltipRect) => {
  let { left, top } = targetElementRect;
  const diffToWidthCenter = (targetElementRect.width - tooltipRect.width) / 2;
  const diffToHeightCenter = (targetElementRect.height - tooltipRect.height) / 2;

  if (position === UP) {
    left += diffToWidthCenter;
    top -= GAP + tooltipRect.height;
  } else if (position === DOWN) {
    left += diffToWidthCenter;
    top += targetElementRect.height + GAP;
  } else if (position === LEFT) {
    left -= GAP + tooltipRect.width;
    top += diffToHeightCenter;
  } else if (position === RIGHT) {
    left += targetElementRect.width + GAP;
    top += diffToHeightCenter;
  }

  return { top, left };
};

/**
 * Calculates tooltip coordinates for target element
 * @param {*} targetElementRect
 * @param {*} tooltipRect
 * @param {*} scrollHelpHeight Height of "scroll help" ui, which is placed below tooltip and tells user to scroll somewhere
 * @returns {Object} tooltipCalculatedProps
 * @returns {boolean} tooltipCalculatedProps.isOffscreen is target element "offscreen"
 * @returns {Object} tooltipCalculatedProps.result Tooltip coordinates
 * @returns {number} tooltipCalculatedProps.result.top top coordinate
 * @returns {number} tooltipCalculatedProps.result.left left coordinate
 */
const usePosition = (targetElementRect, tooltipRect, scrollHelpHeight) => {
  const [position, setPosition] = useState(NOT_SET);

  const [result, setResult] = useState({ x: 0, y: 0 });

  const [isTargetOffscreen, setIsTargetOffscreen] = useState(false);

  const screenHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
  const screenWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;

  useEffect(() => {
    if (!isEmpty(tooltipRect)) {
      // FOR OFFSCREEN ELEMENT (when tooltip "follows" it on the borders)
      // 1. Changing position if element is above/below/left/right the screen
      // 2. In "undeterminate" (?) sectors set position only if current one is opposite one
      //    This way situation "tooltip was in right position, but now element is outside right and bottom borders of screen" — tooltip will be set into left position
      //
      //      ?    | setPos(D)|    ?
      // ----------+----------+----------
      // setPos(R) |  SCREEN  | setPos(L)
      // ----------+----------+----------
      //      ?    | setPos(U)|    ?
      //
      // FOR ONSCREEN (even by one pixel) ELEMENT
      // 3. Only when tooltip doesn't fit at the screen — changing position to next one, until it fits
      //
      // example, top left screen corner
      //   +---------------------------
      // +-|------------+     SCREEN
      // | | tooltip    | +---------+
      // | |            | | element |
      // | |            | +---------+
      // +-|------------+
      //   |
      //
      // Here tooltip's old position was LEFT, user scrolled element to the left, now tooltip is partially offscreen
      // So, by our algorithm:
      // 1. Trying to set next position (UP) and use it
      // 2. UP position also won't fit
      // 3. Trying to set RIGHT
      // 4. It fits, now tooltip has RIGHT position

      let updatedPosition = position;
      let resultingTooltipCoords;

      const currentIsOffscreen = getIsTargetElementOffscreen(targetElementRect, screenWidth, screenHeight);
      if (isTargetOffscreen !== currentIsOffscreen) {
        setIsTargetOffscreen(currentIsOffscreen);
      }
      if (currentIsOffscreen) {
        updatedPosition = updateOffscreenPosition(position, targetElementRect, screenWidth, screenHeight);
        if (updatedPosition !== position) {
          setPosition(updatedPosition);
        }
        // this position is always "dirty" — it places tooltip near offscreen element, so tooltip is also offscreen
        // need to be adjusted with fitToScreen function
        resultingTooltipCoords = calculateTooltipCoords(updatedPosition, targetElementRect, tooltipRect);
      } else {
        const positionsQueue = getPositionsQueue(position);
        updatedPosition = NOT_SET;

        // first trying previous position — if it is ok, just skiping calculations
        resultingTooltipCoords = calculateTooltipCoords(position, targetElementRect, tooltipRect);
        const previousPositionIsOk =
          position !== NOT_SET &&
          isFitToScreen(
            getUpdateTooltipRectCoordinates(tooltipRect, resultingTooltipCoords),
            screenWidth,
            screenHeight,
            scrollHelpHeight
          );

        if (previousPositionIsOk) {
          updatedPosition = position;
        }

        if (!previousPositionIsOk) {
          positionsQueue.every((possiblePosition) => {
            resultingTooltipCoords = calculateTooltipCoords(possiblePosition, targetElementRect, tooltipRect);
            if (
              isFitToScreen(
                getUpdateTooltipRectCoordinates(tooltipRect, resultingTooltipCoords),
                screenWidth,
                screenHeight,
                scrollHelpHeight
              )
            ) {
              updatedPosition = possiblePosition;
              return false;
            }
            return true;
          });
        }

        // "corner" case
        // if target element is too close to corner we can get into situation,
        // where all positions are not good. To resolve that, we just set left or right,
        // by the position of the element relative to the center of the screen
        if (updatedPosition === NOT_SET && !previousPositionIsOk) {
          updatedPosition = getSimplePosition(targetElementRect, screenWidth);
          resultingTooltipCoords = calculateTooltipCoords(updatedPosition, targetElementRect, tooltipRect);
        }

        // we actually found new position for tooltip
        if (updatedPosition !== NOT_SET && updatedPosition !== position) {
          setPosition(updatedPosition);
        }

        // it is possible, that no position will fit (for example, when tooltip size is larger, than screen)
        // if so — last position is used to calculate coordinates.
        // it is not "corner case" and widely used in situations when
        // offscreen element scrolls into view, but yet not enough to set tooltip at it's center points
        // Also this is example of "dirty" tooltip coords for onscreen element — they need to be adjusted
        // with fitToScreen function later
        if (updatedPosition === -1) {
          resultingTooltipCoords = calculateTooltipCoords(position, targetElementRect, tooltipRect);
        }
      }
      const updatedTooltipRectangle = getUpdateTooltipRectCoordinates(tooltipRect, resultingTooltipCoords);
      const fittedCoords = fitToScreen(updatedTooltipRectangle, screenWidth, screenHeight, scrollHelpHeight);
      setResult(fittedCoords);
    }
  }, [targetElementRect, position, screenHeight, screenWidth, isTargetOffscreen, scrollHelpHeight, tooltipRect]);

  return { result, isTargetOffscreen };
};

export default usePosition;
