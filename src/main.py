from fastapi import FastAPI, Request, Response
from marshmallow import Schema, fields
import os
import sqlite3

app = FastAPI()
con = sqlite3.connect(':memory:')

# In dev & testing only, include the stacktrace in the response on internal
# server errors
if os.getenv("FASTAPI_ENV") in ["dev", "test"]:
    @app.exception_handler(Exception)
    async def debug_exception_handler(request: Request, exc: Exception):
        import traceback

        return Response(
            status_code=500,
            content="".join(
                traceback.format_exception(
                    etype=type(exc), value=exc, tb=exc.__traceback__
                )
            )
        )

@app.on_event("startup")
async def startup_event():
    """Creates an in-memory database with a user table, and populate it with
    one account"""
    cur = con.cursor()
    cur.execute('''CREATE TABLE users (email text, password text)''')
    cur.execute('''INSERT INTO users VALUES ('me@me.com', '123456')''')
    con.commit()

@app.get("/")
async def root():
    return {"message": "Hello World"}


class VersionSchema(Schema):
    major = fields.Integer(required=True)
    minor = fields.Integer(required=True)
    patch = fields.Integer(required=True)


VERSION = VersionSchema(many=False)


@app.get("/version")
async def version():
    version, errors = VERSION.load({"major": 1, "minor": 0, "patch": None})
    if errors:
        raise ValueError(errors)
    else:
        return version
