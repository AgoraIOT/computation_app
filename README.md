![](docs/badge.png) ![Python](https://img.shields.io/badge/Python-3.12-yellow?logo=python&logoColor=blue) ![Node.js](https://img.shields.io/badge/Node.js-20.x-green?logo=node.js&logoColor=white)


# Computation app
This is an example application **Computation App** build using **Agora<sup>™</sup>Edge AI and IoT** SDK. 

The project demonstrates a typical development workflow, starting with running the application locally in a simulated environment using the pulser application and mock data :chart_with_upwards_trend: file  `./sim-data/Pulser_Minimal_Data.xlsx`. This approach allows developers to validate functionality and iterate quickly before deploying to real systems. 

The application is intended to serve as a reference for building edge applications, with the goal of subsequent deployment to **Agora<sup>™</sup>Edge AI and IoT** IoT devices. 

# Getting Started
## Prerequisites
Required to be installed:
- docker >= 28
- git >= 2.34
## Installation
```bash
git clone https://github.com/AgoraIOT/computation_app.git
```
# Usage
## Run
Build and up all required containers
```bash
docker compose up --build 
```
the pulser app dashboard
```bash
http://localhost:9443
```
## Workflow
The app simulates periodic data coming from an edge device. The data is broadcast via messages sent to NATS topics. Applications that subscribe to those topics would receive the messages and do some processing of the data before sending a report (IoDataReport) to the cloud. The UI (Pulser dashboard) visually represents an app receiving messages from the device. Those incoming messages are then aggreggated into reports that are sent to another NATS topic.

## Modification
This application is designed to be easily adapted for custom data replay and computation logic. The main customization points are simulation data, application configuration, and computation logic.

### Introduce your own replay data
Replay data is provided through the pulser component using the Excel file located at:

[./sim-data/Pulser_Minimal_Data.xlsx](/sim-data/Pulser_Minimal_Data.xlsx)

To introduce your own data:
- You may create additional tabs (worksheets) as needed. Do not move or rename the first tab
- Each tab represents a dataset and must follow this structure:
  - First row: channel (tag) names
  - Subsequent rows: timestamped values
- In the Configuration tab:
  - Set the name of the default dataset to display in cell B3

This data is replayed into the NATS message bus and consumed by the computation application as IODataReport messages.

### Adapt application configuration (instance-specific)
Instance-specific parameters are defined in:

```bash
AEA.json
```

Using the AppConfig / AppSettings section, you can customize the behavior of each deployed instance without changing the code. Typical configuration parameters include:
- Constant factors used in calculations
- Names of expected input channels
- Names of output channels to be published
These settings are resolved at runtime and allow the same container image to be reused across multiple deployments with different configurations.

### Modify the computation logic
The core computation logic is implemented in:

```bash
./src/computation_example.py
```

The application processes incoming IODataReport messages from the bus, extracts the configured input channels, and computes derived values.

By default, the example performs simple arithmetic operations (e.g. average and difference) using a configurable factor. You can extend or replace this logic to implement:

- Domain-specific calculations
- Aggregations or transformations
- Validation or filtering of incoming data

Only the computation logic needs to be changed; message transport, subscription handling, and publishing are managed by the SDK integration.

## Known issues
- :warning: when opening the browser, data is not flowing right away (seen with podman/windows)
  - workaround: load the file `./sim-data/Pulser_Minimal_Data.xlsx` manually on the website using the `browse` button
# App deployment to Agora IoT device
Scan QR code below and submit request for an app deployment
<p align="center">
  <img src="docs/qr-link.png" alt="QR code" width="220"/>
</p>

# Contribute
As a user of this repository, feel free to provide feedback - bugs or fixes - to the repo contributors (see commits)
# License
AGORA SOFTWARE DEVELOPMENT KIT LICENSE

See LICENSE file for more details.