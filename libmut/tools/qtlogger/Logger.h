/******************************************************************************
 * libmut
 * Logger.h
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

#ifndef LOGGER_H
#define LOGGER_H

#include <QString>
#include <QThread>
#include <QMutex>

#include <LogSpec.h>

extern "C" {
#include "../../mut.h"
}

/* c++ file i/o dsis so lame */
#include <fstream>
using std::ofstream;

class LoggerThread : public QThread{
  Q_OBJECT;

  ofstream   outfile;
  QMutex     stop_lock;
  
  unsigned char *ids;
  unsigned int   nids;
  
  QList<QString> *labels;
  
  mut_connection *conn;
  
 signals:
  void screenLog(const QString & s);
  void updateSampleRate(const unsigned int s);
  
 public:

  LoggerThread(LogSpec *ls){
    ids = ls->ids(&nids);
    labels = ls->labels();
  }
  ~LoggerThread(){
    free(ids);
    delete labels;
  }

  int log(QWidget *parent,const QString *log_fn, const QString *dev_fn);
  void fail(QString qs);
  void stop_log();
  void run();
  QString get_data_line(mut_connection *conn);
};


#endif /*LOGGER_H*/
