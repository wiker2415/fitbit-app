import tkinter as tk

class ViewController:
    @staticmethod
    def start_auth_view():
        from ..views.auth_view import AuthView
        root = tk.Tk()
        auth_view = AuthView(root)
        auth_view.mainloop()

    @staticmethod
    def switch_to_main_view(root):
        from ..views.main_view import MainView
        root.destroy()
        new_root = tk.Tk()
        main_view = MainView(new_root)
        main_view.mainloop()

    @staticmethod
    def switch_to_output_month_view(root):
        from ..views.output_month_view import OutputMonthView
        root.destroy()
        new_root = tk.Tk()
        output_month_view = OutputMonthView(new_root)
        output_month_view.mainloop()

    @staticmethod
    def switch_to_fetch_view(root):
        from ..views.fetch_view import FetchView
        root.destroy()
        new_root = tk.Tk()
        fetch_view = FetchView(new_root)
        fetch_view.mainloop()

    @staticmethod
    def close_view(root):
        root.destroy()