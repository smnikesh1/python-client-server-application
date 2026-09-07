from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for
)

from flask_socketio import (
    join_room,
    send,
    emit,
    SocketIO
)

from database import (
    register_user,
    login_user
)

import random
from string import ascii_uppercase



app = Flask(__name__)

app.config["SECRET_KEY"] = "connecthub_secret_key"

socketio = SocketIO(
    app,
    cors_allowed_origins="*"
)




rooms = {}



online_users = {}



def generate_unique_code(length=4):

    while True:

        code = ""

        for _ in range(length):

            code += random.choice(
                ascii_uppercase
            )

        if code not in rooms:

            return code




@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        name = request.form.get("name")

        code = request.form.get("code")

        join = request.form.get("join")

        create = request.form.get("create")



        if not name:

            return render_template(
                "home.html",
                error="Please enter your name."
            )



        if create:

            room = generate_unique_code()


            rooms[room] = {

                "members": 0,

                "messages": []

            }


        # JOIN ROOM

        elif join:

            if not code:

                return render_template(
                    "home.html",
                    error="Please enter room code."
                )


            code = code.upper()


            if code not in rooms:

                return render_template(
                    "home.html",
                    error="Room does not exist."
                )


            room = code


        else:

            return render_template(
                "home.html",
                error="Invalid action."
            )


        # SAVE SESSION

        session["room"] = room

        session["name"] = name


        return redirect(
            url_for("room")
        )


    return render_template(
        "home.html"
    )



@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )


        if not username or not password:

            return render_template(

                "register.html",

                error="Please fill all fields."

            )


        try:

            register_user(

                username,

                password

            )


            return render_template(

                "register.html",

                success="Registration successful!"

            )


        except Exception as error:

            print(

                "Registration Error:",

                error

            )


            return render_template(

                "register.html",

                error="Username already exists."

            )


    return render_template(

        "register.html"

    )




@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )


        user = login_user(

            username,

            password

        )


        if user:

            session["logged_in"] = True

            session["username"] = username


            return redirect(

                url_for("home")

            )


        return render_template(

            "login.html",

            error="Invalid username or password."

        )


    return render_template(

        "login.html"

    )




@app.route(
    "/logout"
)
def logout():

    session.clear()


    return redirect(

        url_for("home")

    )




@app.route(
    "/room"
)
def room():

    room = session.get(
        "room"
    )

    name = session.get(
        "name"
    )


    if not room or not name:

        return redirect(

            url_for("home")

        )


    if room not in rooms:

        return redirect(

            url_for("home")

        )


    return render_template(

        "room.html",

        code=room,

        messages=rooms[room]["messages"],

        name=name

    )




@socketio.on(
    "message"
)
def message(data):

    room = session.get(
        "room"
    )

    name = session.get(
        "name"
    )


    if not room or room not in rooms:

        return


    message_text = data.get(
        "data"
    )


    if not message_text:

        return


    content = {

        "name": name,

        "message": message_text

    }



    send(

        content,

        to=room

    )



    rooms[room]["messages"].append(

        content

    )


    print(

        f"{name}: {message_text}"

    )



@socketio.on(
    "private_message"
)
def private_message(data):

    sender = session.get(
        "name"
    )

    receiver = data.get(
        "receiver"
    )

    message_text = data.get(
        "message"
    )


    if not sender:

        return


    if not receiver or not message_text:

        return



    if receiver not in online_users:

        emit(

            "private_error",

            {

                "message":

                f"{receiver} is not online"

            }

        )

        return


    receiver_sid = online_users[receiver]


    private_content = {

        "sender": sender,

        "receiver": receiver,

        "message": message_text

    }



    socketio.emit(

        "private_message",

        private_content,

        to=receiver_sid

    )



    emit(

        "private_message",

        private_content

    )




@socketio.on(
    "connect"
)
def connect():

    room = session.get(
        "room"
    )

    name = session.get(
        "name"
    )


    if not room or not name:

        return


    if room not in rooms:

        return


    # SAVE USER

    online_users[name] = request.sid



    join_room(

        room

    )



    rooms[room]["members"] += 1


    

    send(

        {

            "name": name,

            "message":

            "has entered the room"

        },

        to=room

    )


 

    socketio.emit(

        "online_users",

        list(

            online_users.keys()

        )

    )


    print(

        f"{name} joined {room}"

    )




@socketio.on(
    "disconnect"
)
def disconnect():

    room = session.get(
        "room"
    )

    name = session.get(
        "name"
    )


    if name in online_users:

        del online_users[name]


    if room in rooms:

        rooms[room]["members"] -= 1


        if rooms[room]["members"] <= 0:

            del rooms[room]


        else:

            send(

                {

                    "name": name,

                    "message":

                    "has left the room"

                },

                to=room

            )



    socketio.emit(

        "online_users",

        list(

            online_users.keys()

        )

    )




if __name__ == "__main__":

    socketio.run(

        app,

        host="127.0.0.1",

        port=8000,

        debug=True

    )