/******************************************************************************
 * libmut
 * MacLogger.cpp
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


#include <QtGui>

#include "MacLogger.h"


/***********************&*****************************************************/
/* FIXME: regular C */
#include <dirent.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#define OSX_PREFIX    "cu"
#define LINUX_PREFIX  "ttyS"

#ifdef LINUX
#define SERIAL_PREFIX LINUX_PREFIX
#endif
#ifdef MAC_OSX
#define SERIAL_PREFIX OSX_PREFIX
#endif

#define MAX_DEVS     128 /* FIXME: this should grow */
extern "C" {
char** get_list_posix_dev(){
  char **devices;
  int i = 0;
  DIR   *dirp;
  struct dirent *dp;

  
  if(!(dirp = opendir("/dev"))){
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
    
    if(dp != NULL) /* leak? */
      if( strstr(dp->d_name, SERIAL_PREFIX) ){
        devices[i] = (char*)malloc(strlen(dp->d_name)+1); /* FIXME: check return value */
        strcpy(devices[i++], dp->d_name);
      }
  }
  devices[i] = NULL; /* Mark the end */
  closedir(dirp);
  return devices;
}
}
/*****************************************************************************/

MacLoggerWindow::MacLoggerWindow(QWidget *parent){
  setupUi(this);

  log_dir = ""; // FIXME: this should be a better default

  /* Get list of serial devices and insert them into options box */
  char **devs  = get_list_posix_dev();
  {
    /* put them in the list BACKWARDS */
    int i = 0; 
    while(devs[i]) i++;
    for(; i>0;){
      QString qs(devs[--i]);
      PortComboBox->addItem(qs);
      free(devs[i]);
    }
  }
  free(devs);
  
  log_specs = NULL;
  LoadSpecFiles();

  /* Set sensor table headers */
  QHeaderView *headerView = sensorValues->horizontalHeader();
  headerView->setResizeMode(QHeaderView::Stretch);
  QStringList l;
  l << SENSOR_LABEL << VALUE_LABEL;
  sensorValues->setHorizontalHeaderLabels(l);


  activeLogger = NULL;

  connect(actionConnect, SIGNAL(activated()), this, SLOT(deviceConnect() ) );
  connect(actionDisconnect, SIGNAL(activated()), this, SLOT(deviceDisconnect() ) );
  connect(actionChoose_Log_Directory, SIGNAL(activated()), this, SLOT(selectLogDirectory()) );
  connect(actionAbout, SIGNAL(activated()), this, SLOT(about()) );
  connect(specReloadButton, SIGNAL(clicked()), this, SLOT(LoadSpecFiles()));


  set_connected_state(false);
  ConnectStatus->clear();
}

void MacLoggerWindow::selectLogDirectory(){
  QString dir = QFileDialog::getExistingDirectory(this, tr("Open Directory"),
						  "/home",
						  QFileDialog::ShowDirsOnly
						  | QFileDialog::DontResolveSymlinks);
  if(dir.size() > 0){
    log_dir = dir+"/";
    ConnectStatus->append("i: Log Directory changed to: " + dir);
  }
}

void MacLoggerWindow::setSensorValItem(int row, int col, int val){
 QTableWidgetItem *item = new QTableWidgetItem(QString("%1").arg(val));
 sensorValues->setItem(row, col, item);

}

void MacLoggerWindow::about(){
  QMessageBox::about(this, tr("About libmut and MacLogger"),tr(LIB_MUT_LICENSE));
}

void MacLoggerWindow::LoadSpecFiles(){
  LogSpecComboBox->clear();

  if(log_specs != NULL)
    delete log_specs;

  log_specs = LoadLogSpecs();
  if(log_specs){
    QList<LogSpec>::iterator j;
    for(j = log_specs->begin(); j != log_specs->end(); j++){
      LogSpecComboBox->addItem(j->getName());
    }
  }

  ConnectStatus->append("i: Specs reloaded.");
}

