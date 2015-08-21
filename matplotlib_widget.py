#
# Initial code taken from  http://stackoverflow.com/questions/6723527/getting-pyside-to-work-with-matplotlib
# Additional bits from https://gist.github.com/jfburkhart/2423179
#
from __future__ import print_function
import matplotlib

matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'


try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
    from matplotlib.pyplot import setp
    from PySide.QtGui import QVBoxLayout
    import numpy as np
    import matplotlib.cm as cm
    import matplotlib.mlab as mlab
    import matplotlib.pyplot as plt
except ImportError:
    print("ERROR: plotdata needs numpy and matplotlib to work")
    raise


class MatplotlibWidget():

    def __init__(self, parent):
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(parent)
        self.mpl_toolbar = NavigationToolbar(self.canvas, parent)
        self.axes = self.figure.add_subplot(111)
        
        self.grid_layout = QVBoxLayout()
        self.grid_layout.addWidget(self.canvas)
        self.grid_layout.addWidget(self.mpl_toolbar)
        parent.setLayout(self.grid_layout)

    matplotlib.rcParams['xtick.direction'] = 'out'
    matplotlib.rcParams['ytick.direction'] = 'out'
    
    def plotdata(self, data, x=None, y=None,
                 title=None, xtitle=None, ytitle=None,
                 output=None, range=None,
                 fill=True, mono=False, colorbar=True,
                 xerr=None, yerr=None):
        """Plot 1D or 2D data, with a variety of options."""
    
        size = data.shape
        ndims = len(size)
        
        if ndims == 1:
            self.axes.clear()
            self.figure.clear()
            self.axes = self.figure.add_subplot(111)
            #self.figure.subplots_adjust(left=0.07, right=0.98, top=0.95, bottom=0.08)
            if (xerr != None) or (yerr != None):
                # Points with error bars
                if x == None:
                    x = np.arange(size)
                errorbar(x, data, xerr, yerr)
            # Line plot
            if x == None:
                self.axes.plot(data)
                self.canvas.draw()
            else:
                self.axes.plot(x, data)
                self.canvas.draw()

        elif ndims == 2:
            # A contour plot
            
            if x == None:
                x = np.arange(size[1])
            if y == None:
                y = np.arange(size[0])
            self.axes.clear()
            self.figure.clear()
            self.axes = self.figure.add_subplot(111)          
            if fill:
                #plt.contourf(data, colors=colors)
                cmap=None
                if mono: cmap = cm.gray
                css = self.axes.imshow(data, interpolation='bilinear', cmap=cmap)
            else:
                colors = None
                if mono: colors = 'k'
                self.axes.contour(x, y, data, colors=colors)
                
            # Add a color bar
            if colorbar:
                CB = self.figure.colorbar(css ,shrink=0.8, extend='both')
                self.canvas.draw()
            
        else:
            print("Sorry, can't handle %d-D variables" % ndims)
            return
        
        if title != None:
            plt.title(title)
        if xtitle != None:
            plt.xlabel(xtitle)
        if ytitle != None:
            plt.ylabel(ytitle)
        
        if output != None:
            # Write to a file
            plt.savefig(output)
        else:
            # Plot to screen
            plt.show()


