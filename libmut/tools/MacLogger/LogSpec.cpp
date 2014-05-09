/*******************************************************************************
 * libmut
 * LogSpec.cpp
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
 ******************************************************************************/


#include <iostream>
#include <QtXml/QXmlSimpleReader>
#include <QDomDocument>
#include <QFile>
#include <QtGui>

#include <LogSpec.h>

QTextStream cin(stdin, QIODevice::ReadOnly);
QTextStream cout(stdout, QIODevice::WriteOnly);
QTextStream cerr(stderr, QIODevice::WriteOnly);
 
QList<LogSpec>* LoadLogSpecs(){
  QList<LogSpec> *specs = new QList<LogSpec>;

  /* FIXME: define a spec/ dir and read all files from there */
  QDomDocument doc;
  QFile file(":/specs/requestID.xml");

  if(!file.open(QIODevice::ReadOnly)){
    qDebug("opening file failed");
    return NULL;
  }
    
  if(!doc.setContent(&file) )
    qDebug("Set Content failed"); 
  file.close();
  

  QDomElement root = doc.documentElement();
  if(root.tagName() == "MacLogger"){ // FIXME: better rootname
    QDomNode n = root.firstChild();

    while(!n.isNull()){ /* For each ECU */

      QDomElement e = n.toElement();
      if(!e.isNull() && e.tagName() == "ECU"){
	LogSpec cur_spec(e.text());
	
      
	/* The next sibling are the items */
	n = n.nextSibling();
	if(n.isNull())
	  break; /* FIXME: can this be nicer:? */
	
	
	/* Reading requests */
	e = n.toElement();
	if(!e.isNull() && e.tagName() == "Sensors"){
	  
	  QDomNode signal = e.firstChild();	
	  while(!signal.isNull()){
 	    QDomElement sigelt = signal.toElement();
	    if(!sigelt.isNull()){
	      if(sigelt.tagName() == "Request"){
		
		QString l       = sigelt.attribute("LogReference");
		unsigned char i = sigelt.attribute("RequestID").toLong(NULL, 16);
		QString u       = sigelt.attribute("Unit");
		double scale0   = sigelt.attribute("Scale0").toDouble();
		double scale1   = sigelt.attribute("Scale1").toDouble();
		double scale2   = sigelt.attribute("Scale2").toDouble();
		double scale3   = sigelt.attribute("Scale3").toDouble();


		QString logged   = sigelt.attribute("Active");
		bool active = true;
		if(logged == "N" || logged == "n" || logged == "0")
		  active = false;
		
		request r(l,i,u,active,scale0, scale1, scale2, scale3);
		cur_spec.AddRequest(r);
	      }
	    }
	    signal = signal.nextSibling();
	  }
	}
	specs->append(cur_spec);
      }
      n = n.nextSibling();
    }
  }
  
  return specs;
}

void LogSpec::AddRequest(request r){
  requests.append(r);
}


QString LogSpec::getName(){
  return name;
}

QList<QString> *LogSpec::labels(){
  QList<QString> *l = new QList<QString>;
 
  QList<request>::iterator i;
  for(i = requests.begin(); i != requests.end(); i++)
    l->append(i->label); // FIXME: add units

  return l;
}

#include <QTableWidget>
void LogSpec::display(){
  cout << "[LogSpec] " << name << "\t" << requests.size() << endl;
  
  QList<request>::iterator i;
  for(i = requests.begin(); i != requests.end(); i++){
    cout << "\t->" << i->label 
	 <<"\t"	   << i->id
	 <<"\t"	   << i->unit 
	 <<"\t"	   << i->active
	 << endl;
  } 

  
  QTableWidget *tableWidget = new QTableWidget(requests.size(), 4, NULL); //FIXME: leak?
  
  QStringList clabels;
  clabels.append(QString("Label"));
  clabels.append(QString("Unit"));
  clabels.append(QString("ID"));
  clabels.append(QString("Correction Factor"));
  tableWidget->setHorizontalHeaderLabels(clabels);

  QTableWidgetItem *item;
  int row = 0;
  for(i = requests.begin(); i != requests.end(); i++){
    item = new QTableWidgetItem(i->label);
    tableWidget->setItem(row, 0, item);    
    item = new QTableWidgetItem(i->unit);
    tableWidget->setItem(row, 1, item);    
    item = new QTableWidgetItem(QString("%1").arg((unsigned int)i->id));
    tableWidget->setItem(row, 2, item);    
    item = new QTableWidgetItem(QString("%1*x^3 + %2*x^2 + %3*x + %4").arg((double)i->scaling3).arg((double)i->scaling2).arg((double)i->scaling1).arg((double)i->scaling0));
    tableWidget->setItem(row, 3, item);    
    row++;
  }

  tableWidget->resize(350,500);
  tableWidget->show();

}
