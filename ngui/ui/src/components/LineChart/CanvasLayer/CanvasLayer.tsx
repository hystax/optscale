import { useEffect, useRef } from "react";

const CanvasLayer = ({ layerProps, renderCanvasContent }) => {
  const { outerHeight, outerWidth } = layerProps;

  const ref = useRef();

  useEffect(() => {
    if (!ref.current) {
      return undefined;
    }

    const ctx = ref.current.getContext("2d");

    renderCanvasContent(ctx, layerProps);

    return () => ctx.clearRect(0, 0, outerWidth, outerHeight);
  }, [layerProps, outerHeight, outerWidth, renderCanvasContent]);

  return (
    <div
      style={{
        position: "absolute"
      }}
    >
      <canvas ref={ref} style={{ position: "absolute" }} height={outerHeight} width={outerWidth} />
    </div>
  );
};

export default CanvasLayer;
