import os

'''
File: file_util.py
Description: Utility functions for file operations
'''

##############################################################
##############################################################
def check_file(file_path: str) -> bool:
  '''Check if a file exists and create the directory if it does not exist.
  Args:
    file_path (str): The path to the file to check.
  '''
  
  try:
    # Check if file exists
    if os.path.exists(file_path):
      return True
    
    # Get directory from file path
    dir = os.path.dirname(file_path)
  
    # Check if directory is empty
    if not dir:
      return True
    
    # Create directory if it does not exist
    if not os.path.exists(dir):
      os.makedirs(dir)
    
    # Return
    return True
    
  except Exception as e:
    # Raise an exception if there is an error creating the directory
    raise Exception(f'Impossible to create file: {file_path}') from e
  
