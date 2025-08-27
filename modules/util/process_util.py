import psutil
import subprocess
import servicemanager
import time

'''
This module provides utility functions for process management, including checking if an application is running, listing applications, closing applications, and starting new processes.
It uses the psutil library for process management and subprocess for starting new processes.
It is designed to work with Windows systems, particularly for applications like CANoe.
'''

##############################################################
##############################################################
def count_running_processes(name: str) -> int:
  '''Count how many instances of a process are running by its name.
  Args:
    name (str): Name of the application to check (e.g., 'notepad.exe', 'chrome.exe').
  Returns:
    int: Number of instances of the application running, -1 if error.
  '''
  
  i = 0
  # Iterate processes
  try:
    for process in psutil.process_iter(['pid', 'name']):
      if process.info['name'].lower() == name.lower():
        i += 1
  except psutil.Error as e:
    return -1
  # Return count
  return i

##############################################################
##############################################################
def get_running_processes(name: str) -> list[int] | None:
  '''Check if an application is running by its name.
  Args:
    name (str): Name of the application to check (e.g., 'notepad.exe', 'chrome.exe').
  Returns:
    list[int]|None: List of process IDs (PIDs) if the application is running, otherwise None.
  '''
  # Initialize empty list for PIDs
  pids = []
  
  try:
    # Iterate through all processes
    for proc in psutil.process_iter(['pid', 'name']):
      try:
        # Check if the process name matches and append PID
        if name.lower() == proc.info['name'].lower():
          pids.append(proc.info['pid'])
          
      # Handle exceptions for processes that may have terminated or are inaccessible        
      except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        continue

  except Exception as e:
    # Log the exception if needed
    return None
    
  # Return found elements
  return pids if pids else None

##############################################################
##############################################################
def print_running_processes(find: str = '') -> None:
  '''List all running applications or filter by name.
  Args:
    find (str): Optional name to filter applications by. If empty, lists all applications.
  Returns:
    None: Prints the list of applications to the console.
  '''
   
  # Print header
  print("List of running applications:")
  print("{:<10} {:<30}".format("PID", "Nombre"))
  print("-" * 40)
  
  # Iterate through all processes
  # and print their PID and name
  for proc in psutil.process_iter(['pid', 'name']):
    try:
      
      if find == '' or find == proc.info['name']:
        print("{:<10} {:<30}".format(proc.info['pid'], proc.info['name']))
      
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
      continue

##############################################################
##############################################################
def kill_process(name: str, timeout: float = 5.0) -> int:
  '''Kill a process by its name.
  Args:
    name (str): Name of the process to kill (e.g., 'notepad.exe', 'chrome.exe').
    timeout (float): Time in seconds to wait for the process to terminate gracefully before forcefully killing it.
  Returns:
    bool: True if the process was successfully killed, False if it is still running.
  '''

  # Kill process by name
  for process in psutil.process_iter(['pid', 'name']):
    try:
      # Check if the process name matches
      # and terminate it
      if process.info['name'] and name.lower() in process.info['name'].lower():
        process.terminate()  # Try terminate
        try:
          process.wait(timeout=timeout)  # Wait for the process to terminate
        except psutil.TimeoutExpired:
          process.kill()  # Force kill if it didn't terminate
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
      continue
  
  # Check if the process is still running
  i = count_running_processes(name)
  return i == 0

##############################################################
##############################################################
def kill_process_with_retry(name: str, timeout: float= 0.5, attempts: int= 3) -> bool:
  '''Kill a process by its name with retry attempts.
  Args:
    name (str): Name of the process to kill (e.g., 'notepad.exe', 'chrome.exe').
    timeout (float): Time in seconds to wait between attempts to kill the process.
    attempts (int): Number of attempts to kill the process.
  Returns:
    bool: True if the process was successfully killed, False if it is still running after all attempts.
  '''
  
  # Kill attempts
  for attempt in range(1, attempts + 1):
    
    # Look for process to terminate
    found = False
    for process in psutil.process_iter(['pid', 'name']):
      try:
        if process.info['name'] and name.lower() in process.info['name'].lower():
          found = True
          process.terminate()
          
      except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        continue
    
    # Process found
    if not found:
      return True
    
    # Wait time to kill
    if timeout > 0.0:
      time.sleep(timeout)
    
    # Look for process to kill
    for process in psutil.process_iter(['pid', 'name']):
      try:
        if process.info['name'].lower() == name.lower():
          p = psutil.Process(process.info['pid'])
          p.kill() # Force to kill
      
      except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        continue
    
    # Wait time to kill
    if timeout > 0.0:
      time.sleep(timeout)
    
  # Check if the process is still running
  return any(process.info['name'].lower() == name.lower() for process in psutil.process_iter(['name']))
    
##############################################################
##############################################################
def start_process(path: str, show_gui: bool= True, delay: float= 1.0) -> int | None:
  '''Start a new process with the given path.
  Args:
    path (str): Path to the executable file to start.
    show_gui (bool): If True, the process will be started with a new console window.
    delay (float): Time in seconds to wait after starting the process before returning the PID.
  Returns:
    int | None: Process ID (PID) of the started process if successful, otherwise None.
  '''
    
  try:
    process = subprocess.Popen(path, shell=show_gui, creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(delay)
    return process.pid
  
  except Exception as e:
    servicemanager.LogErrorMsg(f'Error to start app: {e}')
    return None
