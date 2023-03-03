const parameters = [
  {
    name: "Accuracy",
    tendency: "more",
    target_value: 0.999,
    key: "accuracy",
    func: "last",
    id: "accuracy"
  },
  {
    name: "Data processed",
    tendency: "less",
    target_value: 150,
    key: "data_processed",
    func: "max",
    id: "data_processed"
  },
  {
    name: "Inference time",
    tendency: "less",
    target_value: 0.2,
    key: "inference_time",
    func: "avg",
    id: "inference_time"
  },
  {
    name: "Data Loss",
    tendency: "less",
    target_value: 10,
    key: "data_loss",
    func: "sum",
    id: "data_loss"
  },
  {
    name: "Data corrupted",
    tendency: "less",
    target_value: 0,
    key: "data_corrupted",
    func: "avg",
    id: "data_corrupted"
  }
];

const getParameter = (key) => parameters.find((parameter) => key === parameter.key);

const getParameters = () => parameters;

export { parameters, getParameter, getParameters };
