import { Fragment } from "react";

const RecommendationListItem = ({ elements }) => (
  <div style={{ display: "flex", alignItems: "center" }}>
    {elements.map(({ key, node }, i) => (
      <Fragment key={key}>
        {node}
        {i !== elements.length - 1 ? <>&nbsp;|&nbsp;</> : null}
      </Fragment>
    ))}
  </div>
);

export default RecommendationListItem;
