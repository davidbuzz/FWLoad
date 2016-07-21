#!/usr/bin/python
#
# pretend to be the "other side" of the communication/s for the otp_program.py
#
import os, pty, serial, time, fcntl, sys
#import cmd2
from cmd2 import Cmd

# similar to 'sudo socat -d -d PTY,link=/dev/ttyS10 PTY,link=/dev/ttyS11' 
master, slave = os.openpty()
#The master side is not a terminal. It is just a device which permits to send/receive data to/from the slave side.
slave_name = os.ttyname(slave)  # this is the "standard terminal"

#fcntl.fcntl(master, fcntl.F_SETFL, os.O_NONBLOCK) 

# unbuffer stdout.?
#sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

# screen /dev/ttys001 57600 8N1 to connect to this....

print " Please connect with: "+slave_name
#
#
#x = 0
#while True:
#    os.write(master, "x = "+str(x))
#    print "x = "+str(x)
#    #r = os.read(master,1000)
#    #print "read:"+  r
#    time.sleep(1)
#    x = x+1

import cmd

class HelloWorld(Cmd):
    """Simple command processor example."""
    last_output = ''
    
    #def do_greet(self, line):
    #    print "hello"
    
    def do_EOF(self, line):
        return True
        
    def do_otp(self, line):
        #print 'do_otp(%s)' % line
        self.do_shell("./mock/otp "+line)
        
    def do_shell(self, line):
        #print "running shell command:", line
        output = os.popen(line).read()
        print output
        self.last_output = output

# helper....
#def fileno(file_or_fd):
#    fd = getattr(file_or_fd, 'fileno', lambda: file_or_fd)()
#    if not isinstance(fd, int):
#        raise ValueError("Expected a file (`.fileno()`) or a file descriptor")
#    return fd
    
if __name__ == '__main__':
    app = HelloWorld()
    app.prompt = 'nsh>'

    # mess with stdout, hook it to the pty
#    if True:
#        stdout = None
#        
#        if stdout is None:
#           stdout = sys.stdout
#    
#        stdout_fd = fileno(stdout)
#    
#        with os.fdopen(os.dup(stdout_fd), 'wb') as copied: 
#            stdout.flush()  # flush library buffers that dup2 knows nothing about
#            try:
#                os.dup2(fileno(to), stdout_fd)  # $ exec >&to
#            except ValueError:  # filename
#                with open(to, 'wb') as to_file:
#                    os.dup2(to_file.fileno(), stdout_fd)  # $ exec > to
#            
                
#        try:
#            yield stdout # allow code to be run with the redirected stdout
#        finally:
#            # restore stdout to its previous value
#            #NOTE: dup2 makes stdout_fd inheritable unconditionally
#            stdout.flush()
#            os.dup2(copied.fileno(), stdout_fd)  # $ exec >&copied
#            
    sys.stdout = os.fdopen(master, 'wb')
    sys.stdin = os.fdopen(master, 'rb')
    sys.stderr = open(os.devnull, 'rb')
    
    #app.default_to_shell=True
    app.cmdloop()
    
    
    
    
    
    
