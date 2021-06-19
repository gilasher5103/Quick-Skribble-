import socket
from tkinter import *
import select
import threading
import numpy as np
import matplotlib.pyplot as plt
from keras.preprocessing import image
import glob
import tensorflow as tf#!!!!!!!!!!!!!!
from PIL import Image
import os
import io
bot_socket = socket.socket()
secondary_bot_socket = socket.socket()

my_canvas = Canvas
def run():
    global bot_socket
    global secondary_bot_socket


    print("BOT start")

    bot_socket.connect(("127.0.0.1", 8820))
    print("BOT connect to server")

    print("secondary BOT socket start")

    secondary_bot_socket.connect(("127.0.0.1", 2088))
    print("secondary BOT socket connected to server")
    run_window_thread = threading.Thread(target=run_window_thread_function)
    run_window_thread.start()
    run_bot_thread = threading.Thread(target=run_bot_thread_function)
    run_bot_thread.start()
def run_bot_thread_function():
    print("my_canvas.place(x=20, y=20)")

    start_server_interaction()
    print("start_server_interaction()")

    t = threading.Thread(target=reader)
    t.start()
    print("reader was called")
    t2 = threading.Thread(target=secondary_reader)
    t2.start()


def run_window_thread_function():
    global my_canvas
    print("run_thread_function")
    window = Tk()
    window.geometry("600x600")
    window.configure(bg='blue')
    my_canvas = Canvas(window, width=350, height=350, background='white')
    my_canvas.place(x=20, y=20)
    window.mainloop()







def start_server_interaction():
    print("start_server_interaction")
    bot_socket.send("IM THE BOT".encode())

# TODO: FIX THE LOCTODRAW CONNECTED to the last x
def copy_draw(datar):  # draw what the playing player draws
    global my_canvas
    lista = datar.split("RECTDRAWING- ")
    lista.remove("")
    #print("COPY DRAW WAS CALLED")
    #print("LIST A = ")
    #print(lista)
    for coordinates in lista:
        l = coordinates.split(" ")
        x = int(l[1])
        y = int(l[3])
        my_canvas.create_rectangle(x*13,y*13,x*13+13,y*13+13,fill = 'black')


def copy_erase(datar):  # erase what the playin player erase
    global my_canvas
    lista = datar.split("RECTERASING- ")
    lista.remove("")
    print("COPY ERASE WAS CALLED")
    #print("LIST A = ")
    #print(lista)
    for coordinates in lista:
        l = coordinates.split(" ")
        x = int(l[1])
        y = int(l[3])
        my_canvas.create_rectangle(x * 13, y * 13, x * 13 + 13, y * 13 + 13, fill='white',outline="white")


def clear_screen():  # removes the paintings
    global my_canvas
    my_canvas.delete("all")
"""
def ML_guess():
    global my_canvas
    print("ML GUESS function was called")
    my_canvas.to_file('draw_to_guess.png')
"""

def reader():
    global private_lobby_list
    global guess_list
    global my_turn
    global guessed_list
    global bot_socket
    global secondary_bot_socket
    while True:
        rlist, wlist, xlist = select.select([bot_socket], [bot_socket], [])
        for current_socket in rlist:
            datar = current_socket.recv(1024).decode()
            print("server replied with: " + datar)
            # print("datar[0:4] is: " + datar[0:4])

            if "Clear Screen" in datar:
                clear_screen()
            if "Activate ML Model" in datar:
                make_a_guess()


def save_current_canvas():
    my_canvas.update()
    ps = my_canvas.postscript(colormode='color')
    image = Image.open(io.BytesIO(ps.encode('utf-8')))
    image.save("Image_To_GUESS.jpg")

def make_a_guess():
    save_current_canvas()

    try:
        Bot_Answer = ""

        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # !!!!!!!!!!!!!!!

        file_list = glob.glob("Image_To_GUESS.jpg")

        file = open("class_names.txt")  # !!!!!!!!!!!!!!!!!!!!

        line = file.read().replace("\n", " ")
        file.close()
        CATEGORIES = list(line.split(" "))

        x = []
        for each in file_list:
            img = image.load_img(each, color_mode="grayscale", target_size=(28, 28))
            img = image.img_to_array(img)
            img = img.reshape(28, 28, 1)
            img = img.astype('float32')
            img = (255 - img) / 255.0
            x.append(img)
            plt.figure()
            plt.imshow(img, cmap='Greys')
            plt.grid(False)
            plt.colorbar()
            # plt.show()
            x.append(img)

        x = np.array(x)
        model = tf.keras.models.load_model("keras.h5", compile=True)  # !!!!!!!
        result = model.predict_classes(x)
        for i in range(len(result)):
            print(CATEGORIES[result[i]], result[i])
            Bot_Answer = str(CATEGORIES[result[i]])
        print("RESULT IS: ")
        print(Bot_Answer)

        for i in range(len(result)):
            plt.figure()
            plt.imshow(x[i], cmap='Greys')
            plt.grid(False)
            plt.axis('off')
            plt.colorbar()
            plt.title(CATEGORIES[result[i]])
            # plt.show()
        message = "BOTG: " + Bot_Answer + " "
        bot_socket.send(message.encode())
    except:
        print("BOT ERROR")




def secondary_reader():
    global bot_socket
    global secondary_bot_socket
    while True:
        rlist, wlist, xlist = select.select([secondary_bot_socket], [secondary_bot_socket], [])
        for current_socket in rlist:
            datar = current_socket.recv(1024).decode()
            #print("SECOND SERVER: " + datar)
            if "RECTDRAWING-" in datar:
                #print("calling copy draw")
                t3 = threading.Thread(target=copy_draw, args=(datar,))
                t3.start()
            if "RECTERASING-" in datar:
                print("calling copy erase")
                t4 = threading.Thread(target=copy_erase, args=(datar,))
                t4.start()

