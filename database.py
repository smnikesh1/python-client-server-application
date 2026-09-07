import mysql.connector
import bcrypt


# =========================
# DATABASE CONNECTION
# =========================

def get_connection():

    return mysql.connector.connect(

        host="localhost",

        user="root",

        password="sairam5235",

        database="connect_hub2"

    )


# =========================
# REGISTER USER
# =========================

def register_user(username, password):

    connection = get_connection()

    cursor = connection.cursor()


    hashed_password = bcrypt.hashpw(

        password.encode("utf-8"),

        bcrypt.gensalt()

    )


    query = """

    INSERT INTO users
    (username, password)

    VALUES (%s, %s)

    """


    cursor.execute(

        query,

        (

            username,

            hashed_password.decode("utf-8")

        )

    )


    connection.commit()

    cursor.close()

    connection.close()


# =========================
# LOGIN USER
# =========================

def login_user(username, password):

    connection = get_connection()

    cursor = connection.cursor()


    query = """

    SELECT password

    FROM users

    WHERE username = %s

    """


    cursor.execute(

        query,

        (username,)

    )


    result = cursor.fetchone()


    cursor.close()

    connection.close()


    if result is None:

        return False


    stored_password = result[0]


    return bcrypt.checkpw(

        password.encode("utf-8"),

        stored_password.encode("utf-8")

    )