/******************************************************************************
 * libmut
 * main_window.cpp
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

#include <QFileDialog>
#include <QTextEdit>
#include <QDateTime>
#include <QtGui>

#include "main_window.h"
#include "Logger.h"


/***************************************************************************/
/* FIXME: regular C */
#include <dirent.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#define OSX_PREFIX    "cu"
#define LINUX_PREFIX  "ttyS"

#define MAX_DEVS     128 /* FIXME: this should grow */
extern "C" {
char** get_list_posix_dev(){
  char **devices;
  int i = 0;
  DIR   *dirp;
  struct dirent *dp;
  
  if(!(dirp = opendir("/dev"))){ /* leak? */
    perror("Open dev failed");
    return NULL;
  }
  
  if((devices = (char**)malloc(sizeof(char*) * MAX_DEVS)) == NULL){
    perror("Malloc broken");
    return NULL;
  }
  
  for(dp = readdir(dirp); 
      dp != NULL && i < MAX_DEVS-1; /* last elt is end marker */ 
      dp = readdir(dirp)){
    
    if( (dp = readdir(dirp)) != NULL ) /* leak? */
      if( strstr(dp->d_name, OSX_PREFIX) ){
	devices[i] = (char*)malloc(strlen(dp->d_name)+1); /* FIXME: check return value */
	strcpy(devices[i++], dp->d_name);
      }
  }
  devices[i] = NULL; /* Mark the end */
  return devices;
}
}
/*******************************************************************************/

/*

class MapTable : public QTableWidget{
  
private:
  int LoadScale; 
  int RPMScale;

public:
  
  MapTable(int rows, int cols){
    int i;
    LoadScale = 10; 
    RPMScale  = 1000;

    setColumnCount(cols);
    QStringList clabels;
    for(i=1; i<=cols; i++){
      clabels.append(QString("%1").arg(i*LoadScale));
    }
    setHorizontalHeaderLabels(clabels);
    for(i=0 ; i < cols ; i++){
      resizeColumnToContents(i);
    } 

    setRowCount(rows);
    QStringList vlabels;
    for(i=1; i<=rows; i++){
      vlabels.append(QString("%1").arg(i*RPMScale));
    }
    setVerticalHeaderLabels(vlabels);
    for(i=0 ; i < rows ; i++){
      resizeRowToContents(i);
    }  
  }

  virtual ~MapTable(){ }
};
*/


MainWindow::MainWindow(){
  QWidget *w = new QWidget;
  setCentralWidget(w);

  createActions();
  createMenus();
  createIOControls();
  createSpecControls();
  createStatus();
  
  //MapTable *test_map = new MapTable(8,20);
  
  QVBoxLayout *vbox = new QVBoxLayout;
  vbox->setMargin(2);
  vbox->addWidget(IOControls);
  vbox->addWidget(specBox);
  vbox->addWidget(statusBox);
  //vbox->addWidget(test_map);
  w->setLayout(vbox);

  setWindowTitle(tr("Menus"));
  setMinimumSize(160, 160);
  resize(480, 320);

  logger = NULL;
}

void MainWindow::contextMenuEvent(QContextMenuEvent *event){
  QMenu menu(this);
  menu.exec(event->globalPos());
}

void MainWindow::stopLog(){
  logger->stop_log();
  logger->wait();
  delete logger;

  stopLogBut->setDisabled(true);
  startLogBut->setDisabled(false);
}

void MainWindow::startLog(){

  if(log_specs == NULL || log_specs->size() == 0 ){
    QMessageBox::critical(this, tr("No spec file"),
			  tr("No log specs are loaded."));
    return ;
  }

  int idx = specComboBox->currentIndex();

  LogSpec ls = log_specs->value(idx);
  logger = new LoggerThread(&ls);

  QString filename(tr("mut-log-"));
  QDateTime date = QDateTime::currentDateTime();
  filename.append( date.toString(Qt::ISODate));
  filename += ".csv";

  QString label("Logfile: ");
  label.append(filename);
  logfile->setText(label);

  QString dev_dir = "/dev/";
  QString dev_fn = dev_dir + portComboBox->currentText();
  QObject::connect(logger,    SIGNAL(screenLog(const QString &)),
		   logStatus, SLOT(     append(const QString &)));
  QObject::connect(logger,SIGNAL(updateSampleRate(const unsigned int)),
		   this,    SLOT(   setSampleRate(const unsigned int)));
  
  if(logger->log(this,&filename, &dev_fn) != 0){ 
    delete logger;
    return;
  }
  
  stopLogBut->setDisabled(false);
  startLogBut->setDisabled(true);
}

void MainWindow::setSampleRate(const unsigned int rate){
  QString label = QString(tr("Samplerate: %1 hz").arg(rate));
  sampleRate->setText(label);

}
void MainWindow::open(){
}

void MainWindow::save(){
}

void MainWindow::about(){
  QMessageBox::about(this, tr("About libmut and MutLog"),tr(LIB_MUT_LICENSE));
}

void MainWindow::viewSpec(){
  int idx = specComboBox->currentIndex();

  if(log_specs)
    if(log_specs->size() >0 )
      (log_specs->value(idx)).display();
}


void MainWindow::createActions()
{

  /*
      openAct = new QAction(tr("&Open..."), this);
      openAct->setShortcut(tr("Ctrl+O"));
      openAct->setStatusTip(tr("Open an existing file"));
      connect(openAct, SIGNAL(triggered()), this, SLOT(open()));
      
      saveAct = new QAction(tr("&Save"), this);
      saveAct->setShortcut(tr("Ctrl+S"));
      saveAct->setStatusTip(tr("Save the document to disk"));
      connect(saveAct, SIGNAL(triggered()), this, SLOT(save()));
  */

  exitAct = new QAction(tr("E&xit"), this);
  exitAct->setShortcut(tr("Ctrl+Q"));
  exitAct->setStatusTip(tr("Exit the application"));
  connect(exitAct, SIGNAL(triggered()), this, SLOT(close()));

  aboutAct = new QAction(tr("&About"), this);
  aboutAct->setStatusTip(tr("Show the application's About box"));
  connect(aboutAct, SIGNAL(triggered()), this, SLOT(about()));

  aboutQtAct = new QAction(tr("About &Qt"), this);
  aboutQtAct->setStatusTip(tr("Show the Qt library's About box"));
  connect(aboutQtAct, SIGNAL(triggered()), qApp, SLOT(aboutQt()));
}

void MainWindow::createMenus(){
  fileMenu = menuBar()->addMenu(tr("&File"));
  //fileMenu->addAction(openAct);
  //fileMenu->addAction(saveAct);
  fileMenu->addSeparator();
  fileMenu->addAction(exitAct);

  helpMenu = menuBar()->addMenu(tr("&Help"));
  helpMenu->addAction(aboutAct);
  helpMenu->addAction(aboutQtAct);
}


void MainWindow::createSpecControls(){
  specBox = new QGroupBox(tr("LogSpec"));
  QHBoxLayout *layout = new QHBoxLayout;

  specComboBox = new QComboBox();
  layout->addWidget(specComboBox);

  log_specs = LoadLogSpecs();
  if(log_specs){
    QList<LogSpec>::iterator j;
    for(j = log_specs->begin(); j != log_specs->end(); j++){
      specComboBox->addItem(j->getName());
    }
  }

  specViewBut = new QPushButton(tr("View"));
  layout->addWidget(specViewBut);
  QObject::connect(specViewBut,SIGNAL(clicked()),this,SLOT(viewSpec()));
  if(log_specs == NULL)
    specViewBut->setDisabled(true);

  specBox->setLayout(layout);
}

void MainWindow::createIOControls(){
  IOControls = new QGroupBox(tr("Controls"));
  QHBoxLayout *layout = new QHBoxLayout;

  startLogBut = new QPushButton(tr("Start Logger"));
  layout->addWidget(startLogBut);
  QObject::connect(startLogBut,SIGNAL(clicked()),this,SLOT(startLog()));

  stopLogBut = new QPushButton(tr("Stop Logger"));
  stopLogBut->setDisabled(true);
  QObject::connect(stopLogBut,SIGNAL(clicked()),this,SLOT(stopLog()));
  layout->addWidget(stopLogBut);


  portComboBox = new QComboBox();
  layout->addWidget(portComboBox);
  char **devs;
  int i;
  devs  = get_list_posix_dev();
  for(i=0; devs[i]; i++){
    QString qs(devs[i]);
    portComboBox->addItem(qs);
    free(devs[i]);
  }
  free(devs);
  
  IOControls->setLayout(layout);
}

void MainWindow::createStatus(){
  statusBox = new QGroupBox(tr("Status"));
  QGridLayout *layout = new QGridLayout;

  logfile = new QLabel(tr(""));
  layout->addWidget(logfile,1,0);

  sampleRate = new QLabel(tr("Samplerate:"));
  layout->addWidget(sampleRate,2,0);

  logStatus = new QTextEdit();
  logStatus->setReadOnly(true);
  layout->addWidget(logStatus,3,0);
  statusBox->setLayout(layout);
  
}
