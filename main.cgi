#!/usr/bin/python3

try:
    from wsgiref.handlers import CGIHandler
    from main import app

    CGIHandler().run(app)

except BaseException as err:
    print("Content-Type: text/html\n\n")
    print(err)

