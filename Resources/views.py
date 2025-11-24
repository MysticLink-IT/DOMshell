# PROJECT:     MysticLink DOMshell
# LICENSE:     AGPL-3.0
# FILE:        DOMshell/views.py
# PURPOSE:     views file for a Django app
#
#
# View scheme - views functions take an HTTP request object and a hostname and create a Powershell command that runs on the remote machine. Then they return a rendered Django template.
# Error checking - an external function should return a tuple consisting of a status code integer and a string. The string can be JSON data. Example (1, 'Connection error')
# Status codes
# 0 = Success
# 1 = Error

from django.shortcuts import render
from django.http import HttpResponse
from .models import Computer
import json
from . import ntlib


# If variable in undefined set it to an empty string
def checkNone(x):
    if x is None: return ""
    elif type(x) is str: return x
    return str(x)

# Get the username and password from the session if it exists, otherwise return message to login
def getCredentials(request):
    # Get the GET values from the URL into variables, checks if they are strings. If undefined then set them to an empty string
    username = checkNone(request.session.get('uname'))
    if username == "":
        return "LOGIN"
    password = checkNone(request.session.get('pass'))
    return (username, password)

# Get a date/time value from the URL's GET data
def getTimeFromGET(t):
    time = t.split(':')
    return {'hour':time[0],'minute':time[1]}

# Get a date/time value from the URL's GET data
def getDateFromGET(d):
    date = d.split('-')
    return {'year':date[0],'month':date[1],'day':date[2]}

def runPSGetResult(request, host, script):
    credentials = getCredentials(request)
    if (credentials == "LOGIN"): return windowsHostPage(request, host) # If username is empty the ask the user to login
    return ntlib.runPS(host, credentials, script)    # Run the Powershell command using WinRM, returns a tuple [error code, JSON]

def renderPageWithPSResult(request, host, template, winPSData):
    if winPSData[0] == 0:
        try:
            winPSData = json.loads(winPSData[1])
        except:
            winPSData = []
        return render(request, template, {'host': host, 'winPSData': winPSData})
    # If not display the error code on the page
    errorMSG = winPSData[1]
    return render(request, template, {'host': host, 'errorCode': errorMSG})

# This the main menu that contains a list of remote computers
def browseComputerLists(request):
    computers = Computer.objects.all()
    return render(request, 'computers.html', {'computers':computers})

# Login to a Windows/NT host
# Checks if a username is saved in the sessions. If not, it gets the credentials from the HTTP POST data
def windowsHostPage(request, host):
    username = checkNone(request.session.get('uname'))
    if username == "":
        username = checkNone(request.POST.get('uname'))
        if username == "":
            return render(request, 'windows-login.html', {'host':host}) # If username is empty the ask the user to login
        password = checkNone(request.POST.get('pass'))
        request.session['uname'] = username
        request.session['pass'] = password
    else:
        password = request.session.get('pass') # If a username was saved in the session table then get the password too
    return render(request, 'windows-host.html', {'host':host})

# Logout from a host. This clears the credentials stored in the database for the session
def windowsLogout(request, host):
    # Clear session values
    del(request.session['uname'])
    del(request.session['pass'])
    request.session.clear()
    return render(request, 'windows-logout.html', {'host':host}) # Return the logout confirmation page

# View the eventlog of the remote server or display a list of eventlogs on the server
def windowsViewEventLog(request, host):
    credentials = getCredentials(request)
    if (credentials == "LOGIN"): return windowsHostPage(request, host) # If username is empty the ask the user to login

    logName = checkNone(request.GET.get('logname')) # Example: 'System' or 'Security'

    if logName == "": logName = "system" # The default log is 'System'
    elif logName == "list":              # If the logname is 'list' then display a list of the available eventlogs on the remote server
        parameters={}                              # See 'buildPSCommand' in ntlib for details
        properties=["LogName","RecordCount"]   # See 'buildPSCommand' in ntlib for details
        script = ntlib.buildPSCommand("Get-WinEvent -ListLog * | sort RecordCount -Descending", parameters, properties)   # The Powershell command the get the list
        winEventlogList = ntlib.runPS(host, credentials, script)     # Run the Powershell command remotely with WinRM, returns a tuple [error code, JSON]

        # Check if the command was successful, 0 = success
        if winEventlogList[0] == 0:
            print(winEventlogList)
            winEventlogList = json.loads(winEventlogList[1])
            return render(request, 'windows-events.html', {'host': host, 'log':logName, 'eventlogList': winEventlogList})
        errorCode = winEventlogList[0]
        errorMSG = winEventlogList[1]
        return render(request, 'windows-events.html', {'host': host, 'errorCode': errorCode, 'errorMSG':errorMSG})

    # More parameters, refer to the 'Get-EventLog' Powershell command documentation for details
    EventIDs = checkNone(request.GET.get('eventids'))
    Newest = checkNone(request.GET.get('newest'))
    if Newest == "": Newest = "10"

    # The time/date range for the events. See the 'Get-EventLog' Powershell command documentation for details
    after = {}
    afterDate = checkNone(request.GET.get('afterdate'))
    afterTime = checkNone(request.GET.get('aftertime'))
    if afterTime != "": after = getTimeFromGET(afterTime)
    if afterDate != "": after = after | getDateFromGET(afterDate)
    before = {}
    beforeDate = checkNone(request.GET.get('beforedate'))
    beforeTime = checkNone(request.GET.get('beforetime'))
    if beforeTime != "": before = getTimeFromGET(beforeTime)
    if beforeDate != "": before = before | getDateFromGET(beforeDate)
    # The 'After' and 'Before' parameters in 'Get-EventLog' take a Powershell date object so we need another command to create those
    a = "(" + ntlib.buildPSCommand("Get-Date",parameters=after, outputJSON=False) + ")"
    b = "(" + ntlib.buildPSCommand("Get-Date",parameters=before, outputJSON=False) + ")"

    parameters={"LogName":logName, "Newest":Newest, "InstanceId":EventIDs, "after":a, "before":b}
    properties = ["*"]   # Return all properties in the JSON response
    script = ntlib.buildPSCommand("Get-EventLog", parameters, properties, expand=['timegenerated'])
    print(script)   # Print the full Powershell command. Useful for debugging. Check this to see an example of what commands are being run

    # Get the data
    winEventData = ntlib.runPS(host, credentials, script)   # Run the Powershell command using WinRM, returns a tuple [error code, JSON]
    # Check if the command was successful, 0 = success
    if winEventData[0] == 0:
        winEventData = json.loads(winEventData[1])
        return render(request, 'windows-events.html', {'host': host, 'log':logName, 'eventData': winEventData})
    # If not display the error code on the page
    print("Error")
    errorCode = winEventData[0]
    errorMSG = winEventData[1]
    return render(request, 'windows-events.html', {'host': host, 'errorCode': errorCode, 'errorMSG':errorMSG})

def windowsGetServices(request, host):
    parameters={}    # See 'buildPSCommand' in ntlib for details
    properties = ["State", "DisplayName", "Name", "Description", "StartMode"]    # See 'buildPSCommand' in ntlib for details
    script = ntlib.buildPSCommand("Get-WmiObject win32_service", parameters, properties)    # Returns a list of services on the system
    template = 'windows-services.html'
    winPSData = runPSGetResult(request, host, script)
    return renderPageWithPSResult(request, host, template, winPSData)

def windowsSetService(request, host, service, parameters={}):
    parameters = {"Name":service} | parameters
    script = ntlib.buildPSCommand("Set-Service", parameters, properties=[], expand=[], outputJSON=False)
    winPSData = runPSGetResult(request, host, script)
    if winPSData[0] == 0:
        return windowsGetServices(request, host)
    # If not display the error code on the page
    errorMSG = winPSData[1]
    return render(request, 'windows-services.html', {'host': host, 'errorCode': errorMSG})

def windowsSetServiceStartup(request, host, service):
    startupType = checkNone(request.GET.get('mode'))
    return windowsSetService(request, host, service, parameters={"StartupType":startupType})

def windowsStartService(request, host, service):
    #script = ntlib.buildPSCommand("Start-Service", {"Name":service}, properties=[], expand=[], outputJSON=False)
    #winPSData = runPSGetResult(request, host, script)
    #if winPSData[0] == 0:
    #    return windowsGetServices(request, host)
    ## If not display the error code on the page
    #errorMSG = winPSData[1]
    #return render(request, template, {'host': host, 'errorCode': errorMSG})
    return windowsSetService(request, host, service, parameters={"Status":"Running"})

def windowsRestartService(request, host, service):
    script = ntlib.buildPSCommand("Restart-Service", {"Name":service}, properties=[], expand=[], outputJSON=False)
    winPSData = runPSGetResult(request, host, script)
    if winPSData[0] == 0:
        return windowsGetServices(request, host)
    # If not display the error code on the page
    errorMSG = winPSData[1]
    return render(request, template, {'host': host, 'errorCode': errorMSG})

def windowsStopService(request, host, service):
    #script = ntlib.buildPSCommand("Stop-Service", {"Name":service}, properties=[], expand=[], outputJSON=False)
    #winPSData = runPSGetResult(request, host, script)
    ##if winPSData[0] == 0:
    #   return windowsGetServices(request, host)
    ## If not display the error code on the page
    #errorMSG = winPSData[1]
    #return render(request, template, {'host': host, 'errorCode': errorMSG})
    return windowsSetService(request, host, service, parameters={"Status":"Stopped"})

def windowsPauseService(request, host, service):
    return windowsSetService(request, host, service, parameters={"Status":"Paused"})

# Not implemented yet
def windowsHostTools(request, host):
    return render(request, 'windows-tools.html', {'host':host})
