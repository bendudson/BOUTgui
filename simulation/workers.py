####################################### NEW CLASS #######################################
from PySide.QtGui import *
from PySide.QtCore import *
from boutGUI import *

class Worker(QThread):
##    """ 
##    This thread runs the simulations in the backgrounds so preventing the GUI from freezing while running
##    STDOUT is redirected to a signal which is collected by the text editor of the output stream
##        """

      dataLine1 = Signal(str)
      def __init__(self, path, restart, outputStream, parent = None):
              QThread.__init__(self, parent)
              self.path = path + '/'
              self.loadpath = path
              self.restart = restart
              self.outputStream = outputStream
              self.exiting = False
              window.tabWidget.setTabEnabled(2, True)

      def run(self):
          # proc runs the simulation
          global proc
          proc = subprocess.Popen([currentDir + '/runboutSim.py', str(self.path), str(self.restart)],
                                  shell = False, stdout = subprocess.PIPE, stderr = subprocess.PIPE, preexec_fn=os.setsid)
            
          running = True
          while running == True:
              output = proc.stdout.readline()
              if output == '' and proc.poll() is not None:  # at the end of proc stops reading empty ines to allow the program to close
                       v =1
                       window.tabWidget.setTabEnabled(3, True)
                       window.tabWidget.setCurrentIndex(3)
                       proc.wait()
                       running = False
                       global loadpath1
                       loadpath1 = self.loadpath
              else:
                  self.dataLine1.emit(output) # lines of output are emited here
