from flask import Flask

import config
import pages
import routes_convert

app = Flask(__name__)
app.config["DB_FILE"] = config.DB_FILE

app.register_blueprint(pages.bp)
app.register_blueprint(routes_convert.bp)

if __name__ == "__main__":
    app.run(debug=True)