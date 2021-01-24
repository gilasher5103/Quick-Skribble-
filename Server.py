import socket #TODO: fix the chat problem!!!!!!!!!!!!!!!!!!!!
import select
import msvcrt
import urllib.request
import threading
from threading import *
from time import *
import time
import random
from datetime import datetime

#TODO: The problem is that the server sends the location to draw but becuase everything is happening so fast he sends the next message with it creating
#TODO: a situation where the final location to draw is connected to the words LocToDraw which casues an error in the int casting


server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8820))
server_socket.listen()

print("server start")

secondary_server_socket = socket.socket()
secondary_server_socket.bind(('0.0.0.0', 2088))
secondary_server_socket.listen()


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

hidden_word = "Apple"

round_number = 1

#new_host_bool = False

def send_waiting_messages(wlist):

    counter = 0
    for guess in guess_list: #NOTE: GUESSLIST IS NOW TUPLE NEED TO CHANGE THE CODE
        for socket_to_send in wlist:
            message = guess.split(" ",1)[0]+" " + " ".join(guess.split(" ",1)[1:])  # NEED TO FIGURE OUT HOW TO ISOLATE THE Guess
            # print("sending to: " + sockets_dictionary{})
            socket_to_send.send(message.encode())
            counter += 1
            if(counter == len(wlist)):#checks if every socket recieved the guess
                guess_list.remove(guess)

def update_lobby_list(wlist):
    #global new_host_bool
    for socket_to_send in wlist:
        #print("About to send somthing")
        current_lobby_list = "Lobby is: \r\n"+ "".join(lobby_list)
        socket_to_send.send(current_lobby_list.encode())
        #if new_host_bool:
            #send_host_message(wlist)
            #new_host_bool = False
        #print("something was sent")


def send_host_message(wlist):
    if host_client[1] in wlist:
        message = "You are now the host"
        host_client[1].send(message.encode())

def send_start_message(wlist):
    for socket_to_send in wlist:
        for key, value in sockets_dictionary.items():
            if socket_to_send == value:
                if key in "".join(lobby_list):
                    print("About to send somthing")
                    message = "THE GAME IS ABOUT TO BEGIN"
                    socket_to_send.send(message.encode())
                    # print("something was sent")





#TODO: feel the function make queue
def make_queue(wlist):# creates the queue
    global queue_list
    print("function is being called")
    queue_list = lobby_list.copy()# מעקב עצמים
    handle_queue(wlist)

def handle_queue(wlist): #TODO: work on this function and the queue in general
    global sockets_dictionary
    global queue_list
    global playing_socket
    global round_number
    print("queue list is: ")
    print(queue_list)
    #print("QUEUE HANDLE SENDING: "+queue_list[0][0:len(queue_list[0])-8])
    message = "Your turn"
    if queue_list == []:
        if round_number < 3:
            round_number = round_number + 1
            make_queue(wlist)
        else:
            end_game(wlist)
    else:
        if "Host" in queue_list[0]:
            if sockets_dictionary[queue_list[0][0:len(queue_list[0]) - 9]] in wlist:  # queuelist[0] - 8(host) = current name
                sockets_dictionary[queue_list[0][0:len(queue_list[0]) - 9]].send(message.encode())
                playing_socket = sockets_dictionary[queue_list[0][0:len(queue_list[0]) - 9]]
                queue_list.remove(queue_list[0])
        else:
            if sockets_dictionary[queue_list[0][0:len(queue_list[0]) - 3]] in wlist:  # queuelist[0] - 8(host) = current name
                sockets_dictionary[queue_list[0][0:len(queue_list[0]) - 3]].send(message.encode())
                playing_socket = sockets_dictionary[queue_list[0][0:len(queue_list[0]) - 3]]
                queue_list.remove(queue_list[0])


    t5 = threading.Thread(target=timer_activation,args=(wlist,playing_socket,))
    t5.start()

def end_game(wlist):
    pass

def timer_activation(wlist,playing_socket):
    print("TIME ACTIVATION WAS CALLED")
    for i in range(30,-1,-1):
        for socket_to_send in wlist:
            message = "Timer: " + str(i)
            socket_to_send.send(message.encode())
        time.sleep(1)
    message2 = "Turn Over"
    playing_socket.send(message2.encode())
    for some_socket in wlist:
        message3 = "Clear Screen"
        some_socket.send(message3.encode())
    handle_queue(wlist) #possibly needs to update the queue list


def send_loc_broadcust(current_socket,data,wlist):#sends location to draw to everyone but the current socket which is drawing
    #global playing_socket
    """
    lastX = data[3]
    lastY = data[5]
    X = data[7]
    Y = data[9]
    """
    #print(sockets_dictionary.get(playing_socket)+"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("broadcusting location")
    for socket_to_send in wlist:
        if socket_to_send != current_socket:
            socket_to_send.send(data.encode())

def correct_answer(wlist,guesser_name):
    for socket_to_send in wlist:
        message = guesser_name + " Scored!!"
        socket_to_send.send(message.encode())

def drawing_thread():
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
                elif data[0:10] == "LocToDraw:":
                    print("Entered the loc to draw if")
                    send_loc_broadcust(current_socket, data, wlist)
                elif data[0:11] == "LocToErase:":
                    print("Entered the loc to erase if")
                    send_loc_broadcust(current_socket, data, wlist)

t = threading.Thread(target=drawing_thread)
t.start()


counter = 0
while True:
    rlist, wlist, xlist = select.select([server_socket] + open_client_sockets, open_client_sockets, [])
    if counter % 1000000 == 0:
        print("shalom oved",counter)
    counter += 1
    for current_socket in rlist:#TODO: RETURN THE FIRST PRINT
        #print("new mashu hegia")
        if current_socket is server_socket:
            (new_socket, adress) = server_socket.accept()
            open_client_sockets.append(new_socket)
            print("new client connected")
        else:#TODO: DO NOT USE THE CURRENT CLIENT NAME!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            #print("I'm here with new data to read")#TODO: RETURN THE FIRST PRINT
            data = current_socket.recv(1024)
            data = data.decode()#TODO: RETURN THE FIRST PRINT
            print("data is " + data)
            #print(data.decode()[len(data)-5:])
            if data[len(data)-5:] == "n5103": #checks for n5103 in order to find the first login
                current_client_name = data[0:len(data) - 5]
                print(data[0:len(data) - 5]) #the name
                sockets_dictionary[current_client_name] = current_socket
                #print(sockets_dictionary)
            elif data == "":
                open_client_sockets.remove(current_socket)
                print("connection with client lost")
            elif data[len(data)-9:] == "enter5103": #checks for a lobby join req
                print(data[0:len(data) - 9] + " is being added to lobby")
                lobby_list.append(data[0:len(data) - 9]+"\r\n")
                if host_client == ():
                    print(data[0:len(data) - 9] + " is now the host")
                    host_client = (data[0:len(data) - 9],current_socket)
                    send_host_message(wlist)
                    lobby_list.remove(data[0:len(data) - 9]+"\r\n")
                    lobby_list.append(data[0:len(data) - 9]+"(Host)\r\n")
                    #new_host_bool = True
                update_lobby_list(wlist)
            elif data[len(data)-14:] == "STARTEDTHEGAME":
                print("And so, it begins... (THE GAME)")
                send_start_message(wlist)
                #print("Function is being called")
                make_queue(wlist)
            elif "guessed" in data:#TODO: RETURN THE FIRST PRINT
                #(data.split(" ")[0]  + data[len(current_client_name) + 1:])# name + guessed + guess
                guess_list.append(data) #tuple of guess and the sockets that need to recieve it. name + guess = data, only the guess = data[len(data.split(' ', 1)[0]) + 1:]
                print("data[data.find(guessed )+1:]" + data[data.find("guessed ")+1:])
                if data[data.find("guessed ")+8:] == hidden_word:
                    print("CORRECT GUESS!!!!!!!!!!")
                    correct_answer(wlist, data.split(" ")[0])
                #messages_to_send.append((current_socket, data))
    send_waiting_messages(wlist)





