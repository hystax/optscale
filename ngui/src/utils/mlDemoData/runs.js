import { getParameter } from "utils/mlDemoData/parameters";

const shoesCategorizerRuns = [
  {
    application_id: "1e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674805862,
    finish: 1674805925,
    name: "strange_bassi",
    number: 3,
    imports: ["tf", "torch", "numpy"],
    tags: {
      Mode: "Test"
    },
    data: {
      accuracy: 0.8,
      data_loss: 0.3,
      inference_time: 0.18,
      data_processed: 134
    },
    executors: [
      "1df0f6be-99c1-4d41-9614-10ee3d1d9917",
      "2df0f6be-99c1-4d41-9614-10ee3d1d9917",
      "3df0f6be-99c1-4d41-9614-10ee3d1d9917"
    ],
    id: "66ad45dc-025f-4204-8261-e27383b50fcb",
    status: "completed",
    duration: 63,
    cost: 102.421,
    goals: [getParameter("accuracy"), getParameter("data_loss"), getParameter("inference_time"), getParameter("data_processed")]
  },
  {
    application_id: "1e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674802668,
    finish: 1674802821,
    name: "relaxed_antonelli",
    number: 2,
    imports: ["tf", "torch", "numpy"],
    tags: {
      Mode: "Development"
    },
    data: {
      accuracy: 0.6,
      data_loss: 0.5,
      inference_time: 0.2,
      data_processed: 154
    },
    executors: ["1df0f6be-99c1-4d41-9614-10ee3d1d9917", "2df0f6be-99c1-4d41-9614-10ee3d1d9917"],
    id: "76ad45dc-025f-4204-8261-e27383b50fcb",
    status: "completed",
    duration: 78,
    cost: 51.1,
    goals: [getParameter("accuracy"), getParameter("data_loss"), getParameter("inference_time"), getParameter("data_processed")]
  },
  {
    application_id: "1e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674739172,
    finish: 1674739239,
    name: "dazzling_lewin",
    number: 1,
    imports: ["tf", "torch", "numpy"],
    tags: {
      Algorithm: "Linear Regression",
      Mode: "Development"
    },
    data: {
      accuracy: 0.3,
      data_loss: 0.9,
      inference_time: 0.9,
      data_processed: 160
    },
    executors: [
      "1df0f6be-99c1-4d41-9614-10ee3d1d9917",
      "2df0f6be-99c1-4d41-9614-10ee3d1d9917",
      "3df0f6be-99c1-4d41-9614-10ee3d1d9917",
      "df0f6be-99c1-4d41-9614-10ee3d1d9917"
    ],
    id: "86ad45dc-025f-4204-8261-e27383b50fcb",
    status: "failed",
    duration: 192,
    cost: 67.23,
    goals: [getParameter("accuracy"), getParameter("data_loss"), getParameter("inference_time"), getParameter("data_processed")]
  }
];

const imageRecognitionRuns = [
  {
    application_id: "2e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674739172,
    finish: 1674739239,
    name: "dazzling_lewin",
    number: 1,
    imports: ["tf", "torch", "numpy"],
    tags: {
      Algorithm: "Linear Regression",
      Mode: "Development"
    },
    data: {
      accuracy: 0.981,
      data_loss: 10,
      inference_time: 0.22,
      data_processed: 190
    },
    executors: [
      "1df0f6be-99c1-4d41-9614-10ee3d1d9917",
      "2df0f6be-99c1-4d41-9614-10ee3d1d9917",
      "3df0f6be-99c1-4d41-9614-10ee3d1d9917",
      "df0f6be-99c1-4d41-9614-10ee3d1d9917"
    ],
    id: "94cde6d1-10df-4f05-afc5-89d98332e759",
    status: "failed",
    duration: 192,
    cost: 66.87,
    goals: [getParameter("accuracy"), getParameter("data_loss"), getParameter("inference_time"), getParameter("data_processed")]
  }
];

const behaviorPredictionRuns = [
  {
    application_id: "3e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674739172,
    finish: 1674739239,
    name: "dazzling_lewin",
    number: 1,
    imports: ["tf", "torch", "numpy"],
    tags: {
      Algorithm: "Linear Regression",
      Mode: "Development"
    },
    data: {
      accuracy: 0.897,
      data_loss: 5,
      inference_time: 0.199,
      data_processed: 170,
      data_corrupted: 2
    },
    executors: [
      "1df0f6be-99c1-4d41-9614-10ee3d1d9917",
      "2df0f6be-99c1-4d41-9614-10ee3d1d9917",
      "3df0f6be-99c1-4d41-9614-10ee3d1d9917",
      "df0f6be-99c1-4d41-9614-10ee3d1d9917"
    ],
    id: "c67054fe-ebfe-4a90-9a8b-3bda0561f588",
    status: "failed",
    duration: 127,
    cost: 75.12,
    goals: [
      getParameter("accuracy"),
      getParameter("data_loss"),
      getParameter("inference_time"),
      getParameter("data_processed"),
      getParameter("data_corrupted")
    ]
  }
];

const mealsCategorizerRuns = [
  {
    application_id: "4e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674739172,
    finish: 1674739239,
    name: "dazzling_lewin",
    number: 1,
    imports: ["tf", "torch", "numpy"],
    tags: {
      Algorithm: "Linear Regression",
      Mode: "Development"
    },
    data: {
      accuracy: 1,
      inference_time: 0.199,
      data_processed: 110
    },
    executors: [
      "1df0f6be-99c1-4d41-9614-10ee3d1d9917",
      "2df0f6be-99c1-4d41-9614-10ee3d1d9917",
      "3df0f6be-99c1-4d41-9614-10ee3d1d9917",
      "df0f6be-99c1-4d41-9614-10ee3d1d9917"
    ],
    id: "12934f22-fb2c-4cf5-b327-043720a0abdb",
    status: "failed",
    duration: 55,
    cost: 61.51,
    goals: [getParameter("accuracy"), getParameter("inference_time"), getParameter("data_processed")]
  }
];

const runs = [...shoesCategorizerRuns, ...imageRecognitionRuns, ...behaviorPredictionRuns, ...mealsCategorizerRuns];

export { runs };
