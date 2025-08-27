import win32com.client, time
from time import sleep

cfg_file_1 = r'C:\CanOeService\cfg\MMA_Updated\BODY1_15.cfg'
cfg_file_2 = r'C:\CanOeService\cfg\DCM223_Updated\BODY1_15.cfg'
canoe_exe = 'CANoe64.exe'

# Create app
app = win32com.client.Dispatch("CANoe.Application")
app.Visible = False
app.Open(cfg_file_1)

cfg_loaded = False
attempt = 0
while attempt < 10:
    try:
        name = app.Configuration.Name
        full = app.Configuration.FullName
        
        if name != '' and name is not None:
            
            print(name)
            print(full)
            cfg_loaded = True
            break
        
        
    except Exception as e:
        print (e)
    finally:
        print(attempt)
        attempt = attempt + 1
        sleep(2.0)

# Check if measurement
if cfg_loaded:
    if not app.Measurement.Running:
        print('Arrancando...')
        app.Measurement.Start()
        print('Arrancado!')
        sleep(2.0)

print("Fin")