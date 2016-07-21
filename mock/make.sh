#/usr/local/bin/gcc-4.8 -std=c99 otp_cmd.c -o otp_cmd

/usr/local/bin/gcc-4.8 -std=c99 -c otp_lib.c 
/usr/local/bin/gcc-4.8 -std=c99 -c otp_cmd.c 
/usr/local/bin/gcc-4.8 -std=c99 -c crc32.c
/usr/local/bin/gcc-4.8 -std=c99 otp_lib.o otp_cmd.o crc32.o -o otp
