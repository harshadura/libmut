/*******************************************************************************
 * libmut
 * Logging.h
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

#ifndef LOGGING_H
#define LOGGING_H

#include <QString>
#include <QThread>
#include <QMutex>

#include <LogSpec.h>

extern "C" {
#include "../../mut.h"
}


/* c++ file i/o is so lame */
#include <fstream>
using std::ofstream;

class LoggerThread : public QThread{
  Q_OBJECT;

  ofstream   outfile;
  QMutex     stop_lock;

  mut_connection *conn;
  LogSpec spec;

 signals:
  void progressUpdate(int v);
  void logToBuffer(QString s);  
  void updateSensorValues(int row, int col, int d);
  void barShowMessage(QString s);

 public:

  LoggerThread(LogSpec s){spec = s;}

  int log(QWidget *parent, unsigned int baudrate, QString filename, QString devfn);
  void run();
  void stop(){ stop_lock.unlock();}
  void fail(QString qs);
};


#endif /* LOGGING_H */
