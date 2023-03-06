API quickstart 

1.Create Goal

```
curl -k -L -d '{"target_value": 0.9, "tendency": "less", "name": "loss", "display_name": "model loss"}' -H "x-api-key: test" -H "Content-Type: application/json" -X POST https://localhost:443/arcee/v2/goals
{"_id":"e0a3f3ab-fa75-4795-863d-bf16fe1857bf","display_name":"model loss","tendency":"less","target_value":0.9,"name":"loss","function":null,"token":"test"}
```

2.Create Application

```
curl -k -L -d '{"key":"test"}' -H "x-api-key: test" -H "Content-Type: application/json" -X POST https://localhost:443/arcee/v2/applications
```

3.Assign Goal to Application

```
curl -k -L -d '{"display_name":"Test123", "goals": ["e0a3f3ab-fa75-4795-863d-bf16fe1857bf"]}' -H "x-api-key: test" -H "Content-Type: application/json" -X PATCH https://localhost:443/arcee/v2/applications/test
```
4.Get application runs

```
curl -k -L -H "x-api-key: test" -H "Content-Type: application/json" -X GET https://localhost:443/arcee/v2/applications/test/run
```
example response:
```
[
  {
    "_id": "fca0970b-16a4-4e69-a469-e80adeba5fec",
    "key": "test",
    "token": "test",
    "display_name": "Test123",
    "goals": "e0a3f3ab-fa75-4795-863d-bf16fe1857bf",
    "applicationGoals": [
      {
        "_id": "e0a3f3ab-fa75-4795-863d-bf16fe1857bf",
        "display_name": "model loss",
        "tendency": "less",
        "target_value": 0.9,
        "name": "loss",
        "function": null,
        "token": "test"
      }
    ],
    "runs": [
      {
        "_id": "5316f319-f17a-4102-af04-6a76671ac686",
        "application_id": "fca0970b-16a4-4e69-a469-e80adeba5fec",
        "start": 1665528835,
        "finish": 1665527774,
        "state": 2,
        "number": 1,
        "tags": {
          "key": "value",
          "project": "regression"
        },
        "data": {
          "step": 2000,
          "loss": "0.153899"
        },
        "executors": [
          "i-09dc9f5553f84a9ad"
        ]
      },
      {
        "_id": "d36bbf44-ecde-404d-a746-153dc1eb355f",
        "application_id": "fca0970b-16a4-4e69-a469-e80adeba5fec",
        "start": 1665529738,
        "finish": 1665528656,
        "state": 2,
        "number": 2,
        "tags": {
          "key": "value",
          "project": "regression"
        },
        "data": {
          "step": 2000,
          "loss": "0.153858"
        },
        "executors": [
          "i-09dc9f5553f84a9ad"
        ]
      }
    ]
  }
]
```