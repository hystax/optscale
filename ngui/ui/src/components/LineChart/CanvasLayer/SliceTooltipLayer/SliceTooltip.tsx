import { useMeasure } from "@nivo/core";

const TOOLTIP_OFFSET = 14;

export const TOOLTIP_ANCHOR = Object.freeze({
  LEFT: "left",
  RIGHT: "right"
});

const SliceTooltip = ({ position, anchor, children }) => {
  const [measureRef, bounds] = useMeasure();

  let x = Math.round(position.x);
  let y = Math.round(position.y);

  const hasDimension = bounds.width > 0 && bounds.height > 0;

  if (hasDimension) {
    if (anchor === TOOLTIP_ANCHOR.RIGHT) {
      x += TOOLTIP_OFFSET;
      y -= bounds.height / 2;
    }
    if (anchor === TOOLTIP_ANCHOR.LEFT) {
      x -= bounds.width + TOOLTIP_OFFSET;
      y -= bounds.height / 2;
    }
  }

  return (
    <div
      ref={measureRef}
      style={{
        position: "absolute",
        pointerEvents: "none",
        left: x,
        top: y
      }}
    >
      {children}
    </div>
  );
};

export default SliceTooltip;
