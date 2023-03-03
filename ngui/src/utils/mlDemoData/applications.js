import { getParameter } from "./parameters";

const applications = [
  {
    name: "Shoes categorizer",
    key: "shoes_categorizer",
    id: "1e0815a2-72d2-418b-afad-bedc99a5e9d2",
    owner_id: "1b7b78b8-6a0d-4f74-b2dc-65fdbe6203c4",
    owner: {
      id: "1b7b78b8-6a0d-4f74-b2dc-65fdbe6203c4",
      name: "Charlie Fisher"
    },
    status: "completed",
    goals: [getParameter("accuracy"), getParameter("data_loss"), getParameter("inference_time"), getParameter("data_processed")]
  },
  {
    name: "Image recognition",
    key: "image_recognition",
    id: "2e0815a2-72d2-418b-afad-bedc99a5e9d2",
    owner_id: "2b7b78b8-6a0d-4f74-b2dc-65fdbe6203c4",
    owner: {
      id: "2b7b78b8-6a0d-4f74-b2dc-65fdbe6203c4",
      name: "Ellie Edwards"
    },
    status: "failed",
    goals: [getParameter("accuracy"), getParameter("data_loss"), getParameter("inference_time"), getParameter("data_processed")]
  },
  {
    name: "Behavior prediction",
    key: "behavior_prediction",
    id: "3e0815a2-72d2-418b-afad-bedc99a5e9d2",
    owner_id: "3b7b78b8-6a0d-4f74-b2dc-65fdbe6203c4",
    owner: {
      id: "3b7b78b8-6a0d-4f74-b2dc-65fdbe6203c4",
      name: "Hope Wilson"
    },
    status: "failed",
    goals: [
      getParameter("accuracy"),
      getParameter("data_loss"),
      getParameter("inference_time"),
      getParameter("data_processed"),
      getParameter("data_corrupted")
    ]
  },
  {
    name: "Meals categorizer",
    key: "meals_categorizer",
    id: "4e0815a2-72d2-418b-afad-bedc99a5e9d2",
    owner_id: "4b7b78b8-6a0d-4f74-b2dc-65fdbe6203c4",
    owner: {
      id: "4b7b78b8-6a0d-4f74-b2dc-65fdbe6203c4",
      name: "Jack Gagnon"
    },
    status: "completed",
    goals: [getParameter("accuracy"), getParameter("inference_time"), getParameter("data_processed")]
  }
];

export { applications };
