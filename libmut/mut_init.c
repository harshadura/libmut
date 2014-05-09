/******************************************************************************
 * libmut
 * mut_init.c
 *
 * Copyright 2006-7: Donour sizemore (donour@unm.edu)
 *                   Jack Morrison (jackm@aktivematrix.com) 
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 *
 * Indicated code borrows heavily from freediag.
 * Copyright (C) 2001 Richard Almeida & Ibex Ltd (rpa@ibex.co.uk)
 *****************************************************************************/

#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <termios.h>

#include <sys/time.h>

#include <mut.h>

#ifdef MAC_OSX
#include <IOKit/serial/ioss.h>
#endif /*MAC_OSX*/

#ifdef LINUX 
#include <linux/serial.h>
#endif 

/* FIXME: this is needed for CRTSCTS on linux, test without it */
/*#ifdef LINUX 
#include <asm/termbits.h>
#endif 
*/

/******************************************************************************
 * These routines are from freediag
 *****************************************************************************/

/* set break condition on file fd */
int set_break(int fd, int dtr){
  int flags; 
  int setflags = 0, clearflags = 0;
  
  if (dtr)
    setflags   |= TIOCM_DTR;
  else
    clearflags |= TIOCM_DTR;

  errno = 0;
  if (ioctl(fd, TIOCMGET, &flags) < 0){
    fprintf(stderr, "open: Ioctl TIOCMGET failed %s\n", strerror(errno));
    return (-1);
  }
  flags |= setflags;
  flags &= ~clearflags;
  if (ioctl(fd, TIOCMSET, &flags) < 0){
    fprintf(stderr, "open: Ioctl TIOCMSET failed %s\n", strerror(errno));
    return (-1);
  }
  return(0);
}

/* set rts on file fd */
int set_rts(int fd, int rts){
  int flags;      /* Current flag values. */
  int setflags = 0, clearflags = 0;
  
  if (rts)
    setflags   |= TIOCM_RTS;
  else
    clearflags |= TIOCM_RTS;

  errno = 0;
  if (ioctl(fd, TIOCMGET, &flags) < 0){
    fprintf(stderr, "open: Ioctl TIOCMGET failed %s\n", strerror(errno));
    return (-1);
  }
  flags |= setflags;
  flags &= ~clearflags;
  if (ioctl(fd, TIOCMSET, &flags) < 0){
    fprintf(stderr, "open: Ioctl TIOCMSET failed %s\n", strerror(errno));
    return (-1);
  }
  return(0);
}

/* sleep for ms milliseconds */
int mut_msleep(int ms){
  struct timespec rqst, resp;
  while (ms){
    if (ms > 2){
      rqst.tv_nsec = 2000000;
      ms -= 2;
    }else{
      rqst.tv_nsec = ms * 1000000;
      ms = 0;
    }
    rqst.tv_sec = 0;
    
    while (nanosleep(&rqst, &resp) != 0){
      if (errno == EINTR){ /* Interrupted, continue */
        memcpy(&rqst, &resp, sizeof(resp));
      }else
        return(-1);     /* Some other failure */    
    }
  }
  return(0);
}
/******************************************************************************
 * End of routines from freediag
 *****************************************************************************/

void get_char(int fd){
  unsigned char buf;
  read(fd, &buf, 1);
  if(MUT_DEBUG)
    printf("got: %x\n", (int)buf);
}

int set_baudrate(int fd, int rate){

#ifdef MAC_OSX
  speed_t speed = rate;
  if (ioctl(fd, IOSSIOSPEED, &speed) < 0){
    perror("Failed to set baudrate");
    return -1;
  }else return 0;
  
#endif /*MAC_OSX*/

#ifdef LINUX
 {
   struct serial_struct old_serinfo;
   struct serial_struct new_serinfo;
   struct termios       old_termios;
   struct termios       new_termios;

   if (ioctl(fd, TIOCGSERIAL, &old_serinfo) < 0){
     perror("Cannot get serial info"); return -1;
   }
   new_serinfo = old_serinfo;
   new_serinfo.custom_divisor = new_serinfo.baud_base / rate;
   new_serinfo.flags =   (new_serinfo.flags & ~ASYNC_SPD_MASK)
                       | ASYNC_SPD_CUST;

   if (ioctl(fd, TIOCSSERIAL, &new_serinfo) < 0){
     perror("Cannot set serial info");return -1;
   }

   if (tcgetattr(fd, &old_termios) < 0){
     perror("Cannot get terminal attributes"); return -1;
   }
   
   /* Change settings to 38400 baud.  The driver will
    * substitute this with the custom baud rate.  */
   new_termios = old_termios;
   cfsetispeed(&new_termios, B0);
   cfsetospeed(&new_termios, B38400);

   if (tcsetattr(fd, TCSANOW, &new_termios) < 0){
     perror("Cannot set terminal attributes"); return -1;
   }

   return 0;
 }
#endif /* LINUX */
 
 /* Should not be reached */
 printf("This version of libmut was not compiled with with serial support for this platform\n");
 return -1;
}


/*
  In the event of success 0 is returned. Here are the error codes:

  -1,-2: cannot set baudrate
  -3   : connection timed out 
*/
int mut_init(mut_connection *conn){
  int i;
  struct termios options;
  speed_t speed = conn->baudrate;
  unsigned char rpm=0x21;

  /* set 8N1, and flow control off */
  tcgetattr(conn->fd, &options);
  options.c_cflag &= ~PARENB; 
  options.c_cflag &= ~CSTOPB;
  options.c_cflag &= ~CSIZE;
  options.c_cflag |=  CS8;
  /*options.c_cflag &= ~CRTSCTS;*/ /* FIXME: test without this */
  options.c_iflag &= ~(IXON | IXOFF | IXANY);

  /* Check this against posix, should return as soon as VTIME has expired */
  /* http://www.masoner.net/articles/async.html */
  options.c_cc[VMIN]  = 0; /* timeout */
  options.c_cc[VTIME] = 10; /* timeout */

  tcsetattr(conn->fd, TCSANOW, &options);

  if(set_baudrate(conn->fd, speed) != 0)
    return -1;

  if(MUT_DEBUG)
    printf("Init: Sending 0x01 at 5 baud...\n");

  set_rts(conn->fd, 1);
  set_break(conn->fd, 1);
  mut_msleep(1800);
  set_break(conn->fd, 0);
  mut_msleep(500);
  set_rts(conn->fd, 0);

  /*
    {
    unsigned char buf[2];
    unsigned char init[] = {
    MUTINIT0,
    MUTINIT1,
    MUTINIT2,
    MUTINIT3,
    MUTINIT4,
    MUTINIT5,
    MUTINIT6
    };
  
    for(i=0; i<7; i++){
    write(conn->fd, &init[i], 1);
    get_char(conn->fd);
    }

    }
  */
  
  /* test connection */
  {
    unsigned char rv;
    for(i=0; i<4; i++)
      mut_get_value(conn, rpm, &rv);
    if(mut_get_value(conn,rpm, &rv) < 0){
      if(MUT_DEBUG)
	printf("Timed out\n");
      return -3;
    }

  }
  return 0;
}
