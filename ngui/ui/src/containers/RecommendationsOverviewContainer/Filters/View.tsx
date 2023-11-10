import ButtonGroup from "components/ButtonGroup";

export const VIEW_CARDS = "cards";
export const VIEW_TABLE = "table";

const VIEWS = [
  {
    id: VIEW_CARDS,
    messageId: "cards"
  },
  {
    id: VIEW_TABLE,
    messageId: "table"
  }
];

export const POSSIBLE_VIEWS = VIEWS.map(({ id }) => id);
export const DEFAULT_VIEW = VIEWS[0].id;

const View = ({ onChange, value }) => {
  const activeButtonIndex = VIEWS.findIndex(({ id }) => id === value);
  const buttons = VIEWS.map((v) => ({ ...v, action: () => onChange(v.id) }));

  return <ButtonGroup buttons={buttons} activeButtonIndex={activeButtonIndex === -1 ? 0 : activeButtonIndex} />;
};

export default View;
