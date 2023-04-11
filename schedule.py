# Import Libraries
import datetime as dt
import win32com.client
import os
import sys
import json
from pathlib import Path
print('In scheduler file for task scheduling')
file = Path("GUI_output.txt")

if file.exists():
    with open(file, "r") as file:
        data = json.load(file)
    scheduling_time = data['report frequency']
    terminate_time = data['terminate reports']
    int_terminate = []
    for char in terminate_time:
        if char.isdigit():
            int_terminate.append(int(char))
    print(scheduling_time)
    int_terminate = int(int_terminate[0])

    min_in_day = 1440 # 60 times 24
    if scheduling_time == 'Weekly':
        scheduling_time = min_in_day*7
    elif scheduling_time == 'Bi-monthly':
        scheduling_time = min_in_day*14
    elif scheduling_time == 'Monthly':
        scheduling_time = min_in_day*30


    current_directory = os.path.dirname(os.path.abspath(__file__))
    print("Current directory:", current_directory)

    python_exe_directory = os.path.dirname(sys.executable)
    print("Python executable directory:", python_exe_directory)

    # Connection to Task Scheduler
    task = win32com.client.Dispatch('Schedule.Service')
    task.Connect()
    root_folder = task.GetFolder('\\')
    newtask = task.NewTask(0)

    # Trigger
    set_time = dt.datetime.now() + dt.timedelta(minutes=scheduling_time)
    end_time = dt.datetime.now() + dt.timedelta(hours=int_terminate*30*24)
    TASK_TRIGGER_TIME = 2
    trigger = newtask.Triggers.Create(TASK_TRIGGER_TIME)
    trigger.StartBoundary = set_time.isoformat()
    trigger.EndBoundary = end_time.isoformat()
    trigger.Enabled = True

    # Repetition
    repetition_pattern = trigger.Repetition
    repetition_pattern.Duration = "PT{}H".format(int_terminate*30*24)
    repetition_pattern.Interval = "PT{}M".format(scheduling_time)

    # Action
    TASK_ACTION_EXEC = 0
    action = newtask.Actions.Create(TASK_ACTION_EXEC)
    action.id = 'Mail'
    action.Path = rf'{python_exe_directory}'
    action.Arguments = rf'{current_directory} + /main_last.py'

    # Parameters
    newtask.RegistrationInfo.Description = 'DiraDiscountWeeklyUpdate'
    newtask.Settings.Enabled = True
    newtask.Settings.StopIfGoingOnBatteries = False

    # Saving
    TASK_CREATE_OR_UPDATE = 6
    TASK_LOGON_NONE = 0
    root_folder.RegisterTaskDefinition(
        'PDUW',  # Python Dira Update Weekly
        newtask,
        TASK_CREATE_OR_UPDATE,
        '',  # No user
        '',  # No password
        TASK_LOGON_NONE)
