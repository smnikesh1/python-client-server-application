import tkinter as tk
from tkinter import messagebox
import socket
import threading

from database import login_user, register_user
from config import SERVER_HOST, SERVER_PORT




client_socket = None


# CONNECT TO SERVER

def connect_to_server():

    global client_socket

    try:

        client_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        client_socket.connect(
            (SERVER_HOST, SERVER_PORT)
        )

        print("Connected to server!")

        return True

    except Exception as error:

        print("Server connection error:", error)

        return False


# LOGIN FUNCTION

def login():

    username = username_entry.get()

    password = password_entry.get()


    if username == "" or password == "":

        messagebox.showwarning(
            "Warning",
            "Please enter username and password"
        )

        return


    success = login_user(
        username,
        password
    )


    if success:

        # Connect to server after successful login
        connected = connect_to_server()


        if connected:

            messagebox.showinfo(
                "Login Successful",
                f"Welcome, {username}!"
            )

            # Hide login window
            root.withdraw()

            # Open chat window
            open_chat_window(username)


        else:

            messagebox.showerror(
                "Connection Error",
                "Could not connect to server"
            )


    else:

        messagebox.showerror(
            "Login Failed",
            "Invalid username or password"
        )


# REGISTER FUNCTION

def register():

    register_window = tk.Toplevel(root)

    register_window.title(
        "Create Account"
    )

    register_window.geometry(
        "400x350"
    )


    title_label = tk.Label(
        register_window,
        text="Create Account",
        font=("Arial", 22, "bold")
    )

    title_label.pack(
        pady=20
    )


    username_label = tk.Label(
        register_window,
        text="Username"
    )

    username_label.pack()


    register_username_entry = tk.Entry(
        register_window,
        width=30
    )

    register_username_entry.pack(
        pady=5
    )


    password_label = tk.Label(
        register_window,
        text="Password"
    )

    password_label.pack()


    register_password_entry = tk.Entry(
        register_window,
        width=30,
        show="*"
    )

    register_password_entry.pack(
        pady=5
    )


    confirm_label = tk.Label(
        register_window,
        text="Confirm Password"
    )

    confirm_label.pack()


    confirm_password_entry = tk.Entry(
        register_window,
        width=30,
        show="*"
    )

    confirm_password_entry.pack(
        pady=5
    )


    def create_account():

        username = register_username_entry.get()

        password = register_password_entry.get()

        confirm_password = confirm_password_entry.get()


        if (
            username == ""
            or password == ""
            or confirm_password == ""
        ):

            messagebox.showwarning(
                "Warning",
                "Please fill all fields"
            )

            return


        if password != confirm_password:

            messagebox.showerror(
                "Error",
                "Passwords do not match"
            )

            return


        success = register_user(
            username,
            password
        )


        if success:

            messagebox.showinfo(
                "Success",
                "Account created successfully!"
            )

            register_window.destroy()


        else:

            messagebox.showerror(
                "Error",
                "Username already exists"
            )


    create_button = tk.Button(
        register_window,
        text="Create Account",
        width=20,
        command=create_account
    )

    create_button.pack(
        pady=20
    )


# CHAT WINDOW

def open_chat_window(username):

    chat_window = tk.Toplevel(root)

    chat_window.title(
        f"ConnectHub - {username}"
    )

    chat_window.geometry(
        "600x500"
    )


    # Username display
    welcome_label = tk.Label(
        chat_window,
        text=f"Welcome, {username}",
        font=("Arial", 18, "bold")
    )

    welcome_label.pack(
        pady=10
    )


    # Chat display area
    chat_display = tk.Text(
        chat_window,
        height=20,
        width=70,
        state="disabled"
    )

    chat_display.pack(
        padx=10,
        pady=10
    )


    # Bottom frame
    bottom_frame = tk.Frame(
        chat_window
    )

    bottom_frame.pack(
        fill=tk.X,
        padx=10,
        pady=10
    )


    # Message input
    message_entry = tk.Entry(
        bottom_frame,
        width=50
    )

    message_entry.pack(
        side=tk.LEFT,
        padx=5
    )


    # Receive messages
    def receive_message():

        while True:

            try:

                message = client_socket.recv(
                    1024
                ).decode()

                if message:

                    chat_display.config(
                        state="normal"
                    )

                    chat_display.insert(
                        tk.END,
                        f"Server: {message}\n"
                    )

                    chat_display.config(
                        state="disabled"
                    )

                    chat_display.see(
                        tk.END
                    )

            except:

                break


    # Send messages
    def send_message():

        message = message_entry.get()


        if message == "":

            return


        try:

            client_socket.send(
                message.encode()
            )


            chat_display.config(
                state="normal"
            )

            chat_display.insert(
                tk.END,
                f"You: {message}\n"
            )

            chat_display.config(
                state="disabled"
            )

            chat_display.see(
                tk.END
            )


            message_entry.delete(
                0,
                tk.END
            )


        except Exception as error:

            messagebox.showerror(
                "Error",
                str(error)
            )


    send_button = tk.Button(
        bottom_frame,
        text="Send",
        command=send_message
    )

    send_button.pack(
        side=tk.LEFT
    )


    # Start receiving thread
    receive_thread = threading.Thread(
        target=receive_message,
        daemon=True
    )

    receive_thread.start()


# MAIN LOGIN WINDOW

root = tk.Tk()

root.title(
    "ConnectHub"
)

root.geometry(
    "400x300"
)


title_label = tk.Label(
    root,
    text="ConnectHub",
    font=("Arial", 24, "bold")
)

title_label.pack(
    pady=20
)


username_label = tk.Label(
    root,
    text="Username"
)

username_label.pack()


username_entry = tk.Entry(
    root,
    width=30
)

username_entry.pack(
    pady=5
)


password_label = tk.Label(
    root,
    text="Password"
)

password_label.pack()


password_entry = tk.Entry(
    root,
    width=30,
    show="*"
)

password_entry.pack(
    pady=5
)


login_button = tk.Button(
    root,
    text="Login",
    width=15,
    command=login
)

login_button.pack(
    pady=10
)


register_button = tk.Button(
    root,
    text="Register",
    width=15,
    command=register
)

register_button.pack()


root.mainloop()