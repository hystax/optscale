# Arcee
## _The OptScale ML profiling tool by Hystax_


Arcee is a tool that hepls you to integrate ML tasks with [OptScale](https://my.optscale.com/).
This tool can automatically collect executor metadata from cloud and process stats.
 
## Installation
Arcee requires python 3.7+ to run. 
```sh
pip install optscale-arcee
```
## Usage

First of all you need to import and init arcee in your code:
```sh
import optscale_arcee as arcee
```

```sh
# init arcee
arcee.init('token', 'application_key')
```

To use custom endpoint and enable\disable ssl checks (supports using self-signed ssl certificates):
```sh
arcee.init('token', 'application_key', endpoint_url='https://my.custom.endpoint:443/arcee/v2', ssl=False)
```

To send stats:
```sh
arcee.send({"loss": 2.0012, "iter": 2, "epoch": 1})
```
(key should be string, value - int or float, multiple values can be sent)

To add tags to application run (key, value):
```sh
arcee.tag("project", "torchvision demo")
```
To add milestones:
```sh
arcee.milestone("Download test data")
```
To add stages:
```sh
arcee.stage("calculation")
```
To finish model:
```sh
arcee.finish()
```
or for failed task:
```sh
arcee.error()
```
