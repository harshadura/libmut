/******************************************************************************
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
 *****************************************************************************/


#ifndef LOGSPEC_H
#define LOGSPEC_H

#include <QtGui>
#include <QErrorMessage>
#include "ui_ViewSpecDlg.h"

class request{

 public:

  QString label;
  unsigned char id;
  QString unit;
  bool active;

  double scaling0;
  double scaling1;
  double scaling2;
  double scaling3;
  double offset;
  
  request(QString l, unsigned char i, QString u, bool a,
	  double scale0, double scale1, double scale2, double scale3){
    label  = l;
    id     = i;
    unit   = u;
    active = a;
    scaling0 = scale0;
    scaling1 = scale1;
    scaling2 = scale2;
    scaling3 = scale3;
  }

  double correct(double val){
    double result = scaling0;
    result += scaling1 * val;
    result += scaling2 * val*val;
    result += scaling3 * val*val*val;
    return result;
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
  QList<QString> *labels();
  //unsigned char *ids(unsigned int *nids);
  


  unsigned int size(){ return requests.size();}
  void display();

  friend class MacLoggerWindow;
  friend class LoggerThread;
};


QList<LogSpec>* LoadLogSpecs();

#endif //LOGSPEC_H
