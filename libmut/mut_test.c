/******************************************************************************
 * libmut
 * mut_test.c
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

#include <stdio.h>

#include <mut.h>

int main(int argc, char *argv[]){
  int sample_count = 50;
  char *dev;

  mut_connection *conn;

  if (argc <=1){
    printf("Usage: mut_test device\n");
    return -1;
  }

  dev = argv[1];

  printf("MUT protocol test: %s\n", dev);
  printf("-----------------------------------\n");

  conn = mut_connect_posix(dev,0);
  if(conn == NULL){
    printf("Connect failed\n");
    return -1;
  }
  
  if(mut_init(conn) != 0){
    printf("Init failed. \n");
    mut_free(conn);
    return -1;
  }

  for(;sample_count > 0; sample_count--){
    int rc; 
    float rpm, kc, octane, tps;

    if( (rc = MUTRPM(conn, &rpm)) < 0)
      break;
    if((rc = MUTKNOCKSUM(conn, &kc)) < 0)
      break;
    if((rc = MUTOCTANENUM(conn, &octane)) < 0)
      break;
    if((rc = MUTTPS(conn, &tps)) < 0)
      break;

    /*rpm = (int)((float)mut_get_value(conn, MUTRPM) * MUTRPMSCALE);
    kc = (int)((float)mut_get_value(conn, MUTKNOCKSUM));
    octane = (int)((float)mut_get_value(conn, MUTOCTANENUM));*/
    printf("RPM: %d \t knocksum: %d \t tps: %d \t octane: %d\n", (int)rpm, (int)kc, (int)tps,(int)octane);    
    mut_msleep(100);
  }
    
  mut_free(conn);
  return 0;
}
