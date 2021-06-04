import socket 
import select
import threading
from time import *
import time
import random
import BOT


server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8820))
server_socket.listen()

print("server start")

secondary_server_socket = socket.socket()
secondary_server_socket.bind(('0.0.0.0', 2088))
secondary_server_socket.listen()

found_bot = False

open_secondary_client_sockets = []
open_client_sockets = []
messages_to_send = []
sockets_dictionary = {}
guess_list = []
lobby_list = []
host_client = ()
current_client_name = ""
queue_list =[]
playing_socket = server_socket
scoreboard = []

bot_socket = server_socket

current_time = 30

file = open("class_names.txt")

line = file.read().replace("\n", " ")
file.close()
CATEGORIES = list(line.split(" "))
hidden_word = "Apple"

round_number = 1

#new_host_bool = False

def send_waiting_messages(wlist): #sends the messages that are left to be sent

    counter = 0
    for guess in guess_list:
        for socket_to_send in wlist:
            message = guess.split(" ",1)[0]+" " + " ".join(guess.split(" ",1)[1:])
            # print("sending to: " + sockets_dictionary{})
            socket_to_send.send(message.encode())
            counter += 1
            if(counter == len(wlist)):#checks if every socket recieved the guess
                guess_list.remove(guess)

def update_lobby_list(wlist): #updates the lobby list when a player enters the lobby
    for socket_to_send in wlist:
        current_lobby_list = "Lobby is: \r\n"+ "".join(lobby_list)
        socket_to_send.send(current_lobby_list.encode())


def send_host_message(wlist): #alerts the host that he is the host of the game
    if host_client[1] in wlist:
        message = "You are now the host"
        host_client[1].send(message.encode())

def send_start_message(wlist,add_bot_bool): #notify the cliets that the game is beginning
    for socket_to_send in wlist:
        for key, value in sockets_dictionary.items():
            if socket_to_send == value:
                if key in "".join(lobby_list):
                    print("About to send somthing")
                    if add_bot_bool:
                        message = "THE GAME IS ABOUT TO BEGIN WITH BOT"
                    else:
                        message = "THE GAME IS ABOUT TO BEGIN WITHOUT BOT"
                    socket_to_send.send(message.encode())
    create_scoreboard()
                    # print("something was sent")
def create_scoreboard(): #creates a list that contains tuples of player's name and score based on the lobby list
    global lobby_list
    global scoreboard
    print(lobby_list)
    for i in range(0, len(lobby_list)):
        scoreboard.append((lobby_list[i], 0))
        print(scoreboard)

def update_scoreborad(guesser_name): #update the score of the players based on their performence in the last round
    global scoreboard
    global current_time

    for i in range(0,len(scoreboard)):
        if scoreboard[i][0].split(" ")[0] == guesser_name:
            lst = list(scoreboard[i])
            lst[1] = current_time * 5 + lst[1]
            scoreboard[i] = tuple(lst)
            print("SCOREBOARD HAS BEEN UPDATED")
            print(scoreboard)

def send_scoreboard(): #sends the scoreboard to all the clients at the end of a round
    global scoreboard
    message = "SCOREBOARD: "
    for i in range(0, len(scoreboard)):
        message = message + scoreboard[i][0].split(" ")[0] + str(scoreboard[i][1])
    message = message + "DS123 " #donescoreboard123
    print("SCOREBOARD MESSAGE IS: " + message)
    for socket_to_send in wlist:
        socket_to_send.send(message.encode())

def random_hidden_word(): #picks the hidden word of the turn
    global hidden_word
    global CATEGORIES

    word_index = random.randint(0, 99)
    hidden_word = CATEGORIES[word_index]
    print("THE HIDDEN WORD IS: " + hidden_word)




def make_queue(wlist):# creates the queue (copies the lobby list)
    global queue_list
    print("function is being called")
    queue_list = lobby_list.copy()
    handle_queue(wlist)


def handle_queue(wlist): #alerts the next player that it is now his turn
    global sockets_dictionary
    global queue_list
    global playing_socket
    global round_number
    print("queue list is: ")
    print(queue_list)
    message = "Your turn" + str(random_hidden_word()) +" END OF 'YOUR TURN' Message"
    if queue_list == []:
        if round_number < 3:
            round_number = round_number + 1
            make_queue(wlist)
    else:
        if "Host" in queue_list[0]:
            if sockets_dictionary[queue_list[0][0:len(queue_list[0]) - 9]] in wlist:
                sockets_dictionary[queue_list[0][0:len(queue_list[0]) - 9]].send(message.encode())
                playing_socket = sockets_dictionary[queue_list[0][0:len(queue_list[0]) - 9]]
                queue_list.remove(queue_list[0])
        else:
            if sockets_dictionary[queue_list[0][0:len(queue_list[0]) - 3]] in wlist:
                sockets_dictionary[queue_list[0][0:len(queue_list[0]) - 3]].send(message.encode())
                playing_socket = sockets_dictionary[queue_list[0][0:len(queue_list[0]) - 3]]
                queue_list.remove(queue_list[0])


    t5 = threading.Thread(target=timer_activation,args=(wlist,playing_socket,))
    t5.start()



def ask_for_bot_guess(): #send a request to the bot for a guess that describes what is painted on the canvas
    print("BOT IS BEING CALLED")
    bot_socket.send("Activate ML Model".encode())

def timer_activation(wlist,playing_socket): # a thread that is resposnsible for the timer in the game
    global current_time
    global found_bot
    print("TIME ACTIVATION WAS CALLED")
    for i in range(30,-1,-1):
        for socket_to_send in wlist:
            if i % 5 == 0 and found_bot:
                ask_for_bot_guess()
            message = "Timer: " + str(i)
            current_time = i
            socket_to_send.send(message.encode())
        time.sleep(1)
    message2 = "Turn Over"
    playing_socket.send(message2.encode())
    for some_socket in wlist:
        message3 = "Clear Screen"
        some_socket.send(message3.encode())
        if found_bot:
            bot_socket.send(message3.encode())

    send_scoreboard()
    handle_queue(wlist)



def send_loc_broadcust(current_socket,data,wlist):#sends location to draw to everyone but the current socket which draws
    for socket_to_send in wlist:
        if socket_to_send != current_socket:
            socket_to_send.send(data.encode())

def correct_answer(wlist,guesser_name):#notify the clients when someone mennages to guess the hidden word
    for socket_to_send in wlist:
        message = guesser_name + " Scored!!"
        socket_to_send.send(message.encode())
    update_scoreborad(guesser_name)

def drawing_thread(): #resposible for broadcusting the location to draw and erase for all the player but the drawer
    while True:
        rlist, wlist, xlist = select.select([secondary_server_socket] + open_secondary_client_sockets, open_secondary_client_sockets, [])
        for current_socket in rlist:
            if current_socket is secondary_server_socket:
                (new_socket, adress) = secondary_server_socket.accept()
                open_secondary_client_sockets.append(new_socket)
                print("new secondary client connected")
            else:
                data = current_socket.recv(1024)
                data = data.decode()
                # print("data is " + data)
                if data == "":
                    open_secondary_client_sockets.remove(current_socket)
                    print("connection with client lost")
                elif data[0:10] == "LocToDraw:" or "RECTDRAWING" in data:
                    #print("Entered the loc to draw if")
                    send_loc_broadcust(current_socket, data, wlist)
                elif data[0:11] == "LocToErase:" or "RECTERASING":
                    #print("Entered the loc to erase if")
                    send_loc_broadcust(current_socket, data, wlist)

def add_bot_to_scoreboard(): #adds the bot to the scoreboard list
    global scoreboard
    global current_time
    scoreboard.append(("BOT", 0))

def update_bot_scoreboard(): #updates the bot score when it guesses the hidden word
    print("ADDING BOT SCORE TO SCOREBOARD")
    global scoreboard
    global current_time
    for i in range(0, len(scoreboard)):
        if scoreboard[i][0].split(" ")[0] == "BOT":
            lst = list(scoreboard[i])
            lst[1] = current_time * 5 + lst[1]
            scoreboard[i] = tuple(lst)
            print("SCOREBOARD HAS BEEN UPDATED")
            print(scoreboard)

def send_bot_guesses(isCorrect,bot_guess):#sends the bot's guesses to every client in the game
    if isCorrect:
        message = "BOT GOT IT RIGHT"
        for socket_to_send in wlist:
            socket_to_send.send(message.encode())
            update_bot_scoreboard()
    else:
        message = "BOT guessed: " + bot_guess
        for socket_to_send in wlist:
            socket_to_send.send(message.encode())
    print(message)

t = threading.Thread(target=drawing_thread)
t.start()


counter = 0 #main reader: this loop is responsible for recieving and handling the data from the clients and bot
while True:
    rlist, wlist, xlist = select.select([server_socket] + open_client_sockets, open_client_sockets, [])
    if counter % 1000000 == 0:
        print("shalom oved",counter)
    counter += 1
    for current_socket in rlist:
        #print("new mashu hegia")
        if current_socket is server_socket:
            (new_socket, adress) = server_socket.accept()
            open_client_sockets.append(new_socket)
            print("new client connected")
        else:
            data = current_socket.recv(1024)
            data = data.decode()
            print("data is " + data)
            if data[len(data)-5:] == "n5103":
                current_client_name = data[0:len(data) - 5]
                print(data[0:len(data) - 5])
                sockets_dictionary[current_client_name] = current_socket
            elif data == "":
                open_client_sockets.remove(current_socket)
                print("connection with client lost")
            elif data[len(data)-9:] == "enter5103":
                print(data[0:len(data) - 9] + " is being added to lobby")
                lobby_list.append(data[0:len(data) - 9]+"\r\n")
                if host_client == ():
                    print(data[0:len(data) - 9] + " is now the host")
                    host_client = (data[0:len(data) - 9],current_socket)
                    send_host_message(wlist)
                    lobby_list.remove(data[0:len(data) - 9]+"\r\n")
                    lobby_list.append(data[0:len(data) - 9]+"(Host)\r\n")
                update_lobby_list(wlist)
            elif "STARTEDTHEGAME" in data:
                if "STARTEDTHEGAMEWITHBOT" in data:
                    send_start_message(wlist,True)
                    BOT.run()
                    add_bot_to_scoreboard()
                    print("NICELY DONE")
                elif "STARTEDTHEGAMEWITHOUTBOT" in data:
                    send_start_message(wlist, False)
                print("And so, it begins... (THE GAME)")
                make_queue(wlist)
            elif "guessed" in data:
                print("data[data.find(guessed )+1:]" + data[data.find("guessed ")+1:])
                if data[data.find("guessed ")+8:] == hidden_word:
                    print("CORRECT GUESS!!!!!!!!!!")
                    correct_answer(wlist, data.split(" ")[0])
                else:
                    guess_list.append(data)
            elif "IM THE BOT" in data:
                print("BOT CONNECTED")
                bot_socket = current_socket
                found_bot = True
            elif "BOTG" in data:
                index = data.find("BOTG")
                index2 = data[index + 6:].find(" ")
                g = data[index + 6:index + 6 + index2]
                print("G IS: " + g)
                if g == hidden_word:
                    print("BOT GUESSED CORRECTLY AND IM ABOUT TO SEND IT")
                    send_bot_guesses(True,g)
                else:
                    send_bot_guesses(False,g)

    send_waiting_messages(wlist)





