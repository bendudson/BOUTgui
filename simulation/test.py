import fileinput, sys



def left(line, sep):
        """
        similar to the clean function, strips off the comments from a line
        leaving just the important value
        """
        for s in sep:
            line = line.split(s)[0]
        return line.strip()
    
def right(line, sep):
        """
        different to left in that this keeps only the comments and none of the
        important values
        """
        try:
            for s in sep:
                line = line.split(s)[1]
            return line.strip()
        except IndexError:
            pass
        
def commentsTup(loadpath):
        """
        creates a list of tuples containing values and comments, effectivly splits up
        the config file so that these parts can be treated seperatly. 
        """
        tups = []
        with open(loadpath, 'r') as controlfile:
            lines = controlfile.readlines()
            for line in lines:
                name = left(line, '#')
                comment = '  #  ' + str(right(line, '#'))
                if name != '':
                    tup = (name, comment)
                    tups.append(tup)
        return tups

def addComments(tups):
        """
        reads through the config file and decides whether each option contains the value kept within
        the tuple and whether that value already has a comment associated with it. If not it adds
        the comment back onto the line - this makes up for the fact that the config parser deletes
        comments.
        """
        for i in range(len(tups)):
            try:
                lineStart = tups[i][0].split()[0]
                for line in fileinput.input('BOUT2.inp', inplace = 1):
                    if lineStart in line and '#' not in line:
                        if 'None' not in tups[i][1]:
                            newline = line.rstrip() + '  ' + tups[i][1].rstrip() + '\n'
                            line = line.replace(line, newline)
                    sys.stdout.write(line)            
            except IndexError:
                pass

            


    



