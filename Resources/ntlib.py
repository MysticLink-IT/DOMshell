# PROJECT:     MysticLink DOMshell
# LICENSE:     AGPL-3.0
# FILE:        webterminal/ntlib.py
# PURPOSE:     This file defines the basic functions for interacting with a Windows/NT basedserver using WinRM and Powershell

import winrm

# Checks if a variable is a non empty string. Needed for Powershell commands
def checkEmpty(x):
    if x is None or x == 0: return False
    elif type(x) is str:
        if x.replace(" ", "") == "": return False
    return True

# Builds a Powershell commands that will return some information from the server
# params is the command parameters such as '-Name' (optional)
# properties are object properties returned in the JSON response for example 'event ID' in an eventlog entry (optional)
def buildPSCommand(cmd, parameters={}, properties=[], expand=[], outputJSON=True):
    script = cmd
    if parameters:
        params = parameters.keys()
        for a in params:
            if checkEmpty(parameters[a]):
                script += " -"
                script += a
                script += " "
                script += str(parameters[a])
    if properties:
        script += " | Select -Property "
        script += ", ".join(properties)
        if expand:
            script += " -ExpandProperty "
            script += ", ".join(expand)
    if(outputJSON): script += " | ConvertTo-JSON" # Format the data into JSON
    return script

# Returns a tuple consisting of a status code integer and a string. Example (1, 'Connection error')
# The string can be JSON data.
# Status codes
# 0 = Success
# 1 = Error
def runPS(host, credentials, script):
    # Open a WinRM session
    print(host + " : " + script)
    try:
        s = winrm.Session(host, credentials)
        r = s.run_ps(script)
    except Exception as e:
        print(f"Error: {e}")
        return (1, e)
    return (r.status_code, r.std_out.decode('utf-8'))
