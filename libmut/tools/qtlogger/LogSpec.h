/*******************************************************************************
 * libmut
 * LogSpec.h
 *
 * Copyright 2007 Donour sizemore (donour@unm.edu)
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
 ******************************************************************************/


#ifndef LOGSPEC_H
#define LOGSPEC_H

#include <QErrorMessage>

class request{

 public:

  QString label;
  unsigned char id;
  QString unit;
  bool active;

  request(QString l, unsigned char i, QString u, bool a){
    label  = l;
    id     = i;
    unit   = u;
    active = a;
  }
};

class LogSpec{

 private:
  
  QString         name;
  QList<request>  requests;

 public:

  /* Default constructor should not be called. It's here only for using the QLists */
  LogSpec(){
    QErrorMessage m;
    m.showMessage("LogSpec() default contructor called!");
    qDebug("LogSpec() default contstructor error");
  }
    

  LogSpec(QString n) { name = n;}
  void AddRequest(request r);
  QString getName();
  unsigned char *ids(unsigned int *nids);
  QList<QString> *labels();
  
  void display();
};


QList<LogSpec>* LoadLogSpecs();

#endif //LOGSPEC_H
