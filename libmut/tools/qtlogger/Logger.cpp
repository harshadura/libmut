/******************************************************************************
 * libmut
 * Logger.cpp
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

#include <QMessageBox>
#include <QTime>
#include <QTextOStream>

#include "Logger.h"

QString LoggerThread::get_data_line(mut_connection *conn){
  QString qs;
  unsigned char buf;
  unsigned int i;
  for(i=0;  i < nids; i++){
    if(mut_get_value(conn, ids[i], &buf) < 0)
      return NULL;
    else
      qs += QString("%1,").arg((int)buf);
  }
  return qs;
}

int LoggerThread::log(QWidget *parent, const QString *log_fn, const QString *dev_fn){
  QString qs;
  QByteArray filename(log_fn->toAscii());
  QByteArray devfile(dev_fn->toAscii());

  outfile.open(filename.data()); /* FIXME: check for error */

  conn = NULL;
  while(conn == NULL){
    int reply;
    conn = mut_connect_posix(devfile.data(), 0);
    if(conn == NULL){
      reply = QMessageBox::critical(parent, *dev_fn,
				    tr("Open device failed."),
				    QMessageBox::Abort,
				    QMessageBox::Retry,
				    QMessageBox::Ignore);
      if(reply != QMessageBox::Retry)
	return -1;      
    }   
  }
  
  stop_lock.lock();
  start();
  return 0;
}

void LoggerThread::stop_log(){
  stop_lock.unlock();
}

void LoggerThread::fail(QString qs){
  emit screenLog(qs);
  while(!stop_lock.tryLock())
    mut_msleep(50);

  outfile.close();
  return;
  
}
void LoggerThread::run(){

  outfile << "#";
  QList<QString>::iterator i;
  for(i = labels->begin(); i != labels->end(); i++){
    outfile << (i->toAscii()).data() << ",";
  }
  outfile <<"\n";

  QString qs;
  
  if(conn == NULL){
    /* We got here with a dead connection handle. Go to sleep */
    qs = "No connection available: sleeping";
    return fail(qs);
  }
  
  qs = "5 baud init...";
  emit screenLog(qs);
  
  /* FIXME: mut_init isn't yet smart enough to tell you it failed*/
  if(mut_init(conn) != 0){
    qs = "Connect failed";
    return fail(qs);
  }else{
    qs = "Connected";
    emit screenLog(qs);
  }
  
  int counter=1;
  QTime etime,sampletime; 
  sampletime.start(); etime.start();    
  while(!stop_lock.tryLock()){
    float time = etime.elapsed() / 1000.0; /* time in ms */

    QString line = QString("%1,\t").arg(time);
    QString data = get_data_line(conn);
    if(data.length() == 0){
      qs = "Connection timed out";
      return fail(qs);
    }
    line += data;
    
    if(counter++ % 20 == 0){ 
      int elapsed     = sampletime.restart(); /* time in ms */
      int sample_rate = (counter*1000) / elapsed;
      counter = 1;
      emit updateSampleRate(sample_rate);
      emit screenLog(line);
    }
    
    outfile << (line.toAscii()).data();
    outfile << endl;
    
  }
  
  outfile.close();
}
