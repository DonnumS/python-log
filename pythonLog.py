#!/usr/local/opt/python/libexec/bin/python
import mysql.connector
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.rcParams['toolbar'] = 'None'

TK_SILENCE_DEPRECATION = 1
globalTheme = "Green"

connected = False
con = mysql.connector.connect(user='root',
                              password=YOUR_PASSWORD,
                              database=DB_NAME)
cursor = con.cursor()


def menu():
    sg.theme(globalTheme)

    layout = [[sg.Text(
        "Welcome to this exercise logger made with Python and SQL\nChoose your desired action from the menu below")],
        [sg.Text('_'*48)],
        [sg.Button("Record new exercise"), sg.Button(
            "View previous exercises"), sg.Button("Exit")]]

    # Create the Window
    menuWindow = sg.Window('Exercise Logger', layout)

    # Event Loop to process "events"
    while True:
        event, values = menuWindow.read()
        if event in ('Record new exercise'):
            menuWindow.close()
            recordWindow()
        elif event in ("View previous exercises"):
            menuWindow.close()
            viewWindow()
        elif event in (sg.WIN_CLOSED, 'Exit'):
            break

    menuWindow.close()


def viewWindow():
    sg.theme(globalTheme)

    layout = [[sg.Text("Here you can view some of your previous exercises\nAt this time, it is only possible to view the last 10\nworkouts from each categorey\n\nPress one of the buttons below to view the statistics for each\nof the types of exercises you have logged")],
              [sg.Radio('Walking', "RADIO2", default=True, key='Walking'), sg.Radio("Running", "RADIO2", default=False,
                                                                                    key='Running'), sg.Radio("Cycling", "RADIO2", default=False, key='Cycling')],
              [sg.Button('Submit'), sg.Button("Back")]]

    # Create the Window
    viewWindow = sg.Window('Exercise Logger', layout)
    # Event Loop to process "events"
    while True:
        event, values = viewWindow.read()
        if event in ('Submit'):
            if values["Walking"] == True:
                dist, mins = viewExercise("Walking")
                viewData("Walking", dist, mins)
            elif values["Running"] == True:
                dist, mins = viewExercise("Running")
                viewData("Running", dist, mins)
            elif values["Cycling"] == True:
                dist, mins = viewExercise("Cycling")
                viewData("Cycling", dist, mins)
        elif event in ("Back"):
            viewWindow.close()
            menu()
        elif event in (sg.WIN_CLOSED):
            break

    viewWindow.close()


def viewExercise(wanted):
    query = (
        "SELECT Exercise, Minutes, DistanceKM FROM Log WHERE Exercise = '{}'".format(wanted))
    print(query)
    cursor.execute(query)
    print("Printing query result")

    exercises = []
    mins = []
    distances = []

    for(Exercise, Minutes, Distance) in cursor:
        print("{} | {} minutes | {} Km".format(Exercise, Minutes, Distance))
        exercises.append(Exercise)
        mins.append(Minutes)
        distances.append(Distance)

    return distances, mins


matplotlib.use("TkAgg")


def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg


def viewData(title, dist, mins):
    index = []
    for i in range(len(dist)):
        index.append(i)

    # Below is some botched pyplot code that works well enough
    fig = plt.figure(figsize=(10, 5))
    plt.subplot(2, 1, 1)

    distanceBar = plt.bar(index, dist, color='maroon',
                          width=0.4, zorder=3)
    plt.ylabel('Kilometers')
    plt.xlabel('')
    for i, v in enumerate(dist):
        plt.text(i, v - 1, str(v), color='white', ha='center',
                 va='bottom', fontweight='bold')
    plt.grid(zorder=0)
    plt.subplot(2, 1, 2)
    minuteBar = plt.bar(index, mins, color='maroon', width=0.4, zorder=3)
    plt.ylabel("Minutes")
    plt.xlabel('Workout id')
    for i, v in enumerate(mins):
        plt.text(i, v - 10, str(v), color='white', ha='center',
                 va='bottom', fontweight='bold')
    plt.grid(zorder=0)
    plt.show(block=False)


def recordWindow():
    sg.theme(globalTheme)

    # Specify layout of window
    layout = [[sg.Text("Good job on finishing a workout!\nBelow you can enter correct data and add the exercise to the log\nAt the moment we only support walking, running and cycling")],
              [sg.Radio('Walking', "RADIO1", default=False, key='walk'), sg.Radio("Running", "RADIO1", default=False,
                                                                                  key='run'), sg.Radio("Cycling", "RADIO1", default=False, key='cycle')],
              [sg.Text('Workout time in minutes', size=(21, 1)),
               sg.InputText(size=(5, 1), key='min')],
              [sg.Text('Distance in kilometer', size=(21, 1)),
               sg.InputText(size=(5, 1), key='km')],
              [sg.Text('Date format YYYY-MM-DD', size=(21, 1)),
               sg.InputText(size=(5, 1), key='date')],
              [sg.Button("Submit"), sg.Button("Back")]]

    # Create the Window
    recordWindow = sg.Window('Exercise Logger', layout)

    # Event Loop to process "events"
    while True:
        event, values = recordWindow.read()
        if event in ('Submit'):
            minutes = values.get('min')
            dist = values.get('km')
            date = values.get('date')

            if values["walk"] == True:
                recordExercise('walk', minutes, dist, date)
            if values["run"] == True:
                recordExercise('run', minutes, dist, date)
            if values["cycle"] == True:
                recordExercise('cycle', minutes, dist, date)

            recordWindow.close()
            menu()

        elif event in ('Back'):
            recordWindow.close()
            menu()
        elif event in (sg.WIN_CLOSED):
            break

    recordWindow.close()


# Takes parameters and inserts them into the SQL database
# No precautions made with respect to sql injection
def recordExercise(typeOfWorkout, mins, dist, date):
    mins = int(mins)

    km = float(dist)

    if(typeOfWorkout == 'walk'):
        query = (
            "INSERT INTO Log (Exercise, Minutes, Exercise_date, DistanceKM) VALUES ('Walking', '{}', '{}', '{}')".format(mins, date,  km))
        print(query)
        cursor.execute(query)

    elif(typeOfWorkout == 'run'):
        query = (
            "INSERT INTO Log (Exercise, Minutes, Exercise_date, DistanceKM) VALUES ('Running', '{}', '{}', '{}')".format(mins, date,  km))
        cursor.execute(query)

    elif(typeOfWorkout == 'cycle'):
        query = (
            "INSERT INTO Log (Exercise, Minutes, Exercise_date, DistanceKM) VALUES ('Cycling', '{}', '{}', '{}')".format(mins, date, km))
        cursor.execute(query)

    con.commit()


def start():
    print("Starting")
    menu()


if __name__ == '__main__':
    start()
