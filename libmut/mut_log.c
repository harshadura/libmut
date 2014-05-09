/******************************************************************************
 * libmut
 * mut_log.c
 *
 * Copyright 2006 Donour sizemore (donour@unm.edu)
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

#include <mut.h>
#include <stdio.h>
#include <unistd.h>



int mut_get_predefined_sensor(const mut_connection *conn,
			      const unsigned char id,
			      const float scale,
			      const float offset,
			      float *rv){

  unsigned char buf;
  int rc;
  rc = mut_get_value(conn, id, &buf);
  *rv = (float)buf * scale + offset;

  if(MUT_DEBUG && rc<0)
    printf("Get sensor %d failed\n", id);

  return rc;
}

int MUTIPW(mut_connection *conn, float *rv){
 return mut_get_predefined_sensor(conn, MUTIPW_ID, MUTIPWSCALE, 0, rv);
}
int MUTOCTANENUM(mut_connection *conn, float *rv){
 return mut_get_predefined_sensor(conn, MUTOCTANENUM_ID, 
				  MUTOCTANENUMSCALE, 0, rv);
}
int MUTKNOCKSUM(mut_connection *conn, float *rv){
 return mut_get_predefined_sensor(conn, MUTKNOCKSUM_ID,1, 0, rv);
}
int MUTRPM(mut_connection *conn, float *rv){ 
 return mut_get_predefined_sensor(conn, MUTRPM_ID,MUTRPMSCALE, 0, rv);
}

int MUTVSPEED(mut_connection *conn, float *rv){
  return mut_get_predefined_sensor(conn, MUTVSPEED_ID,MUTVSPEEDSCALE, 0, rv);
}
int MUTTPS(mut_connection *conn, float *rv){
  return mut_get_predefined_sensor(conn, MUTTPS_ID,MUTTPSSCALE, 0, rv);
}
int MUTMAF(mut_connection *conn, float *rv){
  return mut_get_predefined_sensor(conn, MUTMAF_ID,MUTMAFSCALE, 0, rv);
}
int MUTTIMING(mut_connection *conn, float *rv){
  return mut_get_predefined_sensor(conn, MUTTIMING_ID,1, MUTTIMINGOFFSET, rv);
}
int MUTBATTERY(mut_connection *conn, float *rv){
  return mut_get_predefined_sensor(conn, MUTBATTERY_ID, MUTBATTERYSCALE,0, rv);
}
int MUTINJLATENCY(mut_connection *conn, float *rv){
  return mut_get_predefined_sensor(conn, MUTBATTERY_ID, 
				   MUTBATTERYSCALE* -0.1026,
				   1.8741, /*works because battery offset=0 */ 
				   rv);
}
int MUTAFRMAP(mut_connection *conn, float *rv){
  return mut_get_predefined_sensor(conn, MUTAFRMAP_ID, MUTAFRMAPSCALE,0, rv);
}

int MUTLOAD(mut_connection *conn, float *rv){
  int rc;
  float ipw, inj_lat, afrmap;

  if((rc = MUTIPW(conn, &ipw))< 0)
    return rc;
  
  if((rc = MUTINJLATENCY(conn, &inj_lat)) < 0)
    return rc;
  
  if((rc = MUTAFRMAP(conn, &afrmap)) < 0)
    return rc;

  *rv = 5 * DEFAULTINJSCALE * (ipw - inj_lat) / afrmap;
  return 0;
}

int mut_get_value(const mut_connection *conn, 
		  const unsigned char id,
		  unsigned char *rv){
  int nbytes;
  unsigned char buf[2];
  
  if (conn == NULL){
    if(MUT_DEBUG)
      printf("Tried to get value from dead connection!\n");
    return -1; /* No connection */
  }

  write(conn->fd, &id, 1);
  
  nbytes = read(conn->fd, buf, 2);
  if(nbytes != 2){
    if(MUT_DEBUG)
      printf("Value request didn't return 2 bytes: returned %d\n", nbytes);
    return -2; /* timeout */
  }

  *rv = buf[1];
  return 0;
} 


