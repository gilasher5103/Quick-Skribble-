import socket
from tkinter import *
import select
import threading

print("client start")
client_socket = socket.socket()
client_socket.connect(("10.51.101.232", 8820))
print("client connect to server")

print("secondary client socket start")
secondary_client_socket = socket.socket()
secondary_client_socket.connect(("10.51.101.232", 2088))
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
destroyed = False

first_turn = True

played_this_turn = False

guess_list = []

add_bot_variable = 0


def remove_rules_window():
    rules_window.destroy()


def recieve_name():  # recieve the name and send it
    global client_Name
    if (len(textBox.get("1.0", 'end-1c')) < 18):
        client_Name = textBox.get("1.0", 'end-1c')  # recieve the current input from the textbox
        print("The name is " + client_Name)
        enter_Name_Button.destroy()  # removes the name button
        textBox.delete(1.0, END)  # clears the text box
        if " " in client_Name:
            l = client_Name.split(" ")
            client_Name = ""
            for word in l:
                client_Name = client_Name + word + "_"
            client_Name = client_Name[0:len(client_Name) - 1]
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
    if " " in client_Guess:
        l = client_Guess.split(" ")
        client_Guess = l[0] + "_" + l[1]
    client_Guess = client_Guess.lower()
    if len(client_Guess) < 16:  # 15 is the length of the longest word
        message = client_Name + " guessed " + client_Guess
        client_socket.send(message.encode())
        print("sending: " + message)
        # reply = client_socket.recv(1024)
        # print("server replied with: " +reply.decode())
    else:
        print("GUESS WAS TOO LONG TO SEND")


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
    start_game_button.place(x=80, y=107)


def start():
    global add_bot_variable
    global add_bot_button
    message = ""
    if add_bot_variable == 1:
        message = client_Name + " STARTEDTHEGAMEWITHBOT"
    else:
        message = client_Name + " STARTEDTHEGAMEWITHOUTBOT"

    client_socket.send(message.encode())
    start_game_button.destroy()
    add_bot_button.destroy()


def start_the_actual_game(add_bot_bool):
    global add_bot_variable
    window.geometry("800x600")
    lobby_list_label.place(x=5, y=20)
    my_canvas.place(x=100, y=20)
    # Guess_Button.grid(row=3,column=1)
    textBoxNew.place(x=500, y=470)
    textBoxNew.config(state='normal')
    Guess_Button.place(x=630, y=470)
    guess_Canvas.place(x=500, y=20)
    guessed_list_label.place(x=5, y=200)
    if add_bot_bool:
        add_bot_variable = 1
    else:
        add_bot_variable = 0


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


def fill_rect(rectX_index, rectY_index, color):
    global my_canvas
    if color == "black":
        my_canvas.create_rectangle(rectX_index * 13, rectY_index * 13, rectX_index * 13 + 13, rectY_index * 13 + 13,
                                   fill="black")
    elif color == "white":
        my_canvas.create_rectangle(rectX_index * 13, rectY_index * 13, rectX_index * 13 + 13, rectY_index * 13 + 13,
                                   fill="white", outline='white')
        # print("white rectangle is being painted")


def draw_and_erase_with_bot(event):
    global drawing
    # global my_turn
    # if my_turn:
    X = event.x
    Y = event.y
    global flag
    global lastX
    global lastY
    global color

    rectX_index = 0  # with those varibles i will identify which rectangle im suppose to paint
    rectY_index = 0

    rectX_index = X / 13
    rectY_index = Y / 13
    # print("X = " + str(rectX_index))
    # print("Y = " + str(rectY_index))
    # message = ""
    if drawing == 0:
        fill_rect(int(rectX_index), int(rectY_index), "black")
        message1 = "RECTDRAWING- X: " + str(int(rectX_index)) + " Y: " + str(int(rectY_index))
        secondary_client_socket.send(message1.encode())

    else:
        # print("IM HERE")
        fill_rect(int(rectX_index), int(rectY_index), "white")
        message2 = "RECTERASING- X: " + str(int(rectX_index)) + " Y: " + str(int(rectY_index))
        secondary_client_socket.send(message2.encode())
        # print("MESSAGE WAS SENT")
    # print("message is:  " + message)


def erase_with_bot(event):
    pass


def drawOrErase(event):
    global drawing
    global add_bot_variable
    if drawing == 0:
        if add_bot_variable == 1:
            draw_and_erase_with_bot(event)
        else:
            draw(event)
    else:

        if add_bot_variable == 1:
            draw_and_erase_with_bot(event)
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


# TODO: FIX THE LOCTODRAW CONNECTED to the last x
def copy_draw(datar):  # draw what the playing player draws
    lista = datar.split("LocToDraw: ")
    lista.remove("")
    print("COPY DRAW WAS CALLED")
    print("LIST A = ")
    print(lista)
    for i in range(0, len(lista)):
        # client_socket.send("copied that".encode())
        lastX = int(lista[i].split(" ")[1])
        lastY = int(lista[i].split(" ")[3])
        X = int(lista[i].split(" ")[5])
        Y = int(lista[i].split(" ")[7])
        my_canvas.create_line(lastX, lastY, X, Y, fill="black")


def copy_erase(datar):  # erase what the playin player erase
    lista = datar.split("LocToErase: ")
    lista.remove("")

    for i in range(0, len(lista)):
        # client_socket.send("copied that".encode())
        lastX = int(lista[i].split(" ")[1])
        lastY = int(lista[i].split(" ")[3])
        X = int(lista[i].split(" ")[5])
        Y = int(lista[i].split(" ")[7])
        my_canvas.create_rectangle(lastX, lastY, lastX + 10, lastY + 10, fill="white", outline="")


def destroy_window():
    global window
    window.destroy()


def clear_window_completely():
    global destroyed
    global window
    global my_canvas
    global guessed_list_label
    global scoreboard_label
    global lobby_list_label
    global hidden_word_label
    global guess_Canvas
    global time_label
    global Guess_Button
    global textBoxNew
    global drawButton
    global eraseButton
    global bot_guess_label

    destroyed = True

    my_canvas.destroy()
    guessed_list_label.destroy()
    scoreboard_label.destroy()
    lobby_list_label.destroy()
    hidden_word_label.destroy()
    guess_Canvas.destroy()
    time_label.destroy()
    Guess_Button.destroy()
    textBoxNew.destroy()
    drawButton.destroy()
    eraseButton.destroy()
    bot_guess_label.destroy()


def declare_winner(datar):
    # global result_window
    winner = datar.split("WINNER IS: ")[1]
    print("WINNER IS/ARE: " + winner)
    clear_window_completely()
    window.configure(bg='black')
    window.geometry("400x400")
    results = Label(window, text="WINNER IS: " + str(winner), fg="white", bg="black", font='Helvetica 22 bold')
    results.place(x=80, y=80)

    photo = PhotoImage(file="trophy.png")
    trophy = Label(window, image=photo)
    trophy.image = photo
    trophy.pack()
    trophy.place(x=77, y=150)

    ok_button = Button(window, text="OK", command=destroy_window)
    ok_button.place(x=270, y=500)

    """
    result_window.geometry("600x600")
    result_window.configure(bg='blue')
    result_window = Label(result_window, text=rules, fg="white", bg="red", font='Helvetica 16 bold', justify=LEFT)
    result_window.place(x=20, y=20)
    ok_button = Button(rules_window, text="OK", command=remove_result_window)
    ok_button.place(x=270, y=500)
    result_window.mainloop()
    """


def start_turn(datar):  # adds the button to draw
    global my_turn
    global drawButton
    global eraseButton
    global hidden_word_label
    global played_this_turn

    if played_this_turn == False:
        drawButton = Button(window, text="Draw", command=drawInitiator)
        eraseButton = Button(window, text="Erase", command=eraseInitiator)
        print("start turn was called")
        clear_screen()
        drawButton.place(x=200, y=450)
        eraseButton.place(x=200, y=500)
        lst = datar.split(" ")
        i = 0
        for word in lst:

            if word == "Your":
                break
            i = i + 1

        print("Hidden word time")
        l1 = datar.split("Your turn")
        l2 = l1[1].split(" END OF 'YOUR TURN' Message ")

        hidden_word_label.config(text="Hidden Word is: " + l2[0])
        hidden_word_label.place(x=250, y=550)

    played_this_turn = True


def add_guess():
    global client_Name
    rectXa = 20
    rectYa = 400
    rectXb = 180
    rectYb = 440

    triangleYa = 430
    triangleYb = 420
    triangleYc = 420

    triangleXa = 190
    triangleXb = 185
    triangleXc = 180

    global guess_list

    if len(guess_list) < 10:
        for i in range(len(guess_list) - 1, -1, -1):
            guess_Canvas.create_rectangle(rectXa, rectYa, rectXb, rectYb, fill="white")
            points = [triangleXa, triangleYa, triangleXb, triangleYb, triangleXc, triangleYc]
            guess_Canvas.create_polygon(points)
            if len(guess_list[i]) > 12 and len(guess_list[i].split('\n')) < 2:
                guess_list[i] = guess_list[i][0:len(client_Name) + len(" guessed")] + "\n" + guess_list[i][
                                                                                             len(client_Name) + len(
                                                                                                 " guessed"):]
            guess_Canvas.create_text(rectXa + 50, rectYa + 15, text=guess_list[i])  # todo
            rectYa = rectYa - 60
            rectYb = rectYb - 60

            triangleYa = triangleYa - 60
            triangleYb = triangleYb - 60
            triangleYc = triangleYc - 60
    else:
        for i in range(len(guess_list) - 1, len(guess_list) - 10, -1):
            guess_Canvas.create_rectangle(rectXa, rectYa, rectXb, rectYb, fill="white")
            points = [triangleXa, triangleYa, triangleXb, triangleYb, triangleXc, triangleYc]
            guess_Canvas.create_polygon(points)
            if len(guess_list[i]) > 12 and len(guess_list[i].split('\n')) < 2:
                guess_list[i] = guess_list[i][0:len(client_Name) + len(" guessed")] + "\n" + guess_list[i][
                                                                                             len(client_Name) + len(
                                                                                                 " guessed"):]
            guess_Canvas.create_text(rectXa + 50, rectYa + 15, text=guess_list[i])  # todo
            rectYa = rectYa - 60
            rectYb = rectYb - 60

            triangleYa = triangleYa - 60
            triangleYb = triangleYb - 60
            triangleYc = triangleYc - 60


def update_time_label(datar):
    global destroyed
    l = datar.split("Timer: ")
    time = ""
    print("timer list :")
    print(l)

    if l[1][0].isdigit():
        time = time + l[1][0]
    if len(l[1]) > 1:
        if l[1][1].isdigit():
            time = time + l[1][1]

    if destroyed == False:
        time_label.config(text=time)


def clear_screen():  # removes the paintings
    global guessed_list
    global played_this_turn
    global first_turn
    if played_this_turn and first_turn == False:
        finish_turn()
    first_turn = False
    guessed_list = ""
    print("Screen is clean")
    guessed_list_label.config(text="")
    my_canvas.delete("all")


def finish_turn():
    global my_turn
    global drawButton
    global eraseButton
    global played_this_turn
    # clear_screen()
    print("destroying the buttons")
    drawButton.destroy()
    eraseButton.destroy()
    hidden_word_label.config(text="")
    my_turn = False
    if played_this_turn:
        played_this_turn = False


def update_guessed_list():
    print("guessed list is updated!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    guessed_list_label.config(text="GUESS LIST: \r\n" + guessed_list)


def update_scoreboard(datar):
    global scoreboard_label
    s = datar
    l = s.split(" ")
    i = 0
    for word in l:
        if "SCOREBOARD" in l[i]:
            i = i + 1
            break
        i = i + 1

    digit_or_string = False  # true when its digits
    scoreboard_final_string = "Scoreboard: \n"
    for letter in l[i]:
        if letter.isdigit() == False and digit_or_string == True:
            scoreboard_final_string = scoreboard_final_string + "\n"
            digit_or_string = False
        if letter.isdigit() and digit_or_string == False:
            scoreboard_final_string = scoreboard_final_string + " "
            digit_or_string = True
        scoreboard_final_string = scoreboard_final_string + letter

    scoreboard_final_string = scoreboard_final_string[0:len(scoreboard_final_string) - 7]
    scoreboard_label.config(text=scoreboard_final_string)
    print(scoreboard_final_string)


def add_b_button():
    global add_bot_button

    add_bot_button.place(x=0, y=110)


def add_bot():
    global add_bot_variable
    if add_bot_variable == 1:
        add_bot_variable = 0
        print("Removed Bot")
    else:
        add_bot_variable = 1
        print("Bot Added")


def reader():
    global private_lobby_list
    global guess_list
    global my_turn
    global guessed_list
    global destroyed
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
                add_b_button()
                add_start_button()

            if datar[0:5] == "Lobby":
                print("private client lobby is being updated")
                private_lobby_list = datar
                update_private_lobby_list()

            if "THE GAME IS ABOUT TO BEGIN WITHOUT BOT" in datar:
                start_the_actual_game(False)
                datar = datar[38:]
            if "THE GAME IS ABOUT TO BEGIN WITH BOT" in datar:
                start_the_actual_game(True)
                datar = datar[35:]
            if "Your turn" in datar:
                print("my turn")
                my_turn = True
                textBoxNew.configure(state="disabled")
                start_turn(datar)
                datar = datar[9:]
            if datar != "":
                if "guessed" in datar and "BOT" not in datar:  # TODO: IF TIMER IS IN GUESS SHOULD UPGRADE THE IF
                    print("someone guessed something")
                    guess_list.append(datar)
                    add_guess()
                elif "Timer:" in datar:
                    print("calling the update_time_label function")
                    update_time_label(datar)
                elif "Turn Over" in datar:
                    print("finishfinish!!!!!!!!!")
                    finish_turn()
                if "Clear Screen" in datar:
                    if destroyed == False:
                        textBoxNew.configure(state="normal")
                        bot_guess_label.configure(text="BOT:")
                    clear_screen()
                if "Scored!!" in datar:
                    textBoxNew.configure(state="disabled")
                    datar = datar.replace(" Scored!!", "")
                    if datar == client_Name:
                        textBoxNew.configure(state="disabled")
                    guessed_list = guessed_list + datar + "\r\n"
                    update_guessed_list()
                if "SCOREBOARD" in datar:  # TODO must remove the scoreboard message from datar
                    update_scoreboard(datar)
                if "WINNER IS:" in datar:
                    declare_winner(datar)
                if "BOT guessed:" in datar:
                    update_bot_label(datar, True)
                if "BOT GOT IT RIGHT" in datar:
                    update_bot_label(datar, False)


def update_bot_label(datar, bool):
    global bot_guess_label

    print("datar is " + datar)
    if bool:
        i = datar.find("BOT")
        l = datar[i:]
        bot_guess_label.config(text=l)
        #print(l[i] + l[i + 1] + l[i + 2])
    else:
        bot_guess_label.config(text="BOT GOT IT RIGHT")


def copy_draw_with_bot(datar):
    global my_canvas
    lista = datar.split("RECTDRAWING- ")
    lista.remove("")
    # print("COPY DRAW WAS CALLED")
    # print("LIST A = ")
    # print(lista)
    for coordinates in lista:
        l = coordinates.split(" ")
        x = int(l[1])
        y = int(l[3])
        my_canvas.create_rectangle(x * 13, y * 13, x * 13 + 13, y * 13 + 13, fill='black')


def copy_erase_with_bot(datar):
    global my_canvas
    lista = datar.split("RECTERASING- ")
    lista.remove("")
    print("COPY ERASE WAS CALLED")
    # print("LIST A = ")
    # print(lista)
    for coordinates in lista:
        l = coordinates.split(" ")
        x = int(l[1])
        y = int(l[3])
        my_canvas.create_rectangle(x * 13, y * 13, x * 13 + 13, y * 13 + 13, fill='white', outline="white")


def secondary_reader():
    while True:
        rlist, wlist, xlist = select.select([secondary_client_socket], [secondary_client_socket], [])
        for current_socket in rlist:
            datar = current_socket.recv(1024).decode()
            print(datar)
            if datar[0:10] == "LocToDraw:":
                print("calling copy draw")

                t3 = threading.Thread(target=copy_draw, args=(datar,))
                t3.start()
            if datar[0:11] == "LocToErase:":
                print("calling copy erase")
                t4 = threading.Thread(target=copy_erase, args=(datar,))
                t4.start()
            if "RECTDRAWING- X" in datar:
                t33 = threading.Thread(target=copy_draw_with_bot, args=(datar,))
                t33.start()
            if "RECTERASING- X:" in datar:
                t44 = threading.Thread(target=copy_erase_with_bot, args=(datar,))
                t44.start()


rules_window = Tk()
rules_window.geometry("600x600")
rules_window.configure(bg='blue')
rules = "These are the rules for these game:" + "\r" \
                                                "1. Your nicknames can be up to 17 characters long," + "\r" \
                                                                                                       "2. You are not allowed to use numbers," + "\r" + "   either in your name or in the textbox" + "\r" \
                                                                                                                                                                                                      "3. Every turn one of you will draw something" + "\r" + " and the others will try to guess" \
                                                                                                                                                                                                                                                              " what it was" + "\r" \
                                                                                                                                                                                                                                                                               "4. The guessers can use the guess textbox" + "\r" + " to post their guesses, and it will lock itself" \
                                                                                                                                                                                                                                                                                                                                    "   " + "\r" + "for the rest of the turn after a correct guess" + "\r" \
                                                                                                                                                                                                                                                                                                                                                                                                      "5. Keep it clean and polite in the text window" + "\r" \
                                                                                                                                                                                                                                                                                                                                                                                                                                                         "6. Each turn will be 60 seconds long" + "\r" \
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  "GOOD LUCK EVERYBODY!" + "\r" + "PRESS OK IF YOU UNDERSTAND AND AGREE TO THE RULES"
rules_label = Label(rules_window, text=rules, fg="white", bg="red", font='Helvetica 14 bold', justify=LEFT)
rules_label.place(x=20, y=20)

ok_button = Button(rules_window, text="OK", command=remove_rules_window)
ok_button.place(x=270, y=500)
rules_window.mainloop()

# = Tk()

window = Tk()
window.geometry("270x150")
window.configure(bg='blue')

textBoxNew = Text(window, width=20, height=1)
textBox = Text(window, width=15, height=1)
textBox.place(x=20, y=10)
enter_Name_Button = Button(window, text="Enter Your Name", command=recieve_name)
enter_Name_Button.place(x=150, y=10)
Guess_Button = Button(window, text="->", command=Guess)
join_lobby_button = Button(window, text="Join Lobby", command=joinLobby)
lobby_list_label = Label(window, text=private_lobby_list, bg="red", fg="yellow")
guessed_list_label = Label(window, text="GUESS LIST: \r\n" + guessed_list, bg="red", fg="yellow")
start_game_button = Button(window, text="Start Game!", command=start)
my_canvas = Canvas(window, width=364, height=364, background='white')
guess_Canvas = Canvas(window, width=250, height=450, background='white')
drawButton = Button(window, text="Draw", command=drawInitiator)
eraseButton = Button(window, text="Erase", command=eraseInitiator)
my_canvas.bind('<B1-Motion>', drawOrErase)
my_canvas.bind('<ButtonRelease>', liftThePen)
time_label = Label(window, text="30", fg="purple", bg="green", font='Helvetica 18 bold')
time_label.place(x=5, y=150)
scoreboard_label = Label(window, text="scoreboard: ", fg="brown", bg="pink", font='Helvetica 11 bold')
scoreboard_label.place(x=5, y=300)
hidden_word_label = Label(window, text="", font='Helvetica 11 bold')
add_bot_button = Checkbutton(window, text='Add Bot', variable=add_bot_variable, command=add_bot)
bot_guess_label = Label(window, text="BOT: ", fg="brown", bg="pink", font='Helvetica 11 bold')
bot_guess_label.place(x=5, y=550)

t = threading.Thread(target=reader)
t.start()

t2 = threading.Thread(target=secondary_reader)
t2.start()

window.mainloop()

print("Checkingsomething")