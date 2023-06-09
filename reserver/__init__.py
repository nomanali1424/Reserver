from flask import Flask

app = Flask(__name__)
app.secret_key = "Noman"

import reserver.db_methods
import reserver.error_handler
import reserver.routes.admin
import reserver.routes.home
import reserver.routes.login
import reserver.routes.show
import reserver.routes.venue
import reserver.routes.user

if __name__ == "__main__":
    app.run()
