/******************************************************************************
 * libmut
 * main_window.h
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

#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QGroupBox>
#include <QPushButton>
#include <QLabel>
#include <QComboBox>
#include <QTextEdit>

#include "Logger.h"
#include "LogSpec.h"

#define LIB_MUT_LICENSE					       			\
"<b>Copyright 2006 Donour sizemore (donour@unm.edu)</b><br> 			\
For more information: http://www.cs.unm.edu/~donour/cars/libmut			\
<br><br>			    						\
This program is free software; you can redistribute it and/or modify<br>	\
it under the terms of the GNU General Public License as published by<br>	\
the Free Software Foundation; either version 2 of the License, or<br>		\
(at your option) any later version.<br>		      				\
<br>   									      	\
This program is distributed in the hope that it will be useful,<br>		\
but WITHOUT ANY WARRANTY; without even the implied warranty of<br>		\
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the<br>		\
GNU General Public License for more details.<br>			       	\
<br>		     								\
You should have received a copy of the GNU General Public License<br>		\
along with this program; if not, write to the Free Software<br>		      	\
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.<br>"				

class QAction;
class QActionGroup;
class QLabel;
 class QMenu;

class MainWindow : public QMainWindow{
  Q_OBJECT;
  
 public:
  MainWindow();
  
 protected:
  void contextMenuEvent(QContextMenuEvent *event);
  
 private slots:
   void startLog();
   void stopLog();
   void setSampleRate(const unsigned int);
   void open();
   void save();
   void about();
   void viewSpec();


 private:

   /* MENUS */
   void createActions();
   void createMenus();
   
   QMenu *fileMenu;
   QMenu *formatMenu;
   QMenu *helpMenu;
   QActionGroup *alignmentGroup;
   QAction *openAct;
   QAction *saveAct;
   QAction *exitAct;
   QAction *aboutAct;
   QAction *aboutQtAct;
   QLabel *infoLabel;

   LoggerThread *logger;

   QList<LogSpec> *log_specs;

   /* Log I/O Control */
   void createIOControls();
   QGroupBox *IOControls;
   QPushButton *startLogBut;
   QPushButton *stopLogBut;
   QComboBox   *portComboBox;

   /* LogSpec Controls */
   void createSpecControls();
   QGroupBox   *specBox;
   QComboBox   *specComboBox;
   QPushButton *specViewBut;

   /* Status */
   void createStatus();
   QGroupBox *statusBox;
   QLabel *logfile;
   QLabel *sampleRate;
   QTextEdit *logStatus;

};
#endif /* MAINWINDOW_H */
