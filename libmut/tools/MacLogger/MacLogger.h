/******************************************************************************
 * libmut
 * MacLogger.h
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

#ifndef MACLOGGER_H
#define MACLOGGER_H

#include "LogSpec.h"
#include "Logging.h"
#include "ui_MacLogger.h"

#define SENSOR_LABEL "Sensor ID"
#define VALUE_LABEL  "Value"

class MacLoggerWindow : public QMainWindow, private Ui::MainWindow
{
  Q_OBJECT;
  

 private:
  
  /* Log elts */
  void set_connected_state(bool s);
  QString get_outfile_name();
  QString log_dir; /* FIXME, set this through menu */

  LoggerThread *activeLogger;

  /* GUI elts */
  QList<LogSpec> *log_specs;


 public:
  MacLoggerWindow(QWidget *parent = 0);


  public slots:
    ;
    void deviceConnect();
    void deviceDisconnect();

    void selectLogDirectory();
    void setSensorValItem(int row, int col, int val);
    void about();
    void LoadSpecFiles();

};



#define LIB_MUT_LICENSE                                                     \
"<h3>MacLogger 2.01 </h3><hr>                                                \
<b>Copyright 2006-7 Donour sizemore (donour@unm.edu)</b><br><br>            \
For more information go to: http://www.cs.unm.edu/~donour/cars/libmut       \
<br><br>                                                                    \
This program is free software; you can redistribute it and/or modify        \
it under the terms of the GNU General Public License as published by        \
the Free Software Foundation; either version 2 of the License, or           \
(at your option) any later version.<br>                                     \
<br>                                                                        \
This program is distributed in the hope that it will be useful,             \
but WITHOUT ANY WARRANTY; without even the implied warranty of              \
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               \
GNU General Public License for more details.<br>                            \
<br>                                                                        \
You should have received a copy of the GNU General Public License           \
along with this program; if not, write to the Free Software                 \
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.<br>"                          



#endif//MACLOGGER_H
