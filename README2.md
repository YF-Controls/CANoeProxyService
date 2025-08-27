# Can Oe Service

Project: Técnicas IDE
Author: Christian Yáñez (YF-Controls)

## Table of contents

1. [Basic Installation](#1-basic-installation)
2. [Service Installation](#2-service-installation)
3. [Commands & Responses](#3-commands--responses)

## 1. Basic Installation

### 1.1. Download

* vscode
* python v3.13.2 os last version of v3.13.x
* chrome
* CANoe v15 SP6 64Bit

### 1.2. Powershell settings

Open PowerShell as admin

```PowerShell
Get-ExecutionPolicy
Set-ExecutionPolicy Unrestricted
Yes
```

### 1.3. Install

1. Chrome
2. vscode, open and install these packages:
  2.1. autoDocstring - Python documentations (Nils Werner)
  2.2. Markdown Preview Enhanced (Yiyi Wang)
  2.3. Pylance (Microsoft)
  2.4. Python  (Microsoft)
  2.5. Python Debugger  (Microsoft)
  2.6. Python Indent (Kevin Rose)
3. python as __local user__
4. CANoe v15 SP6 64Bit

### 1.4. Open cmd as admin

```Python
python.exe -m  pip install --upgrade pip
pip install pywin32
pip install psutil
pip install py_canoe
```

## 2. Service Installation

Service installation steps

### 2.1. Install service

Open cmd in can_oe_service.py path and type:

```Python
python can_oe_service.py install --config "C:\CanOeService\config.json"
python can_oe_service.py start
python can_oe_service.py status
```

### 2.2. Uninstall service

Open cmd in can_oe_service.py path and type:

```Python
python can_oe_service.py remove
```

### 2.3. Service settings in Windows Services

1. Open services
2. look for CanOe service
3. enable as auto
4. Click on Log On
5. Check Local system account
6. Check allow service to interact with desktop

### 2.4. Event viewer

1. Go to Event viewer
2. Windows logs
3. Application
4. look for CanOe events

Open vscode
Config vscode
ctrl + ñ to open power shell in vscode

Enable remote access to TCP Server

1. Open Windows Defender Firewall with Advanced Security
2. Go to inbound rules
3. New Rule
4. Select Port
5. Select TCP
6. Specific local ports: 3000 or same port in config.json
7. Allow the connection
8. Check domain, Private, Public
9. Set name: Can Oe Handler
10. Finish

## 3. Commands & Responses

### 3.1. Unknown command

* PLC command: `random text as command`
* Service response: `8FFF,Unknown command`

### 3.2. Command: status

* PLC command: `status`
* Service response:

| response | help |
|:---------|:-----|
| 0000,{cfg_id} in measurement | cfg_id is the configured canOe.cfgs[].id in config.json |
| 8010,No cfg file in measurement | |
| 8011,Unknown cfg file in measurement: {file_path}  | |

### 3.3. Command: `start-app`

* PLC command: `start-app {cfg_id}`
* Service response:

| response | help |
|:---------|:-----|
| 0000,{cfg_id} in measurement | cfg_id is the configured canOe.cfgs[].id in config.json |
| 8000,Missing parameters | |
| 8001,Too many parameters | |
| 8002,Unknown cfg_id {cfg_id} | |
| 8003,Imposible to start {cfg_id} | |

## 3.4. Command: `canoe-cmd`

* PLC command: `canoe-cmd {timeout} {CanOeCommand} {CanOeParameter}`

| Model | DCU type | description |
|:------|:----------|:------------|
| MMA* | DMFL_MMA | Front left door |
| MMA* | DMFR_MMA | Front right door |
| MMA* | DMRL_MMA | Rear left door |
| MMA* | DMRR_MMA | Rear right door |
| 223* | DMD223 | Front driver door |
| 223* | DMP223 | Front passanger door |
| 223* | DMRL223 | Rear left door |
| 223* | DMRR223 | Rear right door |

| CANoe command | CANoe responses | description |
|:--------------|:---------------|:------------|
| Read_info {dcu_type} | - {sw},{hw},{sn}<br>- Set_target ERROR Target not connected<br>- Set_target ERROR Invalid Command<br>- Set_target ZenzefiError | Request DCU data: software version, hardware version and serial number |
| Window_control {action} | - Action_type {action} {dcu_type} OK<br>- Set_target ERROR Target not connected<br>- Set_target ERROR Invalid command | Command to move up/down/stop window |
| DLK_IOControl {action} | DLK_IOControl {action} {dcu_type} OK<br>- Set_target ERROR Target not connected<br>- Set_target ERROR Invalid command | Command to lock/unlock door |

* Service response:

| response | help |
|:---------|:-----|
| 0000,{CanOeResponse} | |
| | |
| 8000,Missing parameters | |
| 8001,Too many parameters | |
| | |
| 8010,No cfg file in measurement | |
| 8011,Unknown cfg file in measurement: {cfg_path} | |
| | |
| 8040,Connection error to CANoe application | |
| 8041,Timeout error from CANoe application | |
| 8042,Unexpected error with CANoe application | |
