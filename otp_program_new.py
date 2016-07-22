#!/usr/bin/python
'''

Author:   David "Buzz" Bussenschutt (c) Copyright July 2016
Based on some earlier unowned code by people who chose not to be named, and then fixed.

Write Information to OTP area

NOTES etc: 

Reference for how this code works:  
https://github.com/3drobotics/PX4Firmware-solo/blob/master/src/systemcmds/otp/README.txt
and code here: 
https://github.com/3drobotics/PX4Firmware-solo/blob/master/src/systemcmds/otp/otp.c
which relies on:
https://github.com/3drobotics/PX4Firmware-solo/blob/master/src/modules/systemlib/otp.c 

We also have a "mock" version of the 'otp' command that runs under linux and just reads/writes to a cople of .bin files but is otherwise stntactically compatible with the nsh one:  ( it's for testing etc ) 
 see mock/otp command 

See also: http://stackoverflow.com/questions/34831131/pyserial-does-not-play-well-with-virtual-port 
 
I'm pretty sure solo/pixhawk MUST be already booted prior to running this, or the kernel messages might mess with it.... and it appears it probably has to be a "fresh" boot too or nsh might run out of ram...? 
 
On Solo, you are best-off being connected to serial 5 on the accessory bay of sol ( rx/tx on pins 9 and 15 ) ..

CAUTION: this script does NOT use "connection.py", it opens its own connecion, so it should NOT be run while any connection is open from elsewhere. 
 
'''
import sys
import argparse
import binascii
import serial
import struct
import json
import zlib
import base64
import time
import array
import os
import binascii
import crcmod
import zlib
from pyotp import Read_OTP,Display_OTP,Write_OTP,Verify_OTP,Lock_OTP,Read_OTP_with_retries,simple_serial_connect,Lock_OTP_with_retries


'''
OTP partitions:
#1 Manufacturer Information(String)
#2 Machine Information(String)
#3 Manufacturing Information(String)
#3 Date of Testing(String)
#4 Time of Testing(String)
#5 Factory Accel Offsets and Scale Factors(6 Floats packed)
'''
'''
COMMAND EXAMPLES:
Manufacturer Info:      python otp_program.py --port /dev/ttyxxx
Machine Information:    python otp_program.py --port /dev/ttyxxx --info-seg 2 --info "Sid's MAC"
Manufacturing Info:     python otp_program.py --port /dev/ttyxxx --info-seg 3 --info "PH11A5500887"
Date of Testing:        python otp_program.py --port /dev/ttyxxx --info-seg 4 --info "Wed 9 Sep 2015"
Time of Testing:        python otp_program.py --port /dev/ttyxxx --info-seg 5 --info "11:28:00 AM"
Accel Calib data:       python otp_program.py --port /dev/ttyxxx --info-seg 6 --info "1.0,1.0,1.0,0.02341,0.023451,0.023552"

Display only:
                        python otp_program.py --port /dev/ttyxxx --only-display
                        
Lock:
                        python otp_program.py --port /dev/ttyxxx --info-seg INFO_SEG --lock
'''


if __name__ == '__main__':
    # Parse commandline arguments
    parser = argparse.ArgumentParser(description="OTP Programmer for the PX autopilot system.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--port', action="store", required=True, help="Serial port(s) to which the FMU may be attached")
    parser.add_argument('--baud', action="store", type=int, default=57600, help="Baud rate of the serial port (default is 115200), only required for true serial ports.")
    parser.add_argument('--only-display', action='store_true', default=False, help="specify if you want to only display otp space")
    parser.add_argument('--lock', action='store_true', default=False, help="specify if you want to lock the mentioned portion of otp space")

    # add upto three -v -v -v params for increasinly harder output to comprehend.
    parser.add_argument('--verbose', '-v', action='count', default=False, help="show also the raw hex output of the 'otp show' command, or more if repeated")

    # new data format ( each block addressed individually ): 
    parser.add_argument('--info-seg', action="store", type=int, default=1, help="OTP partitions:\n"
                                                                               "#1 Manufacturer Information\n"
                                                                               "#2 Machine Information\n"
                                                                               "#3 Manufacturing Information\n"
                                                                               "#3 Date of Testing\n"
                                                                               "#4 Time of Testing\n"
                                                                               "#5 Factory Accel Offsets and Scale Factors\n")
    parser.add_argument('--info', action="store", default="Hex Technology, \xA9 ProfiCNC 2016", help='Information')
    args = parser.parse_args()

    print repr(args)
    
    port = args.port
    print("Trying %s" % port)
    
    # verbosity level of 0, 1, 2 at least
    verbosity = 0
    if args.verbose:
        verbosity = args.verbose

    #conn = connection.Connection()  # untested. 
    conn = simple_serial_connect(port,args.baud)   # works.

    #Read, optionally with more verbosity in the read.
    otp_data = {}
    otp_data = Read_OTP_with_retries(conn,verbosity)
    
    # if read data is good! 
    if otp_data['read_success'] == False:
        print "sorry, failed to read from OTP in THREE tries! "
        conn.close()
        sys.exit(1)
      
    # present the data to the screen human-readable: 
    Display_OTP(conn,otp_data)
    
    # easy. 
    if args.only_display:
        print "Display Completed, nothing further done."
        sys.exit(0)  # done here.
        
    # if we do any changes, then a verify is needed after either/both the write and/or lock.
    do_verify = False
    
    # optionally write 
    if args.info_seg and args.info:
          #'--info-seg'
          blocknumber = args.info_seg
          #'--info'
          infostring = args.info

          # write 
          Write_OTP(conn,blocknumber,infostring)

          do_verify = True

    
    # optionall lock it as well. 
    if args.lock:     
          # lock:
          Lock_OTP_with_retries(conn,blocknumber)
          
          do_verify = True

    # after write and/or lock , verify the lock is done.           
    if  do_verify:
          Verify_OTP(conn,blocknumber,infostring,None,verbosity)
          

    # we are done.
    conn.close()
