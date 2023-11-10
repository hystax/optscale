import { FormattedMessage } from "react-intl";
import RecommendationCard, {
  ServicesChipsGrid,
  TableContent,
  Menu,
  Header,
  AWS_IAM,
  ALIBABA_RDS
} from "containers/RecommendationsOverviewContainer/RecommendationCard";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/RecommendationCard`,
  argTypes: {
    title: { name: "Title", control: "text", defaultValue: "Card title" },
    subtitleText: { name: "Subtitle", control: "text", defaultValue: "" },
    chips: { name: "Services chips", control: "boolean", defaultValue: true },
    value: { name: "Value", control: "text", defaultValue: "14k" },
    valueLabel: { name: "Value label", control: "text", defaultValue: "savings" },
    cardColor: {
      name: "Color",
      control: "select",
      options: ["success", "error", "warning", undefined],
      defaultValue: undefined
    },
    descriptionText: { name: "Description", control: "text", defaultValue: "Card description text" },
    itemsPreview: { name: "Items preview", control: "boolean", defaultValue: true },
    cta: { name: "Call to action", control: "boolean", defaultValue: true },
    menu: { name: "Menu", control: "boolean", defaultValue: true }
  }
};

const menu = (
  <Menu
    items={[
      { key: "setup", caption: "Setup", onClick: () => console.log("setup clicked") },
      { key: "exclude", caption: "Exclude pools (1)", onClick: () => console.log("exclude clicked") },
      { key: "dismiss", caption: "Dismiss all", onClick: () => console.log("dismiss all clicked") },
      { key: "download", caption: "Download items", onClick: () => console.log("download items clicked") },
      { key: "scripts", caption: "Download scripts", onClick: () => console.log("download scripts clicked") },
      { key: "pin", caption: "Pin to top", onClick: () => console.log("setup clicked") }
    ]}
  />
);

export const basic = (args) => (
  <RecommendationCard
    color={args.cardColor}
    header={
      <Header
        color={args.cardColor}
        title={<FormattedMessage id={args.title} />}
        subtitle={
          <>
            {args.subtitleText}
            {args.chips && <ServicesChipsGrid services={[AWS_IAM, ALIBABA_RDS]} />}
          </>
        }
        value={args.value}
        valueLabel={args.valueLabel}
      />
    }
    description={args.descriptionText}
    cta={args.cta && <FormattedMessage id="seeAllItems" values={{ value: 10 }} />}
    onCtaClick={() => console.log(`details clicked`)}
    menu={args.menu && menu}
  >
    {args.itemsPreview && (
      <TableContent
        data={[
          [
            { key: "1", value: "item sample 1" },
            { key: "2", value: "item property" },
            { key: "3", value: "item value" }
          ],
          [
            { key: "4", value: "item sample 2" },
            { key: "5", value: "property" },
            { key: "6", value: "another value" }
          ]
        ]}
      />
    )}
  </RecommendationCard>
);
