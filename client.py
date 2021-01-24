import socket
from tkinter import *
import select
import msvcrt
import urllib.request
import threading
from threading import *
from time import *
import random
from datetime import datetime

print("client start")
client_socket = socket.socket()
client_socket.connect(("127.0.0.1", 8820))
print("client connect to server")

print("secondary client socket start")
secondary_client_socket = socket.socket()
secondary_client_socket.connect(("127.0.0.1", 2088))
print("secondary client socket connected to server")

isHost = False
my_turn = False
client_Name = ""
client_Guess = ""
private_lobby_list = ""
guessed_list = ""
flag = 0
lastX = 0  # had to define the variables lastX and LastY in order to use them but their intial values are irrelevent
LastY = 0
drawing = 0

guess_list = []

def recieve_name():  # recieve the name and send it
    global client_Name
    client_Name = textBox.get("1.0", 'end-1c')  # recieve the current input from the textbox
    print("The name is " + client_Name)
    enter_Name_Button.destroy()  # removes the name button
    textBox.delete(1.0, END)  # clears the text box
    join_lobby_button.place(x=50, y=20)  # adds the enter guess button
    textBox.config(state='disabled')
    textBox.destroy()
    name_message = client_Name + "n5103"  # informs the server that this is the first message from the client
    client_socket.send(name_message.encode())


def Guess():  # send guesses
    global client_Guess
    global client_Name
    client_Guess = textBoxNew.get("1.0", 'end-1c')  # recieve input from the text box
    print(client_Name + " guessed " + client_Guess)
    print("client_Guess " + client_Guess)
    textBoxNew.delete(1.0, END)  # clears the text box
    message = client_Name + " guessed " + client_Guess
    client_socket.send(message.encode())
    print("sending: " + message)
    # reply = client_socket.recv(1024)
    # print("server replied with: " +reply.decode())


def joinLobby():  # responsible for joining the lobby
    join_lobby_button.destroy()
    join_request = client_Name + " enter5103"
    print("sending request to join by: " + join_request)
    client_socket.send(join_request.encode())
    lobby_list_label.grid(row=2, column=0)


def update_private_lobby_list():  # change the label of lobby list
    global private_lobby_list
    print("The Lobby list before adding is: " + private_lobby_list)
    lobby_list_label.config(text=private_lobby_list)


def add_start_button():
    start_game_button.grid(row=3, column=0)


def start():
    message = client_Name + " STARTEDTHEGAME"
    client_socket.send(message.encode())
    start_game_button.destroy()


def start_the_actual_game():
    window.geometry("700x600")
    lobby_list_label.place(x=5, y=20)
    my_canvas.place(x=100, y=20)
    # Guess_Button.grid(row=3,column=1)
    textBoxNew.place(x=500, y=470)
    textBoxNew.config(state='normal')
    Guess_Button.place(x=630, y=470)
    guess_Canvas.place(x=500, y=20)
    guessed_list_label.place(x=5,y=200)


def liftThePen(event):
    global flag
    global lastX
    global lastY
    flag = 0
    lastX = 0  # had to define the variables lastX and LastY in order to use them but their intial values are irrelevent
    LastY = 0


def drawInitiator():
    global drawing
    drawing = 0


def eraseInitiator():
    global drawing
    print("drawing is 1")
    drawing = 1


def drawOrErase(event):
    global drawing
    if drawing == 0:
        draw(event)
    else:
        erase(event)


def draw(event):
    global my_turn
    if my_turn:
        X = event.x
        Y = event.y
        global flag
        global lastX
        global lastY
        global color

        if flag == 0:
            flag = 1
            lastX = X
            lastY = Y
        message = "LocToDraw: lastX- " + str(lastX) + " lastY- " + str(lastY) + " X- " + str(X) + " Y- " + str(Y)
        secondary_client_socket.send(message.encode())

        my_canvas.create_line(lastX, lastY, X, Y, fill="black")
        lastX = X
        lastY = Y




def erase(event):
    global my_turn
    if my_turn:
        X = event.x
        Y = event.y
        global flag
        global lastX
        global lastY
        global color

        if flag == 0:
            flag = 1
            lastX = X
            lastY = Y
        message = "LocToErase: lastX- " + str(lastX) + " lastY- " + str(lastY) + " X- " + str(X) + " Y- " + str(Y)
        secondary_client_socket.send(message.encode())

        my_canvas.create_rectangle(lastX, lastY, lastX + 10, lastY + 10, fill="white", outline="")
        lastX = X
        lastY = Y



#TODO: FIX THE LOCTODRAW CONNECTED to the last x
def copy_draw(datar):#draw what the playing player draws
    lista = datar.split("LocToDraw: ")
    lista.remove("")
    print("COPY DRAW WAS CALLED")
    print("LIST A = " )
    print(lista)
    for i in range(0,len(lista)):
        # client_socket.send("copied that".encode())
        lastX = int(lista[i].split(" ")[1])
        lastY = int(lista[i].split(" ")[3])
        X = int(lista[i].split(" ")[5])
        Y = int(lista[i].split(" ")[7])
        my_canvas.create_line(lastX, lastY, X, Y, fill="black")


def copy_erase(datar):#erase what the playin player erase
    lista = datar.split("LocToErase: ")
    lista.remove("")

    for i in range(0, len(lista)):
        # client_socket.send("copied that".encode())
        lastX = int(lista[i].split(" ")[1])
        lastY = int(lista[i].split(" ")[3])
        X = int(lista[i].split(" ")[5])
        Y = int(lista[i].split(" ")[7])
        my_canvas.create_rectangle(lastX, lastY, lastX + 10, lastY + 10, fill="white", outline="")



def start_turn():  # adds the button to draw
    drawButton = Button(window, text="Draw", command=drawInitiator)
    eraseButton = Button(window, text="Erase", command=eraseInitiator)
    print("start turn was called")
    clear_screen()
    drawButton.place(x=200, y=450)
    eraseButton.place(x=200, y=500)


def add_guess():
    rectXa = 20
    rectYa = 400
    rectXb = 140
    rectYb = 420

    triangleYa = 430
    triangleYb = 420
    triangleYc = 420

    triangleXa = 145
    triangleXb = 135
    triangleXc = 125

    global guess_list

    if len(guess_list) < 10:
        for i in range(len(guess_list)-1, -1, -1):
            guess_Canvas.create_rectangle(rectXa, rectYa, rectXb, rectYb, fill="white")
            points = [triangleXa, triangleYa, triangleXb, triangleYb, triangleXc, triangleYc]
            guess_Canvas.create_polygon(points)
            guess_Canvas.create_text(rectXa + 50, rectYa + 10, text=guess_list[i])
            rectYa = rectYa - 40
            rectYb = rectYb - 40

            triangleYa = triangleYa - 40
            triangleYb = triangleYb - 40
            triangleYc = triangleYc - 40
    else:
        for i in range(len(guess_list) - 1, len(guess_list) - 10, -1):
            guess_Canvas.create_rectangle(rectXa, rectYa, rectXb, rectYb, fill="white")
            points = [triangleXa, triangleYa, triangleXb, triangleYb, triangleXc, triangleYc]
            guess_Canvas.create_polygon(points)
            guess_Canvas.create_text(rectXa + 50, rectYa + 10, text=guess_list[i])
            rectYa = rectYa - 40
            rectYb = rectYb - 40

            triangleYa = triangleYa - 40
            triangleYb = triangleYb - 40
            triangleYc = triangleYc - 40

def update_time_label(datar):
    time_label.config(text=datar.split(" ")[1])

def clear_screen(): #removes the paintings
    print("Screen is clean")
    my_canvas.delete("all")


def finish_turn():
    global my_turn
    #clear_screen()
    drawButton.destroy()
    eraseButton.destroy()
    my_turn = False

def update_guessed_list():
    print("guessed list is updated!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    guessed_list_label.config(text="GUESS LIST: \r\n"+guessed_list)

def reader():
    global private_lobby_list
    global guess_list
    global my_turn
    global guessed_list
    while True:
        # print("I'm in a loop help me")
        rlist, wlist, xlist = select.select([client_socket], [client_socket], [])
        for current_socket in rlist:
            datar = current_socket.recv(1024).decode()
            print("server replied with: " + datar)
            # print("datar[0:4] is: " + datar[0:4])
            if datar[0:20] == "You are now the host":
                datar = datar[20:]
                print("datar iss: " + datar)
                isHost = True
                add_start_button()

            if datar[0:5] == "Lobby":
                print("private client lobby is being updated")
                private_lobby_list = datar
                update_private_lobby_list()

            if "THE GAME IS ABOUT TO BEGIN" in datar :
                start_the_actual_game()
                datar = datar[26:]
            if "Your turn" in datar:
                print("my turn")
                my_turn = True
                start_turn()
                datar = datar[9:]
            if datar != "":
                if "guessed" in datar:#TODO: IF TIMER IS IN GUESS SHOULD UPGRADE THE IF
                    print("someone guessed something")
                    guess_list.append(datar)
                    add_guess()
                elif "Timer:" in datar:
                    print("calling the update_time_label function")
                    update_time_label(datar)
                elif "Turn Over" in datar:
                    finish_turn()
                if "Clear Screen" in datar:
                    clear_screen()
                if "Scored!!" in datar:
                    datar = datar.replace(" Scored!!","")
                    guessed_list = guessed_list + datar +"\r\n"
                    update_guessed_list()

def secondary_reader():
    while True:
        rlist, wlist, xlist = select.select([secondary_client_socket], [secondary_client_socket], [])
        for current_socket in rlist:
            datar = current_socket.recv(1024).decode()
            print(datar)
            if datar[0:10] == "LocToDraw:":
                print("calling copy draw")

                t3 = threading.Thread(target=copy_draw,args=(datar,))
                t3.start()
            if datar[0:11] == "LocToErase:":
                print("calling copy erase")
                t4 = threading.Thread(target=copy_erase,args=(datar,))
                t4.start()






window = Tk()
window.geometry("270x150")
window.configure(bg='blue')

textBoxNew = Text(window, width=15, height=1)
textBox = Text(window, width=15, height=1)
textBox.place(x=20, y=10)
enter_Name_Button = Button(window, text="Enter Your Name", command=recieve_name)
enter_Name_Button.place(x=150, y=10)
Guess_Button = Button(window, text="->", command=Guess)
join_lobby_button = Button(window, text="Join Lobby", command=joinLobby)
lobby_list_label = Label(window, text=private_lobby_list,bg="red",fg="yellow")
guessed_list_label = Label(window, text="GUESS LIST: \r\n"+guessed_list,bg="red",fg="yellow")
start_game_button = Button(window, text="Start Game!", command=start)
my_canvas = Canvas(window, width=350, height=350, background='white')
guess_Canvas = Canvas(window, width=150, height=450, background='white')
drawButton = Button(window, text="Draw", command=drawInitiator)
eraseButton = Button(window, text="Erase", command=eraseInitiator)
my_canvas.bind('<B1-Motion>', drawOrErase)
my_canvas.bind('<ButtonRelease>', liftThePen)
time_label = Label(window,text="30",fg="purple",bg="green",font='Helvetica 18 bold')
time_label.place(x=5,y=150)
t = threading.Thread(target=reader)
t.start()

t2 = threading.Thread(target=secondary_reader)
t2.start()

window.mainloop()

print("Checkingsomething")


