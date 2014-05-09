/******************************************************************************
 * libmut
 * mut_connect.c
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
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>

#include <mut.h>

void mut_free(mut_connection *conn){
  if(conn){
    if(conn->name)
      free(conn->name);
    if(conn->fd >= 0)
      close(conn->fd);
    free(conn);
  }
}

mut_connection *mut_connect_posix(const char *filename, unsigned int baudrate){
  mut_connection *conn;

  conn = malloc(sizeof(mut_connection));
  if(conn == NULL){
    if(MUT_DEBUG)
      perror("Malloc failed,mut_connection");
    return NULL;
  }

  conn->name = malloc(strlen(filename)+1);
  if(conn->name == NULL){
    if(MUT_DEBUG)
      perror("Malloc failed,mut_connection");
    free(conn);
    return NULL;
  }
  strcpy(conn->name, filename);

  if(baudrate == 0){
    printf("We shouldn't be here\n");
    conn->baudrate = MUTSPEEDDEFAULT;
  }
  else{
    conn->baudrate = baudrate;
  }

  conn->fd = open(filename, O_RDWR);
  if(conn->fd < 0){
    if(MUT_DEBUG)
      perror("Open failed");
    mut_free(conn);
    conn = NULL;
  }

  return conn;
}


