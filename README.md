# CANoe Proxy Service

Proyecto: Técnicas IDE
Autor: Christian Yáñez (YF-Controls)

## Tabla de contenidos

1. [Instalación básica](#1-basic-installation)
2. [Service Installation](#2-service-installation)
3. [Commands & Responses](#3-commands--responses)

## 1. Instalación básica

### 1.1. Descarga

* vscode
* python v3.13.2 os last version of v3.13.x
* chrome
* CANoe v15 SP6 64Bit

### 1.2. Configuración de Powershell

Abra PowerShell como __administrador__

```PowerShell
Get-ExecutionPolicy
Set-ExecutionPolicy Unrestricted
Yes
```

### 1.3. Instalación

1. Chrome
2. vscode, open and install these packages
     1. autoDocstring - Python documentations (Nils Werner)
     2. Markdown Preview Enhanced (Yiyi Wang).
     3. Pylance (Microsoft).
     4. Python  (Microsoft).
     5. Python Debugger  (Microsoft).
     6. Python Indent (Kevin Rose).
3. python as __local user__
4. CANoe v15 SP6 64Bit

### 1.4. Instalación de paquetes de Python

Abra la `consola de comandos` como administrador

```Python
python.exe -m  pip install --upgrade pip
pip install pywin32
pip install psutil
pip install py_canoe
```

## 2. Instalación del servicio

### 2.1. Instalación

Para instalar el servicio vaya a la ruta donde se encuentra `canoe_proxy_service.py`, por defecto debería estar en `c:\CANoeProxy\`.

Abra la `consola de comandos` como administrador.

Ejecute el siguiente código:

```Python
python canoe_proxy_service.py install
```

De forma manual continuaremos con la configuración:

Seguir manual en `doc/A06_ConfigService`



### 2.2. Uninstall service

Para desinstalar el servicio abra la `consola de comandos` como administrador.

Ejecute el siguiente código:

```Python
python canoe_proxy_service.py remove
```

En caso de que no se pueda eliminar el servicio con python, abra la  `consola de comandos`como administrador.

Ejecute el siguiente código:

```Cmd
sc delete "Nombre del servicio tal como está en la UI de Servicios"
```

> Si el nombre del comando lleva espacios se ha de poner entre comillas


### 2.3. Configurar el servicio en Windows Services

1. Abrir `Services`
2. Busque `CANoe Proxy Service`
3. Habilitar como `auto`
4. Clic en `Log On`
5. Check en `Local system account`
6. Check en `allow service to interact with desktop`

### 2.4. El Visor de Eventos

1. Abra `Event viewer`
2. Vaya a `Windows logs`
3. Vaya a `Application`
4. Busque `CANoe Proxy Service`

### 2.5. Configuración de Windows para habilitar el acceso remoto al Servicio y a Vector CANoe.exe

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

## 3. Comandos para los Paneles de Vector CANoe.exe

Palabras clave para entender los comandos.

`DCU`: Controlador de la puerta.

`sw`: Versión del software de la `DCU`.

`hw`: Versión del hardware de la `DCU`.

`sn`: Número de serie de la `DCU`.

Lista de tipos de la `DCU` para `MMA`:

| dcu_type | descripción |
|:---------|:------------|
| `DMFL_MMA` | Puerta delantera izquierda (conductor) |
| `DMFR_MMA` | Puerta delantera derecha (pasajero) |
| `DMRL_MMA` | Puerta trasera izquierda (pasajero) |
| `DMRR_MMA` | Puerta trasera derecha (pasajero) |

Lista de tipos de la `DCU` para `223`:

| dcu_type | descripción |
|:---------|:------------|
| `DMD223` | Puerta delantera izquierda (conductor) |
| `DMP223` | Puerta delantera derecha (pasajero) |
| `DMRL223` | Puerta trasera izquierda (pasajero) |
| `DMRR223` | Puerta trasera derecha (pasajero) |

### 3.1. Comando: `Read_info`

Este comando hace la petición a la `DCU` para obtener `sw`, `hw`, `sn`.

El parámetro `dcu_type` es requerido.

* PLC command: `Read_info {dcu_tpye}`
* Vector response:

| level | response | description |
|:------|:---------|:------------|
| Done | `{sw},{hw},{sn}` | String con `sw`, `hw` y `sn`separados por comas |
| Error | `Set_target ZenzefiError` | Fallo de autentificación |
| Error | `Set_target ERROR Target not connected` | Fallo al no encontrar `DCU` |
| Error | `Set_target ERROR Invalid command` | Comando no válido |

### 3.2. Comando: `Window_control`

Este comando sirve para subir, bajar y parar la ventana conectada a la `DCU`.

El parámetro `action`es requerido:

| action | description |
|:-------|:------------|
| `UP` | Orden para subir la ventana |
| `DOWN` | Orden para bajar la ventana |
| `STOP` | Orden para parar la ventana |

* PLC command: `Window_control {action}`
* Vector response:

| level | response | description |
|:------|:---------|:------------|
| Done | `Action_type {action} {dcu_type} OK` | El comando ha sido procesado correctamente |
| Error | `Set_target ERROR Target not connected` | Fallo al no encontrar `DCU` |
| Error | `Set_target ERROR Invalid command` | Comando no válido |

__Importante__: La respuesta para este comando no significa que se está ejecutando la acción sino que el comando ha sido procesado correctamente.

### 3.3. Comando: `DLK_IOControl`

Este comando sirve para bloquear o desbloquear una puerta conectada a la `DCU`.

El parámetro `action` es requerido:

| action | description |
|:-------|:------------|
| `LOCK` | Orden para bloquear la puerta |
| `UNLOCK` | Orden para desbloquear la puerta |

* PLC command: `DLK_IOControl {action}`
* Vector response:

| level | response | description |
|:------|:---------|:------------|
| Done | `DLK_IOControl {action} {dcu_type} OK` | El comando ha sido procesado correctamente |
| Error | `Set_target ERROR Target not connected` | Fallo al no encontrar `DCU` |
| Error | `Set_target ERROR Invalid command` | Comando no válido |

__Importante__: La respuesta para este comando no significa que se está ejecutando la acción sino que el comando ha sido procesado correctamente.

## 4. Comandos del servicio CANoe Proxy

Palabras clave para entender los comandos.

`cfg_id`: Es el identificador del Panel que se quiere abrir. `cfg_id` está descrito en el fichero `config.json` en `canOe` > `cfgs` > `id`

`cfg_path`: Es la ruta donde el ficher .cfg del Panel está almacenado, la referencia a este fichero está descrita en el fichero `config.json` en `canOe` > `cfgs` > `path`

`canoe_exe`: Es el nombre del ejecutable de Vector CANoe.exe, la referencia a este fichero está descrita en el fichero `config.json` en `canOe` > `exe`

### 4.1. Comando: `help`

Este comando muestra los comandos disponibles para este servicio.

* PLC command: `help`
* Service response:

| level | response |
|:------|:---------|
| Done  | `0000,Available commands: status, start {cfg_id}, close, help` |

### 4.2. Comando: `status`

Este comando muestra el estado de `Vector CANoe.exe`

* PLC command: `status`
* Service response:

| level | response |
|:------|:---------|
| Done | `0000,{cfg_id} {cfg_file} measurement running` |
| Warning | `7000,{canoe_exe} closed` |
| Warning | `7001,No cfg file loaded` |
| Warning | `7002,{cfg_id} {cfg_file} waiting to start measurement` |
| Error | `8000,Too many open {canoe_exe} instances` |

### 4.3. Comando: `start`

Este comando inica una medición en `Vector CANoe.exe` con el fichero `cfg_path` cargado.

`start` necesita un argumento `cfg_id`.

* PLC command: `start {cfg_id}`
* Service response:

| level | response |
|:------|:---------|
| Done | `0000,{cfg_id} {cfg_file} measurement running` |
| Error | `8100,Missing parameters` |
| Error | `8101,Too many parameters` |
| Error | `8102,Unknown cfg_id: {cfg_id}` |
| Error | `8110,{cfg_id} Impossible to start measurement, file: {cfg_path}` |
| Error | `8111,{cfg_id} Some error when opening file {cfg_path}` |

### 4.4 Comando: `close`

Este comando cierra inmediatamente `Vector CANoe.exe`.

* PLC command: `close`
* Service response:

| level | response |
|:------|:---------|
| Done | `0000,{canoe.exe} closed`|
| Error | `8200,Impossible to close {canoe_exe}. Force manually!` |

### 4.5. Comando desconocido

* PLC command: `random text as command`
* Service response:

| level | response |
|:------|:---------|
| Error | `8FFF,Unknown command` |

## 5. Conexión y comunicación con Vector CANoe.exe y CANoe Proxy Service

Para poder comunicar con el `servicio` y con `CANoe` el `PLC` necesita crear dos `sockets clientes TCP`.

Un socket sirve para comunicar con el `servicio` a través del puerto `3000`. Este puerto se puede configurar en el fichero `config.json` en `service` > `port`. También es posible limitar el adaptador de red por el que va a escuchar en `service` > `host`, recuerde que `0.0.0.0` habilita la escucha por todos los adaptadores de red del PC.

El otro socket sirve para comunicar con `CANoe` una vez arrancado gracias al `servicio`, aunque en `config.json` se puede configurar el puerto del servidor para cada fichero `cfg` en `canOe` > `cfgs` > `port`, el puerto está definido internamente en el fichero `cfg` facilitado por `ANTOLIN`.

Ejemplo de secuencia de comandos:

```Python
# Service socket: 3000
PLC command: start MMA
response: 0000,MMA c:\CANoeProxy\cfg\MMA_Updated\BODY1_15.cfg measurement running

# CANoe socket: 4242
PLC command: Read_info DMFR_MMA
response: xxxx,yyyy,zzzzzz

```

## 6. Otros

### Cableado DB9

[Enlace de vector para el cableado](https://support.vector.com/kb?sys_kb_id=9ef442e41b2614148e9a535c2e4bcb69&id=kb_article_view&sysparm_rank=5&sysparm_tsqueryId=b046dd80fbe22a542430f55dbeefdcf7)

Resistencia 120 ohms entr 1 y 8

```
Channel (a)1 (can/lin) (este es el canal que va a la puerta)
DB9 --------------------------------> DCU
can L 2 (marron)             pin 1 (gris)
gnd   3 blanco               
can H 7 (verde)              pin 2 (verde)
```

```
Channel (b)3 (can)
DB9 --------------------------------> DCU
can L 1 (marron)             pin 1 (gris)
gnd   6 blanco               
can H 8 (verde)              pin 2 (verde)
```

### Zenzefi

Hacer login offline de vez en cuando.

Hacer pantalla de advertencia para que el operario
haga login offline.

web: https://127.0.0.1:61000/#/zenzefi/ui/error/401
Usuario: S1AZENZE
Contraseña: GA0525,Prod

### HMI

Usuario: admin
Contraseña: ide

### Formatos de log

```Python
"%(asctime)s [%(levelname)-8s] %(message)-80s [%(name)s , %(funcName)s , %(lineno)d]"
"%(asctime)s [%(levelname)-8s] [%(name)s , %(funcName)s , %(lineno)d] %(message)s"
```

### Github

Para actualizar el repositorio desde `Github` hay que hace un `pull`.
