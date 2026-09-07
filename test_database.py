from database import register_user, login_user


register_user(

    "sairam",

    "1234"

)


print(

    login_user(

        "sairam",

        "1234"

    )

)