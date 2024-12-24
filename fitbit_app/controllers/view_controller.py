import tkinter as tk

class ViewController:
    @staticmethod
    def start_auth_view():
        from ..views.auth_view import AuthView
        new_root = tk.Tk()
        AuthView(new_root)
        new_root.mainloop()

    @staticmethod
    def switch_to_main_view(root):
        from ..views.main_view import MainView
        root.destroy()
        new_root = tk.Tk()
        MainView(new_root)
        new_root.mainloop()

    @staticmethod
    def switch_to_output_view(root):
        from ..views.output_view import OutputView
        root.destroy()
        new_root = tk.Tk()
        OutputView(new_root)
        new_root.mainloop()

    @staticmethod
    def switch_to_fetch_view(root):
        from ..views.fetch_view import FetchView
        root.destroy()
        new_root = tk.Tk()
        FetchView(new_root)
        new_root.mainloop()

    @staticmethod
    def close_view(root):
        root.destroy()