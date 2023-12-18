import EventsOverviewListItem from "components/EventsOverviewListItem";

export default {
  component: EventsOverviewListItem,
  argTypes: {
    title: { name: "Title", control: "text", defaultValue: "Initial warning" },
    description: { name: "Description", control: "text", defaultValue: "Something went wrong!" },
    time: { name: "Time", control: "number", defaultValue: 1578214058 },
    level: {
      name: "Level",
      control: "select",
      options: ["warning", "success", "info", "error"],
      defaultValue: "error"
    }
  }
};

export const basic = () => <EventsOverviewListItem title="Title" description="Description" level="info" time={1578214058} />;

export const withKnobs = (args) => (
  <EventsOverviewListItem title={args.title} description={args.description} level={args.level} time={args.time} />
);
