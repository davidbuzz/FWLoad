import time
import struct
import sys
import binascii

BASICDEBUG = False
MOREDEBUG = False

crc32_tab = [
  0x00000000, 0x77073096, 0xee0e612c, 0x990951ba, 0x076dc419, 0x706af48f, 0xe963a535, 0x9e6495a3,
  0x0edb8832, 0x79dcb8a4, 0xe0d5e91e, 0x97d2d988, 0x09b64c2b, 0x7eb17cbd, 0xe7b82d07, 0x90bf1d91,
  0x1db71064, 0x6ab020f2, 0xf3b97148, 0x84be41de, 0x1adad47d, 0x6ddde4eb, 0xf4d4b551, 0x83d385c7,
  0x136c9856, 0x646ba8c0, 0xfd62f97a, 0x8a65c9ec, 0x14015c4f, 0x63066cd9, 0xfa0f3d63, 0x8d080df5,
  0x3b6e20c8, 0x4c69105e, 0xd56041e4, 0xa2677172, 0x3c03e4d1, 0x4b04d447, 0xd20d85fd, 0xa50ab56b,
  0x35b5a8fa, 0x42b2986c, 0xdbbbc9d6, 0xacbcf940, 0x32d86ce3, 0x45df5c75, 0xdcd60dcf, 0xabd13d59,
  0x26d930ac, 0x51de003a, 0xc8d75180, 0xbfd06116, 0x21b4f4b5, 0x56b3c423, 0xcfba9599, 0xb8bda50f,
  0x2802b89e, 0x5f058808, 0xc60cd9b2, 0xb10be924, 0x2f6f7c87, 0x58684c11, 0xc1611dab, 0xb6662d3d,
  0x76dc4190, 0x01db7106, 0x98d220bc, 0xefd5102a, 0x71b18589, 0x06b6b51f, 0x9fbfe4a5, 0xe8b8d433,
  0x7807c9a2, 0x0f00f934, 0x9609a88e, 0xe10e9818, 0x7f6a0dbb, 0x086d3d2d, 0x91646c97, 0xe6635c01,
  0x6b6b51f4, 0x1c6c6162, 0x856530d8, 0xf262004e, 0x6c0695ed, 0x1b01a57b, 0x8208f4c1, 0xf50fc457,
  0x65b0d9c6, 0x12b7e950, 0x8bbeb8ea, 0xfcb9887c, 0x62dd1ddf, 0x15da2d49, 0x8cd37cf3, 0xfbd44c65,
  0x4db26158, 0x3ab551ce, 0xa3bc0074, 0xd4bb30e2, 0x4adfa541, 0x3dd895d7, 0xa4d1c46d, 0xd3d6f4fb,
  0x4369e96a, 0x346ed9fc, 0xad678846, 0xda60b8d0, 0x44042d73, 0x33031de5, 0xaa0a4c5f, 0xdd0d7cc9,
  0x5005713c, 0x270241aa, 0xbe0b1010, 0xc90c2086, 0x5768b525, 0x206f85b3, 0xb966d409, 0xce61e49f,
  0x5edef90e, 0x29d9c998, 0xb0d09822, 0xc7d7a8b4, 0x59b33d17, 0x2eb40d81, 0xb7bd5c3b, 0xc0ba6cad,
  0xedb88320, 0x9abfb3b6, 0x03b6e20c, 0x74b1d29a, 0xead54739, 0x9dd277af, 0x04db2615, 0x73dc1683,
  0xe3630b12, 0x94643b84, 0x0d6d6a3e, 0x7a6a5aa8, 0xe40ecf0b, 0x9309ff9d, 0x0a00ae27, 0x7d079eb1,
  0xf00f9344, 0x8708a3d2, 0x1e01f268, 0x6906c2fe, 0xf762575d, 0x806567cb, 0x196c3671, 0x6e6b06e7,
  0xfed41b76, 0x89d32be0, 0x10da7a5a, 0x67dd4acc, 0xf9b9df6f, 0x8ebeeff9, 0x17b7be43, 0x60b08ed5,
  0xd6d6a3e8, 0xa1d1937e, 0x38d8c2c4, 0x4fdff252, 0xd1bb67f1, 0xa6bc5767, 0x3fb506dd, 0x48b2364b,
  0xd80d2bda, 0xaf0a1b4c, 0x36034af6, 0x41047a60, 0xdf60efc3, 0xa867df55, 0x316e8eef, 0x4669be79,
  0xcb61b38c, 0xbc66831a, 0x256fd2a0, 0x5268e236, 0xcc0c7795, 0xbb0b4703, 0x220216b9, 0x5505262f,
  0xc5ba3bbe, 0xb2bd0b28, 0x2bb45a92, 0x5cb36a04, 0xc2d7ffa7, 0xb5d0cf31, 0x2cd99e8b, 0x5bdeae1d,
  0x9b64c2b0, 0xec63f226, 0x756aa39c, 0x026d930a, 0x9c0906a9, 0xeb0e363f, 0x72076785, 0x05005713,
  0x95bf4a82, 0xe2b87a14, 0x7bb12bae, 0x0cb61b38, 0x92d28e9b, 0xe5d5be0d, 0x7cdcefb7, 0x0bdbdf21,
  0x86d3d2d4, 0xf1d4e242, 0x68ddb3f8, 0x1fda836e, 0x81be16cd, 0xf6b9265b, 0x6fb077e1, 0x18b74777,
  0x88085ae6, 0xff0f6a70, 0x66063bca, 0x11010b5c, 0x8f659eff, 0xf862ae69, 0x616bffd3, 0x166ccf45,
  0xa00ae278, 0xd70dd2ee, 0x4e048354, 0x3903b3c2, 0xa7672661, 0xd06016f7, 0x4969474d, 0x3e6e77db,
  0xaed16a4a, 0xd9d65adc, 0x40df0b66, 0x37d83bf0, 0xa9bcae53, 0xdebb9ec5, 0x47b2cf7f, 0x30b5ffe9,
  0xbdbdf21c, 0xcabac28a, 0x53b39330, 0x24b4a3a6, 0xbad03605, 0xcdd70693, 0x54de5729, 0x23d967bf,
  0xb3667a2e, 0xc4614ab8, 0x5d681b02, 0x2a6f2b94, 0xb40bbe37, 0xc30c8ea1, 0x5a05df1b, 0x2d02ef8d
]

def otp_crc(src):
    #src = bytearray.fromhex(information)
    crc32val = 0
    for i in range (0,32):
        crc32val = crc32_tab[(crc32val ^ src[i]) & 0xff] ^ (crc32val >> 8);
    crc = hex(crc32val)   # adds a prefix of 0x that we don't want, gives us a string
    return crc[2:]   # here we remove  the 0x prefix.

# make a string exactly 64chars ong with additional 'f' chars, as neded. 
def f_fill_64(s):
    s = s + 'f'*(64-len(s))
    return s

def Read_OTP_with_retries(conn,verbosity=0):
    global BASICDEBUG
    global MOREDEBUG

    if verbosity <= 0 :
        DEBUG = False
        BASICDEBUG = False
        MOREDEBUG = False
    if verbosity == 1 :
        DEBUG = True
        BASICDEBUG = False
        MOREDEBUG = False
    if verbosity == 2 :
        DEBUG = True
        BASICDEBUG = True
        MOREDEBUG = False
    if verbosity >= 3 :
        DEBUG = True
        BASICDEBUG = True
        MOREDEBUG = True
     
    retry = 0
    otp_data = {}
    otp_data['read_success'] = False
    
    while (retry < 3) and (otp_data['read_success'] == False):
    
        if MOREDEBUG:
            print "try:"+str(retry)
        
        # read from device into variable unless given it
        otp_data = Read_OTP(conn,DEBUG)
                
        # unable to read data..? 
        if otp_data['read_success'] == False:
            time.sleep(0.5)
            conn.close()
            conn.open()
            retry = retry+1
            if MOREDEBUG:
                print "read_success false, retrying!"
        
        # if read data is good! 
        if otp_data['read_success'] == True:
            if MOREDEBUG:
                print "read_success true:!"
            return otp_data

    # we return the empty/false one anyway as indicator. 
    return otp_data


def Read_OTP(conn,DEBUG=True):
    if BASICDEBUG:
       print "Read_OTP"

    # flush input serial buffers
    conn.reset_input_buffer()
    # flush other buffers
    #conn.flush()
    conn.reset_output_buffer()
    
    otp_data = {}
    otp_data['written'] = []
    otp_data['lock'] = []

    read_all_lines_success = 0   # once this is 15, it's success! 
    lock = ['','','','','','','','','','','','','','','','']    # fixed size 16, must be initialised. 
    written = ['','','','','','','','','','','','','','','','']

    starttime = int(time.time())  # now in unix seconds.     

    cmd = "otp show\r\n".encode()
    if BASICDEBUG:
        print cmd,
    conn.write(cmd)

    linecount = 0
        
    # breakout on global 30 second timeout ( that's 10 secs per re-try ) 
    now = int(time.time()) # now in unix seconds. 
    if now > starttime + 30:
            #read_success = False
            otp_data['read_success'] = False
            return otp_data

    #print "Data in OTP segments:"
    last_time = time.time()
    while True:
            this_time = time.time()
            if (this_time - last_time) > 1:  # max 1 seconds to handle reading the results of this one command.
                #read_success = False   # timeout hit
                otp_data['read_success'] = False
                if BASICDEBUG:
                    print "timeout reached in Read_OTP"
                return otp_data
            # caution... readline needs a ASCII LF (10 decimal) to think its the end of the line, 
            # ASCII CR (13 decimal ) won't do it, and could block the readline() until 
            # the entire output is sent and a timeout occurs.?  be sure you're sending the right one.
            line  = conn.readline()    
            
            # in non-blocking mode, we get a lot of zero-length data to ignore.. ( see simple_serial_connect timeouts ) 
            if len(line) == 0:
                continue
            
            if MOREDEBUG:
                print "handling line:"+line+"    -> at linecount:"+str(linecount)
            
            words = line.split()   
            
            # there's 16 relevant lines, the last is this one wit hthe '15:' label, and we can savely say we are done.
            #if (len(words) > 0) and (words[0] == "15:"):
            #    otp_data['read_success'] = True
            #    # but don't return yet, as we have to parse this line too... 
                
            # basic sanity check on words sizes and qty ...so we don't try to parse rubbish:
            if (len(words) == 4) and (len(words[0]) <= 3 )  and (len(words[1]) == 1) and (len(words[2]) == 64) and (len(words[3]) == 8) :   
            # example line: ' 0: U ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff e666fea6'
            # example line: '11: U ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff e666fea6'

                if DEBUG: 
                    print line,  # just display the line/s we know about as-is 

            
                blockstring = words[0]   # that's the first wordin the line  ( ie '0:' or '12:' etc )
                blockstring = blockstring[0:-1] # drop the colon on the end
                blocknumber = int(blockstring)
                
                if words[1] == 'U':
                    lock[blocknumber] = "Unlocked\t"
                else:
                    lock[blocknumber] = "Locked\t"

                if words[2][:4] != "ffff":
                    written[blocknumber] = True
                else:
                    written[blocknumber] = False
                    
                # save it into the var we will return later.
                otp_data[blocknumber] = words[2]
                
                # if we read up to the 7th block, that's a measure of success, as we don't currently use the rest...
                #if blocknumber == 7:
                        #read_success = True
                        #if read_all_lines_success  7:
                        #otp_data['read_success'] = True
                        #return otp_data  we'll keep reading till line labeled '15'

                # a state-machine here validates that we actually read all the labeled lines between 0 and 15, as without this partial
                # reads can break stuff: 
                if blocknumber == read_all_lines_success:
                    read_all_lines_success = read_all_lines_success + 1 

            else:
                if MOREDEBUG:
                    print "unknown line, ignoring:"+line

            
            #print "read_all_lines_success  7:"+str(read_all_lines_success)

            # there's 16 relevant lines, the last is this one with the '15:' label, and we can savely say we are done, above.
            if (len(words) > 0) and (words[0] == "15:") and (read_all_lines_success  >= 8 ):
                otp_data['read_success'] = True
                otp_data['written'] = written
                otp_data['lock'] = lock
                return otp_data 

            linecount = linecount+1
            if linecount >= 20:
                print "hit hard linecount limit of 20, aborting."
                otp_data['read_success'] = False
                return otp_data

        
    otp_data['written'] = written
    otp_data['lock'] = lock
    #otp_data['read_success'] = False # must be True for the other data to be considered valid and complete.
    
    return otp_data


def Display_OTP(conn,otp_data=None,DEBUG=True):
  
    if BASICDEBUG:
      print "Display_OTP"
    #lock = ['','','','','','','','','','','','','','','','']    # fixed size 16, must be initialised. 
    #written = ['','','','','','','','','','','','','','','','']
  
    # if we don't already have some, read it quietly
    if otp_data==None:
        otp_data = Read_OTP_with_retries(conn,False)
    
    # unable to read data..? 
    if otp_data['read_success'] == False:
        print "ERROR: unable to read data"
        conn.close()        
        system.exit(1)

    # if read data is good! 
    if otp_data['read_success'] == True:
    
      # get related state infor for these :
      written = otp_data['written']
      lock = otp_data['lock']

      if MOREDEBUG:
        print "read_success true:!"
    
      # all possible blocks...
      for blocknumber in range(0,15):

        if MOREDEBUG:
            print "blocknumber"+str(blocknumber)
            print str(otp_data)

        # don't display data we don't know about from the read: 
        if blocknumber in otp_data:

            if MOREDEBUG:
                print "found blocknumber"+str(blocknumber)
            
            blockstring = str(blocknumber)
            blockstring = blockstring.rjust(2) # make it a fixed 2 chars wide, all the time. 
        
            # ways to interpret it: 
            string = otp_data[blocknumber].decode('hex')
            shortstring = string[:string.index('\xff')]
            caldata = struct.unpack('6f', bytearray.fromhex(otp_data[blocknumber][:48]))
            
            if blocknumber == 0:
                pass
            if blocknumber == 1:
                print "Segment", blockstring, lock[blocknumber], "Manufacturer Info:\t", shortstring, " Written:", written[blocknumber]
            if blocknumber == 2:
                print "Segment", blockstring, lock[blocknumber], "Test Machine Info:\t", shortstring, " Written:", written[blocknumber]
            if blocknumber == 3:
                print "Segment", blockstring, lock[blocknumber], "Manufacturing Info:\t", shortstring, " Written:", written[blocknumber]
            if blocknumber == 4:
                print "Segment", blockstring, lock[blocknumber], "Date of Testing:\t", shortstring, " Written:", written[blocknumber]
            if blocknumber == 5:
                print "Segment", blockstring, lock[blocknumber], "Time of Testing:\t", shortstring, " Written:", written[blocknumber]
            if blocknumber == 6:
                print "Segment", blockstring, lock[blocknumber], "Accel :\t", caldata, " Written:", written[blocknumber]
            if blocknumber == 7:
                print "Segment", blockstring, lock[blocknumber], "Accel :\t", caldata, " Written:", written[blocknumber]
                #read_success = True
                # if we read up to the last block, that's a measure of success.
            # a default for unknown data higher up:
            if blocknumber > 7:
                pass
                #print "Segment", blockstring, lock[blocknumber], "Info:\t", shortstring, " Written:", written[blocknumber]

# write one block:    
def Write_OTP(conn,blocknumber,infostring,DEBUG=True):
        if BASICDEBUG:
             print "Write_OTP"
             
        # flush input serial buffers
        conn.reset_input_buffer()
        # flush other buffers
        #conn.flush()
        conn.reset_output_buffer()
    
        #Write Information
        if BASICDEBUG:
            print "Writing..."
        if blocknumber < 6:
            information = str(str(infostring).encode('hex'))
        elif (blocknumber == 6) or (blocknumber == 7):
            accel_data = [float(x) for x in infostring.split(',') if x]
            packed_accel_data = struct.pack('%sf' % len(accel_data), *accel_data)
            accelhexarray = binascii.hexlify(packed_accel_data)
            information = accelhexarray
            #data = struct.unpack('6f', bytearray.fromhex(accelhexarray))
        else:
            print "Segment ("+str(blocknumber)+") is unavailable or reserved for future!!\n"
            #return -1
            conn.close()
            sys.exit()
    
        if len(information) > 64:
            print "ERROR: Single information ("+str(infostring)+") cannot be larger that 64 Bytes!!"
            conn.close()
            sys.exit()
    
        information = information + 'f'*(64-len(information))
        src = bytearray.fromhex(information)
        crc = otp_crc(src)
        cmd = "otp write " + str(blocknumber) + " " + str(information) + " " + str(crc) + "\r\n".encode()
        if BASICDEBUG:
            print cmd,
        conn.write(cmd)
        time.sleep(0.5)

        # flush input serial buffers
        conn.reset_input_buffer()
        # flush other buffers
        #conn.flush()
        
        # return it in similar format as 'otp read' for easy verify:
        return str(blocknumber) + " " + str(information) + " " + str(crc) + "\r\n"



# verify one block:
def Verify_OTP(conn,blocknumber,infostring,otp_data=None,DEBUG=True):
    if BASICDEBUG:
        print "Verify_OTP"

    # flush input serial buffers
    conn.reset_input_buffer()
    # flush other buffers
    #conn.flush()
    conn.reset_output_buffer()
        
    # if we don't already have some, read it quietly
    if otp_data==None:
        otp_data = Read_OTP_with_retries(conn,DEBUG)
        if BASICDEBUG:
            print "otp re-read done"
    
    # unable to read data..? 
    if otp_data['read_success'] == False:
        print "ERROR: unable to verify data"
        conn.close()        
        system.exit(1)
        
    # flush input serial buffers
    conn.reset_input_buffer()
    # flush other buffers
    #conn.flush()

    # if read data is good! 
    if otp_data['read_success'] == True:
    
        if MOREDEBUG:
            print "looking for block:"+str(blocknumber)
    
        # the single block we are looking for:
        if blocknumber in otp_data:
        
            if MOREDEBUG:
                print "comparing block to otp:"+str(blocknumber)
    
            # let us compare agains either the stringified OR the hexified versions, any are fine. :-) 
            if otp_data[blocknumber] == infostring:
                print "Verify Succeeded! on infostring!"
                return True
        
            information = str(str(infostring).encode('hex'))
            if otp_data[blocknumber] == information:
                print "Verify Succeeded! on information!"
                return True

            ffilled = f_fill_64(information)    
            if otp_data[blocknumber] == ffilled:
                print "Verify Succeeded! on ffilled!"
                return True

            print "Verify Failed!"+str(blocknumber)
            print infostring
            print information
            print otp_data[blocknumber]
            

    # default behaviour:
    return False

    
def Lock_OTP_with_retries(conn,blocknumber,DEBUG=True):

    retry = 0    
    result = False
    while (retry < 3) and (result == False):
        result = Lock_OTP(conn,blocknumber,DEBUG)
    return result  

# we hope u did a verify etc before doing this: 
def Lock_OTP(conn,blocknumber,DEBUG=True):
    if BASICDEBUG:
       print "Lock_OTP"

    # flush input serial buffers
    conn.reset_input_buffer()
    # flush other buffers
    #conn.flush()
    conn.reset_output_buffer()

    cmd = "otp lock "+str(blocknumber)+" "+str(blocknumber)+"\r\n".encode()
    if BASICDEBUG:
        print cmd,
    conn.write(cmd)
    print "Segment " + str(blocknumber) + " probably locked!\n"
   

    # immediate validate: ? 
    # this waits for 2-ish secs for the serial device to get back to us with it's response of "LOCKED" or similar.
    # this relies on the readline() being nonblocking as per simple_serial_connect()s timeout values
    last_time = time.time()
    while (time.time() - last_time) < 2:
        #print "thinking"
        line = conn.readline()  # don't block here, see above.
        if len(line) == 0:
            continue
        if BASICDEBUG:
            print "line:"+line,
        if (line != None) and ( line != "") :
            if line[0] == 'L' or line[0] == 'F':
                print "Segment " + str(blocknumber) + " locked!\n"
                return True
    
    print "Segment " + str(blocknumber) + " lock FAILED.!\n"
    return False            
                

# this is non-blocking on both read() and write() calls due to the use of writeTimeout = 0 and timeout = 0
def nonblocking_serial_connect(port,baud=57600,timeout=5,rtscts=True,dsrdtr=True):

    from sys import platform as _platform
    import serial 

    conn = None
    # attach to the port
    try:
            if "linux" in _platform:
                    # Linux, don't open Mac OS and Win ports
                    if not "COM" in port and not "tty.usb" in port:
                            conn = serial.Serial(port, baud, timeout=0,rtscts=True,dsrdtr=True,writeTimeout = 0)
            elif "darwin" in _platform:
                    # OS X, don't open Windows and Linux ports
                    if not "COM" in port and not "ACM" in port:
                            conn = serial.Serial(port, baud, timeout=0,rtscts=True,dsrdtr=True,writeTimeout = 0)
            elif "win" in _platform:
                    # Windows, don't open POSIX ports
                    if not "/" in port:
                            conn = serial.Serial(port, baud, timeout=0,rtscts=True,dsrdtr=True,writeTimeout = 0)
    except Exception as e:
        # open failed, rate-limit our attempts
        print "Port Not Found!"+str(e)
        #print repr(conn)
        sys.exit()
        # Inappropriate ioctl for device    
    
    return conn
    
    
def getMacAddress(): 
        import os
        mac = ""
        if sys.platform == 'win32': 
            for line in os.popen("ipconfig /all"): 
                if line.lstrip().startswith('Physical Address'): 
                    mac = line.split(':')[1].strip().replace('-',':') 
                    break 
        else: 
            for line in os.popen("/sbin/ifconfig"): 
                if line.find('Ether') > -1: 
                    mac = line.split()[4] 
                    break 
        return mac 
