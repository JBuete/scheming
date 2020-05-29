#!/bin/bash python3
"""
A colour scheme generating application.

author: Jacob Buete
"""
import colours
import matplotlib.patches
import matplotlib.pyplot
import numpy
import tkinter
import tkinter.ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class FileRegion(tkinter.Frame):
    """The region dealing with files."""

    def __init__(self, parent, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # the first thing is to make the file opening button
        self.df_open = tkinter.ttk.Button(self, text="Open data source...", command=self._open_file)

        self.df_open.pack(side="left", fill="both", expand=True)

    def _open_file(self):
        """Open the selected data file."""
        # first let's try a file dialogue
        filename = tkinter.filedialog.askopenfilename(filetypes=(("Comma Separated Variable", "*.csv"),
                                                                 ("Tab Separated Variable", "*.tsv"),
                                                                 ("Data File (tabbed)", "*.dat"),
                                                                 ("Plain Text", ".txt")))

        # first make sure the filename exists
        if filename:
            try:
                # we want to set this filename to the
                self.parent.master.parent.parent.plot_layout.data = numpy.genfromtxt(filename, delimiter="\t")
            except OSError:
                tkinter.messagebox.showerror("Open Source File", "Failed to read in {}".format(filename))


class ColourPicker(tkinter.Frame):
    """The colour picking region of the application."""

    def __init__(self, parent, *args, **kwargs):
        # initialise the frame
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        # self.config(bg="red")

        # start adding things
        self.label_frame = tkinter.ttk.LabelFrame(self, text="Controls")

        # make a frame for the sliders and other controls
        self.slider_container = tkinter.Frame(self.label_frame)
        self.input_container = tkinter.Frame(self.label_frame)
        self.num_stack = tkinter.Frame(self.input_container)
        self.preset_stack = tkinter.Frame(self.input_container)
        self.file_io = FileRegion(self.label_frame)  # this will contain data selection and saving

        # now get the sliders
        self.hue = Sliders(self.slider_container, 0, 360)
        self.hue.label.config(text="Hue")
        self.chroma = Sliders(self.slider_container, 0, 100)
        self.chroma.label.config(text="Chroma")
        self.light = Sliders(self.slider_container, 0, 100)
        self.light.label.config(text="Light")

        # add the sliders to the list
        self.hue.pack(side="left", fill="x", expand=True)
        self.chroma.pack(side="left", fill="x", expand=True)
        self.light.pack(side="left", fill="x", expand=True)
        # self.introduction.pack(side="left", expand=True)

        # controls region
        self.num_colours = tkinter.IntVar(self)
        self.num_colours.set(10)
        self.num_label = tkinter.ttk.Label(self.num_stack, text="# colours", anchor="center")
        self.num_entry = tkinter.ttk.Entry(self.num_stack, textvariable=self.num_colours, width=3)

        # this stuff handles the preset menu
        self.preset = tkinter.StringVar(self)
        self.preset_options = self._preset_options()
        self.preset_label = tkinter.ttk.Label(self.preset_stack, text="Presets", anchor="center")
        self.preset_menu = tkinter.ttk.Combobox(self.preset_stack, textvariable=self.preset)
        self.preset_menu['values'] = list(self.preset_options.keys())
        self.preset_menu.current(1)
        self._update_sliders("event_gibberish")
        self.preset_menu.bind("<<ComboboxSelected>>", self._update_sliders)

        # the button to generate the colours
        self.gen_button = tkinter.ttk.Button(self.input_container, text="Generate", command=self.parent.reroll)

        # now we can start packing things
        self.num_label.pack(side="top", expand=True)
        self.num_entry.pack(side="top", expand=True)

        self.preset_label.pack(side="top", expand=True)
        self.preset_menu.pack(side="top", expand=True)

        self.num_stack.pack(side="left", expand=True)
        self.preset_stack.pack(side="left", expand=True)
        self.gen_button.pack(side="right", expand=True)

        self.input_container.pack(side="top", fill="both", expand=True)
        self.slider_container.pack(side="top", fill="both", expand=True)
        self.file_io.pack(side="top", fill="both", expand=True)
        self.label_frame.pack(fill="both", expand=True)

    def _preset_options(self):
        """Define a dictionary of the preset options."""
        # this will be a dictionary keyed by the present name
        # since we can use that for the presentation
        # the value is a 3-tuple of 2-tuples
        # corresponding to ((h_low, h_high), (c_low, c_high), (l_low, l_high))
        options = {"All": ((0, 360), (0, 100), (0, 100)),
                   "Colourblind Friendly": ((0, 360), (40, 70), (15, 85))}

        return options

    def _update_sliders(self, event):
        """Update the sliders for the selected preset."""
        # first figure out what the setting is
        setting = self.preset.get()

        # now figure out what to set the settings to
        (h_low, h_high), (c_low, c_high), (l_low, l_high) = self.preset_options[setting]

        # now we can update the sliders accordingly
        self.hue.low.value.set(h_low)
        self.hue.high.value.set(h_high)
        self.chroma.low.value.set(c_low)
        self.chroma.high.value.set(c_high)
        self.light.low.value.set(l_low)
        self.light.high.value.set(l_high)


class Swatch(tkinter.Frame):
    """A colour swatch."""

    def __init__(self, parent, colour, rgb, _hex, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # now make the things that we want
        self.config(relief="groove")

        # make the objects that we care about, namely a region to put the colour
        # and the names
        self.name_frame = tkinter.Frame(self, bg="white")
        self.coloured = tkinter.Frame(self, bg=colour, height=30)
        self.rgb_name = tkinter.ttk.Label(self.name_frame, text=rgb, background="white", width=14, anchor="center")
        self.hex_name = tkinter.ttk.Label(self.name_frame, text=_hex, background="white", width=14, anchor="center")

        # first do the colour
        self.coloured.pack(side="top", fill="both", expand=True)

        # make sure the names are where they need to be
        self.rgb_name.pack(side="left", fill="x", expand=True)
        self.hex_name.pack(side="right", fill="x", expand=True)

        # and now the name frame
        self.name_frame.pack(side="top", fill="x", expand=True)


class SwatchCard(tkinter.Frame):
    """A collection of swatches."""

    def __init__(self, parent, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # maybe other things will go here?


class ColourViewer(tkinter.Frame):
    """The viewer for the generated colours."""

    def __init__(self, parent, *args, **kwargs):
        # first let's make sure we do the frame things
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.config(bg="green")

        self.label = tkinter.ttk.Label(self, text="Colour pictures will go here")

        self.frame = tkinter.ttk.LabelFrame(self, text="Colours")
        self.swatches = []
        self.cards = []
        # let's create the figure
        # self.figure = matplotlib.pyplot.figure(frameon=False)
        # self.ax = self.figure.add_subplot(1, 1, 1, aspect="equal")
        # self.ax.axis("off")

        # self._canvas = FigureCanvasTkAgg(self.figure, master=self)
        # self._canvas.draw()

        # self.canvas = self._canvas.get_tk_widget()
        # self.canvas.pack(side="left", fill="both", expand=True)

        self._draw()

    def update_colours(self, **args):
        """Update the colours to reflect the given colourblindness."""
        # iternate through the colours
        n_colours = len(self.swatches)
        for i in range(n_colours):
            colour = colours.Colourblind(self.parent.scheme.colours[i].rgb, linear=False).as_though(**args)
            self.swatches[i].coloured.config(bg=colour)

    def _draw(self):
        """Draw the colourscheme in a nicer way."""
        # first let's check the number of colours that we're looking at
        n_colours = len(self.parent.scheme.colours)

        # now let's see how close we can make this to a square
        for n_cols in range(int(n_colours**0.5), 0, -1):
            if n_colours % n_cols == 0:  # check if it's a factor
                break
        else:
            if n_colours < 5:
                n_cols = 1
            else:
                n_cols = 2

        n_rows = n_colours // n_cols  # integer division to avoid dangling issues

        # check if the number of colours has changed
        if n_colours == len(self.swatches):
            viewer = self.parent.parent.view
            self.update_colours(**viewer.colourblind_args[viewer.index[viewer.selected]])
            for i in range(n_colours):
                self.swatches[i].rgb_name.config(text=self.parent.scheme.colours[i].get_rgb_string())
                self.swatches[i].hex_name.config(text=self.parent.scheme.colours[i].hex)
        else:  # we have to remake everything
            self.swatches = []
            self.cards = []
            self.frame.destroy()
            # and then remake
            frame_backup = tkinter.ttk.LabelFrame(self, text="Colours")
            # now let's start adding some things
            for i in range(n_rows):
                # add a card
                self.cards.append(SwatchCard(frame_backup))
                for j in range(n_cols):
                    # first make the swatch
                    swatch = Swatch(self.cards[i],
                                    self.parent.scheme.colours[i * n_cols + j].hex,
                                    self.parent.scheme.colours[i * n_cols + j].get_rgb_string(),
                                    self.parent.scheme.colours[i * n_cols + j].hex)
                    # add it to the list
                    self.swatches.append(swatch)

                    # and then add it to the carc
                    self.swatches[i * n_cols + j].pack(side="left", fill="both", expand=True)

                # now add the card to the frame
                self.cards[i].pack(side="top", fill="both", expand=True)

            self.frame.destroy()
            self.frame = frame_backup
            self.frame.pack(side="left", fill="both", expand=True)

    def draw(self, ncol=5, x_offset=2.5, y_offset=3):
        """Draw the colourscheme."""
        # first erase the figure
        self.figure.clf()
        self.ax = self.figure.add_axes([0, 0, 1, 1], aspect='equal')
        self.ax.axis("off")

        # now we want to make the colours visible
        for index, colour in enumerate(self.parent.scheme.colours):
            patch = matplotlib.patches.PathPatch(colours._rounded_verts(x_offset * (index % ncol),
                                                                        -y_offset * (index // ncol)),
                                                 facecolor=colour.rgb/255, lw=0.5)

            self.ax.add_patch(patch)

        self.ax.set_ylim(-5, 5)
        self.ax.set_xlim(-1, 12)

        # self._canvas.update()
        self._canvas.draw()


class ColourRegion(tkinter.Frame):
    """The section containing the colour information."""

    def __init__(self, parent, *args, **kwargs):
        # first let's make sure we do the frame things
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.config(bg="white")
        self.parent = parent

        # first let's make the picker
        self.picker = ColourPicker(self, height=300)

        # get the colours
        self.scheme = colours.ColourScheme(self.picker.num_colours.get())

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(1, weight=1)

        # now the viewer for the colours
        self.viewer = ColourViewer(self, height=300)

        self.picker.grid(column=0, row=0, sticky="nsew")
        self.viewer.grid(column=1, row=0, sticky="nsew")
        # self.picker.pack(side="left", fill="both", expand=True)
        # self.viewer.pack(side="left", fill="both", expand=True)

    def reroll(self):
        """Regenerate the colours and draw them."""
        # we should see if the number of colours has changed
        # and if so we should generate a new scheme
        if len(self.scheme.colours) != self.picker.num_colours.get():
            self.scheme = colours.ColourScheme(self.picker.num_colours.get())

        # make sure the limits are correct
        self.scheme.set_hue_limit(self.picker.hue.low.value.get(), self.picker.hue.high.value.get())
        self.scheme.set_chroma_limit(self.picker.chroma.low.value.get(), self.picker.chroma.high.value.get())
        self.scheme.set_light_limit(self.picker.light.low.value.get(), self.picker.light.high.value.get())

        # now we can regenerate the colours
        self.scheme.reroll()

        # and then draw them
        self.viewer._draw()


class ViewOptions(tkinter.LabelFrame):
    """The viewing options for the colours."""

    def __init__(self, parent, *args, **kwargs):
        tkinter.ttk.LabelFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # first thing to do is make some buttons
        # we can probably make a grid here to make it easier
        self.normal = tkinter.Button(self, text="No Deficiency (95%)",
                                     command=lambda x="normal": self._selected(x))
        self.greyscale = tkinter.Button(self, text="Greyscale",
                                        command=lambda x="greyscale": self._selected(x))
        self.deuteranomaly = tkinter.Button(self, text="Deuteranomaly (2.7%)",
                                            command=lambda x="deuteranomaly": self._selected(x))
        self.deuteranopia = tkinter.Button(self, text="Deuteranopia (0.55%)",
                                           command=lambda x="deuteranopia": self._selected(x))
        self.protanomaly = tkinter.Button(self, text="Protanomaly (0.66%)",
                                          command=lambda x="protanomaly": self._selected(x))
        self.protanopia = tkinter.Button(self, text="Protanopia (0.58%)",
                                         command=lambda x="protanopia": self._selected(x))
        self.tritanomaly = tkinter.Button(self, text="Tritanomaly (0.01%)",
                                          command=lambda x="tritanomaly": self._selected(x))
        self.tritanopia = tkinter.Button(self, text="Tritanopia (0.015%)",
                                         command=lambda x="tritanopia": self._selected(x))

        self.buttons = [self.normal,
                        self.greyscale,
                        self.deuteranomaly,
                        self.deuteranopia,
                        self.protanomaly,
                        self.protanopia,
                        self.tritanomaly,
                        self.tritanopia]

        self.index = {"normal": 0,
                      "greyscale": 1,
                      "deuteranomaly": 2,
                      "deuteranopia": 3,
                      "protanomaly": 4,
                      "protanopia": 5,
                      "tritanomaly": 6,
                      "tritanopia": 7}

        self.colourblind_args = [{"condition": "normal", "anomalise": False, "_hex": True},
                                 {"condition": "achroma", "anomalise": False, "_hex": True},
                                 {"condition": "deutan", "anomalise": True, "_hex": True},
                                 {"condition": "deutan", "anomalise": False, "_hex": True},
                                 {"condition": "protan", "anomalise": True, "_hex": True},
                                 {"condition": "protan", "anomalise": False, "_hex": True},
                                 {"condition": "tritan", "anomalise": True, "_hex": True},
                                 {"condition": "tritan", "anomalise": False, "_hex": True}]

        # define normal to be selected first
        self.selected = "normal"
        self._selected("normal")

        # now do the grid things
        for i in range(4):
            self.grid_columnconfigure(i, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # now layout the buttons
        for j in range(2):
            for i in range(4):
                self.buttons[j + i * 2].grid(column=i, row=j, sticky='nsew')

    def _selected(self, event):
        """Signal the change in selection."""
        print(event)

        # now update the button
        self.buttons[self.index[self.selected]].config(relief="raised")
        self.buttons[self.index[event]].config(relief="sunken")

        # make sure this is tracked
        self.selected = event

        # we also need to make sure that we update the colours
        self.parent.colours.viewer.update_colours(**self.colourblind_args[self.index[self.selected]])


class PlotLayoutIntroduction(tkinter.Frame):
    """The Introduction and control for the PlotLayout."""

    def __init__(self, parent, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.message = tkinter.Message(self, text=("Here is where you can customise your plot. "
                                                   + "\nThe colour, x, y, x_err, and y_err are specified with their "
                                                   + "index."), width=600)
        self.plot_button = tkinter.ttk.Button(self, text="Plot", command=self.parent.plot.make_plot)

        self.message.pack(side="left", fill="x", expand=True)
        self.plot_button.pack(side="right", fill="x", expand=True)


class PlotLayout(tkinter.ttk.LabelFrame):
    """Where to layout the plot."""

    def __init__(self, parent, *args, **kwargs):
        # first let's make sure we do the frame things
        tkinter.ttk.LabelFrame.__init__(self, parent, *args, **kwargs)
        # self.config(bg="magenta")
        self.parent = parent
        # make a local copy of the plot
        self.plot = self.parent.plot
        self.data = None

        # self.label_frame = tkinter.ttk.LabelFrame(self, text="Plot Layout")
        self.header = PlotLayoutHeader(self)
        self.intro = PlotLayoutIntroduction(self)
        self.entries = []

        # self.label_frame.pack(side="top", fill="both", expand=True)
        self.intro.pack(side="top", fill="x", expand=True)
        self.header.pack(side="top", fill="x", expand=True)

        for i in range(5):
            self.entries.append(PlotLayoutEntry(self))
            self.entries[i].pack(side="top", fill="x", expand=True)

    def _make_plot(self):
        """Create the plot."""
        # the first thing to do is to figure out which lines are going to be used
        for i in range(len(self.entries)):
            # we will use the colour column as the indication
            if self.entries[i].colour_choice.get() != "":  # we have a value here
                pass


class PlotRegion(tkinter.ttk.LabelFrame):
    """A region for the plot to go in."""

    def __init__(self, parent, *args, **kwargs):
        # first let's make sure we do the frame things
        tkinter.ttk.LabelFrame.__init__(self, parent, *args, **kwargs)
        self.config(text="Plot")
        self.parent = parent
        self.layout = None

        # let's create the figure
        self.figure = matplotlib.pyplot.figure(frameon=False)
        self.ax = self.figure.add_subplot(1, 1, 1)
        # self.ax.axis("off")

        self._canvas = FigureCanvasTkAgg(self.figure, master=self)
        self._canvas.draw()

        self.canvas = self._canvas.get_tk_widget()
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # this is where we define the plot values
        self.lines = []
        self.points = []
        self.errors = []

    def make_plot(self):
        """Make the given plot."""
        # first clear the plotables and the axes
        self.lines = []
        self.points = []
        self.errors = []
        self.ax.cla()
        
        self.layout = self.parent.plot_layout
        use_legend = False
        
        # now figure out which elements we plot
        for entry in self.layout.entries:
            if entry.colour_choice.get() != "":
                # then we have a valid plot choice
                # and we can start to make the plot
                # first up figure out the colour we can use
                colour = colours.Colourblind(self.parent.colours.scheme.colours[int(entry.colour_choice.get())].rgb,
                                             linear=False)
                
                print(self.parent.colours.scheme.colours[int(entry.colour_choice.get())].hex)
                # and how to view that colour
                viewer = self.parent.view
                effective_colour = colour.as_though(**viewer.colourblind_args[viewer.index[viewer.selected]])
                print(effective_colour)
                # check the legend
                label = None
                if entry.legend.get() != "":
                    label = entry.legend.get()
                    use_legend = True
                
                # now check if we are using error bars or not
                if entry.x_err.get() != "" or entry.y_err.get() != "":
                    if entry.x_err.get() == "":
                        x_errors = None
                        y_errors = self.layout.data[:, int(entry.y_err.get())]
                    else:
                        y_errors = None
                        x_errors = self.layout.data[:, int(entry.y_err.get())]
                    
                    # make the plot and store the result
                    self.errors.append(self.ax.errorbar(self.layout.data[:, int(entry.x.get())], 
                                                        self.layout.data[:, int(entry.y.get())],
                                                        yerr=y_errors,
                                                        xerr=x_errors,
                                                        markerfacecolor=effective_colour,
                                                        markeredgecolor=effective_colour,
                                                        ecolor=effective_colour,
                                                        fmt='o',
                                                        label=label))
                else:
                    # we don't have errors
                    # in this case we will just check lines for this moment
                    if entry.x.get() == "":
                        self.lines.append(self.ax.plot(self.layout.data[:, int(entry.y.get())],
                                                       color=effective_colour,
                                                       label=label))
                    else:
                        self.lines.append(self.ax.plot(self.layout.data[:, int(entry.x.get())],
                                                       self.layout.data[:, int(entry.y.get())],
                                                       color=effective_colour,
                                                       label=label))
                        
        # make the legend
        
        self.ax.legend()
        
        # and draw the values
        self._canvas.draw()

class PlotLayoutEntry(tkinter.Frame):
    """The entry fields for the plot layout."""

    def __init__(self, parent, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        # inside this we're going to have the entry fields
        self.colour_choice = tkinter.ttk.Entry(self, width=5, justify='center')
        self.x = tkinter.ttk.Entry(self, width=5, justify='center')
        self.y = tkinter.ttk.Entry(self, width=5, justify='center')
        self.x_err = tkinter.ttk.Entry(self, width=5, justify='center')
        self.y_err = tkinter.ttk.Entry(self, width=5, justify='center')
        self.type = tkinter.ttk.Entry(self, width=10, justify='center')
        self.style = tkinter.ttk.Entry(self, width=10, justify='center')
        self.legend = tkinter.ttk.Entry(self, width=10, justify='center')

        self.colour_choice.pack(side="left", fill="x", expand=True, padx=2)
        self.x.pack(side="left", fill="x", expand=True, padx=2)
        self.y.pack(side="left", fill="x", expand=True, padx=2)
        self.x_err.pack(side="left", fill="x", expand=True, padx=2)
        self.y_err.pack(side="left", fill="x", expand=True, padx=2)
        self.type.pack(side="left", fill="x", expand=True, padx=2)
        self.style.pack(side="left", fill="x", expand=True, padx=2)
        self.legend.pack(side="left", fill="x", expand=True, padx=2)


class PlotLayoutHeader(tkinter.Frame):
    """The headers of the plot inputs."""

    def __init__(self, parent, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        # this is going to contain all the elements we care about
        self.colour_choice = tkinter.ttk.Label(self, text="Colour", anchor="center", width=5)
        self.x = tkinter.ttk.Label(self, text="x", anchor="center", width=5)
        self.y = tkinter.ttk.Label(self, text="y", anchor="center", width=5)
        self.x_err = tkinter.ttk.Label(self, text="x_err", anchor="center", width=5)
        self.y_err = tkinter.ttk.Label(self, text="y_err", anchor="center", width=5)
        self.type = tkinter.ttk.Label(self, text="Type", anchor="center", width=10)
        self.style = tkinter.ttk.Label(self, text="Style", anchor="center", width=10)
        self.legend = tkinter.ttk.Label(self, text="Label", anchor="center", width=10)

        self.colour_choice.pack(side="left", fill="x", expand=True)
        self.x.pack(side="left", fill="x", expand=True)
        self.y.pack(side="left", fill="x", expand=True)
        self.x_err.pack(side="left", fill="x", expand=True)
        self.y_err.pack(side="left", fill="x", expand=True)
        self.type.pack(side="left", fill="x", expand=True)
        self.style.pack(side="left", fill="x", expand=True)
        self.legend.pack(side="left", fill="x", expand=True)


class Slider(tkinter.Frame):
    """The slider creation."""

    def __init__(self, parent, low, high, *args, **kwargs):
        """Initialise the slider."""
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # now this region should have a text box above it with the value
        # a slider below it
        self.value = tkinter.IntVar()
        self.text_box = tkinter.ttk.Entry(self, text=self.value, width=3)

        self.slider = tkinter.ttk.Scale(self, variable=self.value, from_=low, to=high,
                                        orient="vertical", command=self._callback)

        # and pack the things
        self.text_box.pack(side="top", expand=True, padx=5, pady=3)
        self.slider.pack(side="top", expand=True, pady=3, padx=5)

    def _callback(self, value):
        """Round to an integer and verify the limits are reasonable."""
        self.value.set(round(float(value)))

        # now check if the other value needs fixing
        if self.value.get() == self.parent.low.value.get():
            # then we are the lower value so we should be lower than the high
            if self.value.get() > self.parent.high.value.get():
                self.parent.high.value.set(round(float(value)))
        else:  # we are the higher value
            if self.value.get() < self.parent.low.value.get():
                self.parent.low.value.set(round(float(value)))


class Sliders(tkinter.Frame):
    """A frame containing a high and low slider."""

    def __init__(self, parent, low, high, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.config(relief="sunken")

        # some label
        self.label = tkinter.ttk.Label(self, text="temp", anchor="center")

        # now we want two sliders in this
        self.low = Slider(self, high, low)
        self.high = Slider(self, high, low)

        self.low.value.set(low)
        self.high.value.set(high)

        # pack them in the region
        self.label.pack(side="top", fill="x", expand=True)
        self.low.pack(side="left", expand=True)
        self.high.pack(side="left", expand=True)


class MainApplication(tkinter.Frame):
    """The MainApplication defines the frame for the application."""

    def __init__(self, parent, *args, **kwargs):
        """Initialise an instance."""
        # first make sure we do the super-initialisation
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        # set the name of the application
        self.winfo_toplevel().title("Scheming")

        # now we need to pack this so we can see it
        self.pack(fill="both", expand=True)
        # now track the parent and make the window the size that we want
        self.parent = parent
        self.parent.geometry("1800x900+100+100")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # add things
        self.colours = ColourRegion(self, height=450, width=750)
        self.plot = PlotRegion(self, height=750, width=750)
        self.plot_layout = PlotLayout(self, height=450, width=750, text="Plot Layout")
        self.view = ViewOptions(self, height=150, width=750, text="Viewing Options")

        # now do some geometry management
        self.colours.grid(column=0, row=0, sticky="nsew")
        self.plot_layout.grid(column=0, row=1, sticky="nsew")
        self.plot.grid(column=1, row=0, sticky="nsew")
        self.view.grid(column=1, row=1, sticky="nsew")


if __name__ == "__main__":
    # first initialise the application root
    root = tkinter.Tk()

    # now make the application
    app = MainApplication(root)

    root.mainloop()
