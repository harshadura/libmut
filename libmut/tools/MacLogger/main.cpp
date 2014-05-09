#include <QApplication>

#include "MacLogger.h"

int main(int argc, char *argv[]){

  QApplication app(argc, argv);
  MacLoggerWindow *ml = new MacLoggerWindow;
  
  ml->show();
  return app.exec();
}
