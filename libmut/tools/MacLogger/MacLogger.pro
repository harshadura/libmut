TEMPLATE = app
TARGET   = 
DEPENDPATH  += .
INCLUDEPATH += .
INCLUDEPATH += ../../
LIBS += -L../../ -lmut

QT += xml thread
RESOURCES = MacLogger.qrc

# Input
HEADERS += LogSpec.h    \
           MacLogger.h  \
           Logging.h    \
           ../../mut.h
FORMS   += MacLogger.ui ViewSpecDlg.ui
SOURCES += LogSpec.cpp         \
           MacLogger.cpp       \
           main.cpp            \
           Logging.cpp         

unix {
           DEFINES += LINUX
}

macx {
           ICON = icons/MacLogger.icns
           DEFINES -= LINUX
           DEFINES += MAC_OSX
#           QMAKE_MAC_SDK=/Developer/SDKs/MacOSX10.4u.sdk     
           QMAKE_MAC_SDK=/Developer/SDKs/MacOSX10.5.sdk     
           CONFIG += x86 ppc
}

