/******************************************************************************
 * libmut
 * mut.h
 *
 * Copyright 2006-7 Donour sizemore (donour@unm.edu)
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
 *****************************************************************************/
#ifndef MUTIII
#define MUTIII

#define MUT_DEBUG 1

typedef struct mut_connection_t{
  char *name;
  int fd; 

  unsigned int baudrate;
}mut_connection;

void mut_free(mut_connection *conn);
mut_connection *mut_connect_posix(const char *filename, unsigned int baudrate);

int mut_msleep(int ms);
int mut_init(mut_connection *conn);


int mut_get_value(const mut_connection *conn, const unsigned char sensor, unsigned char *rv);

/******************************************************************************
 * This may be the way we want to do things in the future. For the time being 
 * it is unused though.
 *****************************************************************************/
typedef struct sensor_t{  
  char *label;
  unsigned char address;
  int (*correct)(int);
} mut_sensor;
/*****************************************************************************/

  
/*****************************************************************************/
#define MUTSPEEDDEFAULT  15625 /* baud                                       */
#define MUTINIT0    0xFE  /* These bytes are defined in the protocol for     */
#define MUTINIT1    0xFF  /* the MUT handshaking process                     */
#define MUTINIT2    0xFE  /* |                                               */
#define MUTINIT3    0xFF  /* |                                               */
#define MUTINIT4    0xFD  /* |                                               */
#define MUTINIT5    0xFD  /* |                                               */
#define MUTINIT6    0xFD  /* v                                               */
/*****************************************************************************/

#define MUTTIMING_ID       0x06
#define MUTTIMINGOFFSET    (-20)

#define MUTBATTERY_ID      0x14
#define MUTBATTERYSCALE    (0.0733)

#define MUTTPS_ID          0x17
#define MUTTPSSCALE        ((float)(100.0/255.0))

#define MUTMAF_ID          0x1A
#define MUTMAFSCALE        (6.29)

#define MUTECULOAD_ID      0x1C
#define MUTECULOADSCALE    (0.625)

#define MUTKNOCKSUM_ID     0x26
#define MUTOCTANENUM_ID    0x27
#define MUTOCTANENUMSCALE  1

#define MUTRPM_ID          0x21
#define MUTRPMSCALE        (31.25)

#define MUTIPW_ID          0x29
#define MUTIPWSCALE        (0.256)

#define MUTVSPEED_ID       0x2F
#define MUTVSPEEDSCALE     2 

#define MUTAFRMAP_ID       0x32
#define MUTAFRMAPSCALE     1 

#define DEFAULTINJSCALE    513


int MUTIPW(mut_connection *conn, float *rv);
int MUTOCTANENUM(mut_connection *conn, float *rv);
int MUTKNOCKSUM(mut_connection *conn, float *rv);
int MUTRPM(mut_connection *conn, float *rv); 
int MUTVSPEED(mut_connection *conn, float *rv);
int MUTTPS(mut_connection *conn, float *rv);
int MUTMAF(mut_connection *conn, float *rv);
int MUTTIMING(mut_connection *conn, float *rv);
int MUTBATTERY(mut_connection *conn, float *rv);
int MUTINJLATENCY(mut_connection *conn, float *rv);
int MUTAFRMAP(mut_connection *conn, float *rv);
int MUTLOAD(mut_connection *conn, float *rv);

#endif /*MUTIII*/
 
