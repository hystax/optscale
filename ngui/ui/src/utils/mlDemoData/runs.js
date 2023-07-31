import { getParameter, isParameterReached } from "utils/mlDemoData/parameters";

const getReachedGoal = (goalKey, value) => ({
  ...getParameter(goalKey),
  value,
  reached: isParameterReached(goalKey, value)
});

export const shoesCategorizerRuns = [
  {
    application_id: "1e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674741319,
    finish: 1674741579,
    name: "whispering_fog",
    number: 9,
    imports: ["tensorflow", "keras", "numpy"],
    tags: {
      Mode: "Development"
    },
    runset: {
      id: "0e49ebaf-0993-4116-bb4f-4257e877c572",
      name: "gentle_sky"
    },
    data: {},
    reached_goals: {
      accuracy: getReachedGoal("accuracy"),
      data_loss: getReachedGoal("data_loss"),
      inference_time: getReachedGoal("inference_time"),
      data_processed: getReachedGoal("data_processed")
    },
    executor_id: "3a3a3a3b-3b3b-4a4a-aaaa-2f2f2f2f2f2f",
    id: "c362e72e-61a7-49e8-8c7e-71093f55c7b4",
    status: "aborted",
    duration: 65,
    cost: 14,
    goals: [
      getParameter("accuracy"),
      getParameter("data_loss"),
      getParameter("inference_time"),
      getParameter("data_processed")
    ],
    status_description: {
      type: "reached_plateau",
      payload: {
        goal: "Accuracy",
        value: 0.87
      }
    },
    runset_template_id: "826f8381-9a12-4854-8274-9ca421b19856",
    hyperparameters: {
      lr: 0.01,
      bs: 32
    }
  },
  {
    application_id: "1e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674741119,
    finish: 1674741379,
    name: "relaxed_antonelli",
    number: 8,
    imports: ["tf", "torch", "numpy"],
    tags: {
      Mode: "Development"
    },
    runset: {
      id: "0e49ebaf-0993-4116-bb4f-4257e877c572",
      name: "gentle_sky"
    },
    data: {
      accuracy: 1,
      data_loss: 5,
      inference_time: 0.15,
      data_processed: 150
    },
    reached_goals: {
      accuracy: getReachedGoal("accuracy", 1),
      data_loss: getReachedGoal("data_loss", 5),
      inference_time: getReachedGoal("inference_time", 0.15),
      data_processed: getReachedGoal("data_processed", 150)
    },
    executor_id: "5f24f97c-dd38-45a0-b92a-5633ee43edbd",
    id: "76ad45dc-025f-4204-8261-e27383b50fcb",
    status: "completed",
    duration: 78,
    cost: 9.3,
    goals: [
      getParameter("accuracy"),
      getParameter("data_loss"),
      getParameter("inference_time"),
      getParameter("data_processed")
    ],
    status_description: {
      type: "goals_met"
    },
    runset_template_id: "826f8381-9a12-4854-8274-9ca421b19856",
    hyperparameters: {
      lr: 0.01,
      bs: 32
    }
  },
  {
    application_id: "1e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674740919,
    finish: 1674741079,
    name: "frosty_snowflake",
    number: 7,
    imports: ["tensorflow", "keras", "numpy"],
    tags: {
      Mode: "Development"
    },
    runset: {
      id: "0e49ebaf-0993-4116-bb4f-4257e877c572",
      name: "gentle_sky"
    },
    data: {},
    reached_goals: {
      accuracy: getReachedGoal("accuracy"),
      data_loss: getReachedGoal("data_loss"),
      inference_time: getReachedGoal("inference_time"),
      data_processed: getReachedGoal("data_processed")
    },
    executor_id: "58ffb238-4691-4a92-88d5-17d0994c1fde",
    id: "a362e72e-61a7-49e8-8c7e-71093f55c7b4",
    status: "aborted",
    duration: 201,
    cost: 12.2,
    goals: [
      getParameter("accuracy"),
      getParameter("data_loss"),
      getParameter("inference_time"),
      getParameter("data_processed")
    ],
    status_description: {
      type: "time_exceeded"
    },
    runset_template_id: "826f8381-9a12-4854-8274-9ca421b19856",
    hyperparameters: {
      lr: 0.01,
      bs: 32
    }
  },
  {
    application_id: "1e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674740719,
    finish: 1674740879,
    name: "strange_bassi",
    number: 6,
    imports: ["tf", "torch", "numpy"],
    tags: {
      Mode: "Development"
    },
    runset: {
      id: "0e49ebaf-0993-4116-bb4f-4257e877c572",
      name: "gentle_sky"
    },
    data: {},
    reached_goals: {
      accuracy: getReachedGoal("accuracy"),
      data_loss: getReachedGoal("data_loss"),
      inference_time: getReachedGoal("inference_time"),
      data_processed: getReachedGoal("data_processed")
    },
    executor_id: "595b6d7c-65b9-45b1-920c-0b6652c1dc08",
    id: "66ad45dc-025f-4204-8261-e27383b50fcb",
    status: "aborted",
    duration: 63,
    cost: 16.2,
    goals: [
      getParameter("accuracy"),
      getParameter("data_loss"),
      getParameter("inference_time"),
      getParameter("data_processed")
    ],
    status_description: {
      type: "reached_plateau",
      payload: {
        goal: "Accuracy",
        value: 0.77
      }
    },
    runset_template_id: "826f8381-9a12-4854-8274-9ca421b19856",
    hyperparameters: {
      lr: 0.01,
      bs: 32
    }
  },
  {
    application_id: "1e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674740519,
    finish: 1674740679,
    name: "dazzling_lewin",
    number: 5,
    imports: ["tf", "torch", "numpy"],
    tags: {
      Algorithm: "Linear Regression",
      Mode: "Development"
    },
    runset: {
      id: "0e49ebaf-0993-4116-bb4f-4257e877c572",
      name: "gentle_sky"
    },
    data: {
      accuracy: 0.3,
      data_loss: 0.9,
      inference_time: 0.9,
      data_processed: 160
    },
    reached_goals: {
      accuracy: getReachedGoal("accuracy", 0.3),
      data_loss: getReachedGoal("data_loss", 0.9),
      inference_time: getReachedGoal("inference_time", 0.9),
      data_processed: getReachedGoal("data_processed", 160)
    },
    executor_id: "380abb2f-dff4-417c-bcf4-c696436e93aa",
    id: "86ad45dc-025f-4204-8261-e27383b50fcb",
    status: "completed",
    duration: 45,
    cost: 11.5,
    goals: [
      getParameter("accuracy"),
      getParameter("data_loss"),
      getParameter("inference_time"),
      getParameter("data_processed")
    ],
    runset_template_id: "826f8381-9a12-4854-8274-9ca421b19856",
    hyperparameters: {
      lr: 0.01,
      bs: 32
    }
  },
  {
    application_id: "1e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674740159,
    finish: 1674740319,
    name: "neon_tundra",
    number: 4,
    imports: ["tf", "torch", "numpy"],
    tags: {
      Algorithm: "Linear Regression",
      Mode: "Development"
    },
    runset: {
      id: "fc3dd9a8-ed5b-462f-8290-5ac66272518c",
      name: "blooming_meadow"
    },
    data: {
      accuracy: 0.4,
      data_loss: 0.87,
      inference_time: 0.8,
      data_processed: 149
    },
    reached_goals: {
      accuracy: getReachedGoal("accuracy", 0.4),
      data_loss: getReachedGoal("data_loss", 0.87),
      inference_time: getReachedGoal("inference_time", 0.8),
      data_processed: getReachedGoal("data_processed", 149)
    },
    executor_id: "5f24f97c-dd38-45a0-b92a-5633ee43edbd",
    id: "58ffb238-4691-4a92-88d5-17d0994c1fde",
    status: "running",
    duration: 122,
    cost: 15.5,
    goals: [
      getParameter("accuracy"),
      getParameter("data_loss"),
      getParameter("inference_time"),
      getParameter("data_processed")
    ],
    runset_template_id: "826f8381-9a12-4854-8274-9ca421b19856",
    hyperparameters: {
      lr: 0.01,
      bs: 32
    }
  },
  {
    application_id: "1e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674739799,
    finish: 1674739959,
    name: "quirky_ritchie",
    number: 3,
    imports: ["tf", "torch", "numpy"],
    tags: {
      Algorithm: "Linear Regression",
      Mode: "Development"
    },
    runset: {
      id: "d4264062-969c-4851-9453-89da80881521",
      name: "wandering_moon"
    },
    data: {},
    reached_goals: {
      accuracy: getReachedGoal("accuracy"),
      data_loss: getReachedGoal("data_loss"),
      inference_time: getReachedGoal("inference_time"),
      data_processed: getReachedGoal("data_processed")
    },
    executor_id: "380abb2f-dff4-417c-bcf4-c696436e93aa",
    id: "176a9c18-a347-4d10-8992-2ca96cc2afc2",
    status: "failed",
    duration: 142,
    cost: 12.5,
    goals: [
      getParameter("accuracy"),
      getParameter("data_loss"),
      getParameter("inference_time"),
      getParameter("data_processed")
    ],
    runset_template_id: "826f8381-9a12-4854-8274-9ca421b19856",
    hyperparameters: {
      lr: 0.01,
      bs: 32
    }
  },
  {
    application_id: "1e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674739439,
    finish: 1674739599,
    name: "peaceful_bell",
    number: 2,
    imports: ["tf", "torch", "numpy"],
    tags: {
      Algorithm: "Linear Regression",
      Mode: "Development"
    },
    runset: {
      id: "d4264062-969c-4851-9453-89da80881521",
      name: "wandering_moon"
    },
    data: {
      accuracy: 0.7,
      data_loss: 0.5,
      inference_time: 0.6,
      data_processed: 190
    },
    reached_goals: {
      accuracy: getReachedGoal("accuracy", 0.7),
      data_loss: getReachedGoal("data_loss", 0.5),
      inference_time: getReachedGoal("inference_time", 0.6),
      data_processed: getReachedGoal("data_processed", 190)
    },
    executor_id: "5f24f97c-dd38-45a0-b92a-5633ee43edbd",
    id: "380abb2f-dff4-417c-bcf4-c696436e93aa",
    status: "running",
    duration: 142,
    cost: 12.5,
    goals: [
      getParameter("accuracy"),
      getParameter("data_loss"),
      getParameter("inference_time"),
      getParameter("data_processed")
    ],
    runset_template_id: "826f8381-9a12-4854-8274-9ca421b19856",
    hyperparameters: {
      lr: 0.01,
      bs: 32
    }
  },
  {
    application_id: "1e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674739172,
    finish: 1674739239,
    name: "blissful_bell",
    number: 1,
    imports: ["tensorflow", "keras", "numpy"],
    tags: {
      Mode: "Development"
    },
    runset: {
      id: "0e49ebaf-0993-4116-bb4f-4257e877c572",
      name: "gentle_sky"
    },
    data: {},
    reached_goals: {
      accuracy: getReachedGoal("accuracy"),
      data_loss: getReachedGoal("data_loss"),
      inference_time: getReachedGoal("inference_time"),
      data_processed: getReachedGoal("data_processed")
    },
    executor_id: "3a3a3a3b-3b3b-4a4a-aaaa-2f2f2f2f2f2f",
    id: "fa8a5233-582b-41c6-a321-9c831675cdcf",
    status: "failed",
    duration: 125,
    cost: 10,
    goals: [
      getParameter("accuracy"),
      getParameter("data_loss"),
      getParameter("inference_time"),
      getParameter("data_processed")
    ],
    runset_template_id: "826f8381-9a12-4854-8274-9ca421b19856",
    hyperparameters: {
      lr: 0.01,
      bs: 32
    }
  }
];

export const imageRecognitionRuns = [
  {
    application_id: "2e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674739439,
    finish: 1674739599,
    name: "neon_zebra",
    number: 3,
    imports: ["tf", "torch", "numpy"],
    tags: {
      Algorithm: "Linear Regression",
      Mode: "Development"
    },
    runset: {
      id: "ee57963c-e678-4d28-afee-612ef5ba3a4b",
      name: "solar_gorilla"
    },
    data: {},
    reached_goals: {
      accuracy: getReachedGoal("accuracy"),
      data_loss: getReachedGoal("data_loss"),
      inference_time: getReachedGoal("inference_time"),
      data_processed: getReachedGoal("data_processed")
    },
    executor_id: "3e94c1da-e9fd-40bb-a075-4136806d2464",
    id: "9bfaaee6-7280-426c-90f8-89c01c08d2d3",
    status: "failed",
    duration: 192,
    cost: 16.2,
    goals: [
      getParameter("accuracy"),
      getParameter("data_loss"),
      getParameter("inference_time"),
      getParameter("data_processed")
    ],
    runset_template_id: "ac2adbf7-0793-475d-932c-6a899ceb9c30",
    hyperparameters: {
      lr: 0.01,
      bs: 32
    }
  },
  {
    application_id: "2e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674739172,
    finish: 1674739239,
    name: "jovial_beaver",
    number: 2,
    imports: ["tf", "torch", "numpy"],
    tags: {
      Algorithm: "Linear Regression",
      Mode: "Development"
    },
    runset: {
      id: "ee57963c-e678-4d28-afee-612ef5ba3a4b",
      name: "solar_gorilla"
    },
    data: {
      accuracy: 0.931,
      data_loss: 8,
      inference_time: 0.12,
      data_processed: 186
    },
    reached_goals: {
      accuracy: getReachedGoal("accuracy", 0.931),
      data_loss: getReachedGoal("data_loss", 8),
      inference_time: getReachedGoal("inference_time", 0.12),
      data_processed: getReachedGoal("data_processed", 186)
    },
    executor_id: "3e94c1da-e9fd-40bb-a075-4136806d2464",
    id: "94cde6d1-10df-4f05-afc5-89d98332e759",
    status: "completed",
    duration: 192,
    cost: 11.7,
    goals: [
      getParameter("accuracy"),
      getParameter("data_loss"),
      getParameter("inference_time"),
      getParameter("data_processed")
    ],
    runset_template_id: "ac2adbf7-0793-475d-932c-6a899ceb9c30",
    hyperparameters: {
      lr: 0.01,
      bs: 64
    }
  },
  {
    application_id: "2e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674739172,
    finish: 1674739239,
    name: "golden_peak",
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
    reached_goals: {
      accuracy: getReachedGoal("accuracy", 0.931),
      data_loss: getReachedGoal("data_loss", 10),
      inference_time: getReachedGoal("inference_time", 0.22),
      data_processed: getReachedGoal("data_processed", 190)
    },
    executor_id: "3e94c1da-e9fd-40bb-a075-4136806d2464",
    id: "b3fe0187-703a-4e67-a555-c5a70bf64bc5",
    status: "completed",
    duration: 192,
    cost: 12.7,
    goals: [
      getParameter("accuracy"),
      getParameter("data_loss"),
      getParameter("inference_time"),
      getParameter("data_processed")
    ],
    runset_template_id: "ac2adbf7-0793-475d-932c-6a899ceb9c30",
    hyperparameters: {
      lr: 0.01,
      bs: 64
    }
  }
];

export const behaviorPredictionRuns = [
  {
    application_id: "3e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674739439,
    finish: 1674739599,
    name: "daring_babbage",
    number: 2,
    imports: ["tf", "torch", "numpy"],
    tags: {
      Algorithm: "Linear Regression",
      Mode: "Development"
    },
    runset: {
      id: "f253907d-0ae1-4a37-b441-ea060c4a9f80",
      name: "thunder_dragon"
    },
    data: {
      accuracy: 0.897,
      data_loss: 5,
      inference_time: 0.199,
      data_processed: 170,
      data_corrupted: 2
    },
    reached_goals: {
      accuracy: getReachedGoal("accuracy", 0.897),
      data_loss: getReachedGoal("data_loss", 5),
      inference_time: getReachedGoal("inference_time", 0.199),
      data_processed: getReachedGoal("data_processed", 170),
      data_corrupted: getReachedGoal("data_processed", 2)
    },
    executor_id: "8244430a-6f7b-4545-a067-3cacb97ac402",
    id: "c67054fe-ebfe-4a90-9a8b-3bda0561f588",
    status: "completed",
    duration: 127,
    cost: 10.9,
    goals: [
      getParameter("accuracy"),
      getParameter("data_loss"),
      getParameter("inference_time"),
      getParameter("data_processed"),
      getParameter("data_corrupted")
    ],
    runset_template_id: "5c7b5a5a-866e-4916-adc4-b56a1f1adb0a",
    hyperparameters: {
      lr: 0.01,
      bs: 32
    }
  },
  {
    application_id: "3e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674739172,
    finish: 1674739239,
    name: "flamboyant_roentgen",
    number: 1,
    imports: ["tf", "torch", "numpy"],
    tags: {
      Algorithm: "Linear Regression",
      Mode: "Development"
    },
    runset: {
      id: "f253907d-0ae1-4a37-b441-ea060c4a9f80",
      name: "thunder_dragon"
    },
    data: {
      accuracy: 0.687,
      data_loss: 7,
      inference_time: 0.299,
      data_processed: 172,
      data_corrupted: 3
    },
    reached_goals: {
      accuracy: getReachedGoal("accuracy", 0.687),
      data_loss: getReachedGoal("data_loss", 7),
      inference_time: getReachedGoal("inference_time", 0.299),
      data_processed: getReachedGoal("data_processed", 172),
      data_corrupted: getReachedGoal("data_processed", 3)
    },
    executor_id: "32bf7a4c-df92-464c-b356-4311e82149b8",
    id: "e581d2fc-aa78-441e-930f-994630bac526",
    status: "completed",
    duration: 102,
    cost: 15.9,
    goals: [
      getParameter("accuracy"),
      getParameter("data_loss"),
      getParameter("inference_time"),
      getParameter("data_processed"),
      getParameter("data_corrupted")
    ],
    runset_template_id: "5c7b5a5a-866e-4916-adc4-b56a1f1adb0a",
    hyperparameters: {
      lr: 0.01,
      bs: 64
    }
  }
];

export const mealsCategorizerRuns = [
  {
    application_id: "4e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674739172,
    finish: 1674739239,
    name: "silver_dawn",
    number: 3,
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
    reached_goals: {
      accuracy: getReachedGoal("accuracy", 1),
      inference_time: getReachedGoal("inference_time", 0.199),
      data_corrupted: getReachedGoal("data_processed", 110)
    },
    executor_id: "ffff0f8e-4ec4-4e9c-bfe8-c0f0adbbc5a7",
    id: "a7cf4aa8-6c28-4085-af05-7980406ea919",
    status: "completed",
    duration: 55,
    cost: 8.9,
    goals: [getParameter("accuracy"), getParameter("inference_time"), getParameter("data_processed")],
    hyperparameters: {}
  },
  {
    application_id: "4e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674738972,
    finish: 1674739039,
    name: "starry_butterfly",
    number: 2,
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
    reached_goals: {
      accuracy: getReachedGoal("accuracy", 1),
      inference_time: getReachedGoal("inference_time", 0.199),
      data_corrupted: getReachedGoal("data_processed", 110)
    },
    executor_id: "ffff0f8e-4ec4-4e9c-bfe8-c0f0adbbc5a7",
    id: "1e1c303c-70fd-4405-9383-8b177ec0254e",
    status: "completed",
    duration: 78,
    cost: 10.05,
    goals: [getParameter("accuracy"), getParameter("inference_time"), getParameter("data_processed")],
    hyperparameters: {}
  },
  {
    application_id: "4e0815a2-72d2-418b-afad-bedc99a5e9d2",
    start: 1674738772,
    finish: 1674738839,
    name: "cosmic_turtle",
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
    reached_goals: {
      accuracy: getReachedGoal("accuracy", 1),
      inference_time: getReachedGoal("inference_time", 0.199),
      data_corrupted: getReachedGoal("data_processed", 110)
    },
    executor_id: "ffff0f8e-4ec4-4e9c-bfe8-c0f0adbbc5a7",
    id: "7eb904d7-3b4f-46bc-a4e3-441c85fd375a",
    status: "completed",
    duration: 90,
    cost: 15.05,
    goals: [getParameter("accuracy"), getParameter("inference_time"), getParameter("data_processed")],
    hyperparameters: {}
  }
];

const runs = [...shoesCategorizerRuns, ...imageRecognitionRuns, ...behaviorPredictionRuns, ...mealsCategorizerRuns];

export { runs };
