import colours
import numpy
import tkinter
import tkinter.ttk
import matplotlib.pyplot


class ColourPicker(tkinter.Frame):
    """The ColourPicker defines the frame for the application."""


    def __init__(self, parent, *args, **kwargs):
        """Initialise an instance."""
        tkinter.Frame.__init__(self, *args, **kwargs)
        self.parent = parent


        

if __name__ == "__main__":
    # first initialise the application root
    root = tkinter.Tk()

    # now make the application
    app = ColourPicker(root)

    root.mainloop()
