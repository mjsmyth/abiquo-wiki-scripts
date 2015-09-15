#!/usr/bin/python3 -tt
# Process Abiquo wink console
# Remove namespace first!

class Row(object):
    """Table row."""

    def __init__(self, method, uri, accepts, contenttypes):
        """Initialise row."""
        self.method = method
        self.uri = uri
        self.accepts = accepts
        self.contenttypes = contenttypes


    def printargs(self):
        """Print row."""
        print self.arg1
        print self.arg2

def main():

	accepts = []
	contenttypes = []
	method = ""
	uri = ""



if __name__ == '__main__':
  	main()