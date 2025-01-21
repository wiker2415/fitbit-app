import matplotlib.backends.backend_pdf # pyinstaller でexe化するときに必要
from fitbit_app.controllers.view_controller import ViewController

if __name__ == "__main__":
    ViewController.start_auth_view()
