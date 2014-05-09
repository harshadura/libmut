/******************************************************************************
 * libmut
 * mut_test.c
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
 ************2*****************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>

#include <sys/select.h>
#include <unistd.h>
#include <sys/time.h>

#include <mut.h>

#define LINE_LEN 80
char *get_data_line(mut_connection *conn){
  int rc;
  float data[6];
  char *line;

  if((rc = MUTRPM(conn,      &data[0])) < 0)
    return NULL;
  if((rc = MUTLOAD(conn,     &data[1])) < 0)
    return NULL;
  if((rc = MUTTIMING(conn,   &data[2])) < 0)
    return NULL;
  if((rc = MUTKNOCKSUM(conn, &data[3])) < 0)
    return NULL;
  if((rc = MUTOCTANENUM(conn,&data[4])) < 0)
    return NULL;
  if((rc = MUTTPS(conn,      &data[5])) < 0)
    return NULL;

  if((line = malloc(LINE_LEN)) == NULL){
    perror("Malloc failed!");
    exit(-1);
  }
  snprintf(line, LINE_LEN, "%4d, %3d, %2d, %2d, %3d, %3d\n", 
	   (int)data[0], (int)data[1], (int)data[2], (int)data[3], (int)data[4], (int)data[5]);
  printf(line);
  return line;
}

int check_keyboard(int wait_sec,int wait_usec){
  int ready = 0;
  struct timeval tv;    
  fd_set fds;
  
  /* this little beauty will cheaply tell us if keyboard input is available*/
  tv.tv_sec  = wait_sec;
  tv.tv_usec = wait_usec;
  FD_SET(STDIN_FILENO, &fds);
  select(1, &fds, NULL, NULL, &tv);
  ready = FD_ISSET(STDIN_FILENO, &fds);  
  return ready;
}

int main(int argc, char *argv[]){
  int input_waiting = 0;
  char *dev, *fn;
  FILE *outfile;

  mut_connection *conn;

  if (argc <=2){
    printf("Usage: perf_logger device log-file\n");
    return -1;
  }

  dev = argv[1];
  fn  = argv[2];

  printf("libM U T logger for Engine Peformance:\n");
  printf("--------------------------------------\n");
  
  printf("Opening log file  :%s\n", fn);
  /* FIXME: At some point in the future, atexit should close this file*/
  if( (outfile = fopen(fn, "w+")) == NULL){
    perror("Log open failed");
    return -1;

  }
  printf("MUT device:%s\n", dev);
  /* FIXME: At some point in the future, atexit should close this file*/
  printf("Press [return] to start:");
  fflush(stdout);
  while(input_waiting == 0){
    input_waiting = check_keyboard(1,0);
    if(input_waiting){
      char buf;
      scanf("%c", &buf);
      input_waiting=0;
      break;
    }
  }

  printf("Connecting...\n");
  conn = mut_connect_posix(dev,0);
  if(conn == NULL){
    perror("Failed");
    return -1;
  }
  if(mut_init(conn) != 0){
    printf("Init failed.\n");
    mut_free(conn);
    return -1;
  }

  printf("Logging, press [return] to quit.");

  while(input_waiting == 0){
    char *line;

    /* Log a line */
    line = get_data_line(conn);
    if(line == NULL){
      printf("data timed out");
      break;
    }

    fprintf(outfile, line);
    free(line);

    input_waiting = check_keyboard(0,250);
    if(input_waiting){
      char buf;
      scanf("%c", &buf);
      input_waiting=0;
      break;
    }
  }

  mut_free(conn);
  return 0;
}
