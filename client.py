import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
import rsa

# Generate RSA key pair
public_key, private_key = rsa.newkeys(2048)

# Convert keys to PEM format
public_key_pem = public_key.save_pkcs1().decode('utf-8')
private_key_pem = private_key.save_pkcs1().decode('utf-8')

# hostname = socket.gethostname()
# ip_address = socket.gethostbyname(hostname)
# HOST = ip_address
HOST = '192.168.0.39'
PORT = 9999


class Client:

    def __init__(self, host, port):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        msg = tkinter.Tk()
        msg.withdraw()

        self.nickname = simpledialog.askstring("Nickname", "Please choose a nick name: ", parent=msg)

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(background='gray')

        self.chat_label = tkinter.Label(self.win, text="Chat", background="gray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

        self.msg_label = tkinter.Label(self.win, text="Message", background="gray")
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.send_message)
        self.send_button.config(font=('Arial', 12))
        self.send_button.pack(padx=20, pady=5)

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def send_message(self):
        message = self.input_area.get("1.0", tkinter.END).strip()
        encrypted_message = rsa.encrypt(message.encode('utf-8'), public_key)
        self.sock.send(encrypted_message)
        self.input_area.delete("1.0", tkinter.END)

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024)
                decrypted_message = rsa.decrypt(message, private_key).decode('utf-8')
                if decrypted_message == 'NICK':
                    self.sock.send(self.nickname.encode())
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert(tkinter.END, decrypted_message + '\n')
                        self.text_area.yview(tkinter.END)
                        self.text_area.config(state='disabled')

            except ConnectionAbortedError:
                break
            except:
                print("Error")
                self.sock.close()
                break


client = Client(HOST, PORT)
