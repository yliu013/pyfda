# -*- coding: utf-8 -*-
#
# This file is part of the pyFDA project hosted at https://github.com/chipmuenk/pyfda
#
# Copyright © pyFDA Project Contributors
# Licensed under the terms of the MIT License
# (see file LICENSE in root directory for details)

"""
Tabbed container with all plot widgets
"""
from __future__ import print_function, division, unicode_literals, absolute_import

import logging
logger = logging.getLogger(__name__)

from ..compat import QTabWidget, QVBoxLayout, QEvent, QtCore, pyqtSlot, pyqtSignal

from pyfda.pyfda_rc import params

from pyfda.plot_widgets import (plot_hf, plot_phi, plot_pz, plot_tau_g, plot_impz,
                          plot_3d)

#------------------------------------------------------------------------------
class PlotTabWidgets(QTabWidget):
       
    sig_rx = pyqtSignal(dict)
    sig_tx = pyqtSignal(dict) # not used yet
    
    def __init__(self, parent):
        super(PlotTabWidgets, self).__init__(parent)

        self.pltHf = plot_hf.PlotHf(self)
        self.pltPhi = plot_phi.PlotPhi(self)
        self.pltPZ = plot_pz.PlotPZ(self)
        self.pltTauG = plot_tau_g.PlotTauG(self)
        self.pltImpz = plot_impz.PlotImpz(self)
        self.plt3D = plot_3d.Plot3D(self)

        self._construct_UI()

#------------------------------------------------------------------------------
    def _construct_UI(self):
        """ Initialize UI with tabbed subplots """
        self.tabWidget = QTabWidget(self)
        self.tabWidget.setObjectName("plot_tabs")
        self.tabWidget.addTab(self.pltHf, '|H(f)|')
        self.tabWidget.addTab(self.pltPhi, 'phi(f)')
        self.tabWidget.addTab(self.pltPZ, 'P/Z')
        self.tabWidget.addTab(self.pltTauG, 'tau_g')
        self.tabWidget.addTab(self.pltImpz, 'h[n]')
        self.tabWidget.addTab(self.plt3D, '3D')

        layVMain = QVBoxLayout()
        layVMain.addWidget(self.tabWidget)
        layVMain.setContentsMargins(*params['wdg_margins'])#(left, top, right, bottom)

        self.setLayout(layVMain)
        
        #----------------------------------------------------------------------
        # SIGNALS & SLOTs
        #----------------------------------------------------------------------
        # local signals:
        
        self.timer_id = QtCore.QTimer()
        self.timer_id.setSingleShot(True)
        # redraw current widget at timeout (timer was triggered by resize event):
        self.timer_id.timeout.connect(self.current_tab_redraw)

        # When user has selected a different tab, trigger a redraw of current tab
        self.tabWidget.currentChanged.connect(self.current_tab_redraw)
        # The following does not work: maybe current scope must be left?
        # self.tabWidget.currentChanged.connect(self.tabWidget.currentWidget().redraw) # 

        self.tabWidget.installEventFilter(self)
        
        # global signals
        self.sig_rx.connect(self.process_signals)
        
        """
        https://stackoverflow.com/questions/29128936/qtabwidget-size-depending-on-current-tab

        The QTabWidget won't select the biggest widget's height as its own height
        unless you use layout on the QTabWidget. Therefore, if you want to change
        the size of QTabWidget manually, remove the layout and call QTabWidget::resize
        according to the currentChanged signal.

        You can set the size policy of the widget that is displayed to QSizePolicy::Preferred
        and the other ones to QSizePolicy::Ignored. After that call adjustSize to update the sizes.
        
        void MainWindow::updateSizes(int index)
        {
        for(int i=0;i<ui->tabWidget->count();i++)
            if(i!=index)
                ui->tabWidget->widget(i)->setSizePolicy(QSizePolicy::Ignored, QSizePolicy::Ignored);

        ui->tabWidget->widget(index)->setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Preferred);
        ui->tabWidget->widget(index)->resize(ui->tabWidget->widget(index)->minimumSizeHint());
        ui->tabWidget->widget(index)->adjustSize();
        resize(minimumSizeHint());
        adjustSize();
        }
        
        adjustSize(): The last two lines resize the main window itself. You might want to avoid it, 
        depending on your application. For example, if you set the rest of the widgets 
        to expand into the space just made available, it's not so nice if the window 
        resizes itself instead. 
        """

#------------------------------------------------------------------------------
    @pyqtSlot(object)
    def process_signals(self, sig_dict):
        """
        Process signals coming in
        """
        logger.debug("sig_rx = {0}".format(sig_dict))
#        if self.sender(): # origin of signal that triggered the slot
#            sender_name = self.sender().objectName()
#            sender_text = self.sender().text()
#            sender_class = self.sender().__class__.__name__
#            print("sender = ", sender_text, sender_class, sender_name, self.__class__.__name__)
#            logger.debug("process_signals called by {0}".format(sender_name))

        if 'specs_changed' in sig_dict:
               self.update_view()
            
        elif 'view_changed' in sig_dict.keys():
               self.update_view()
            
        elif 'filter_designed' in sig_dict:
               self.update_data()

        else:
            pass

#------------------------------------------------------------------------------
        
#    @QtCore.pyqtSlot(int)
#    def tab_changed(self,argTabIndex):
    def current_tab_redraw(self):
        self.tabWidget.currentWidget().redraw()
            
#------------------------------------------------------------------------------
    def eventFilter(self, source, event):
        """
        Filter all events generated by the QTabWidget. Source and type of all
         events generated by monitored objects are passed to this eventFilter,
        evaluated and passed on to the next hierarchy level.
        
        This filter stops and restarts a one-shot timer for every resize event.
        When the timer generates a timeout after 500 ms, current_tab_redraw is 
        called by the timer.
        """
        if isinstance(source, QTabWidget):
            if event.type() == QEvent.Resize:
                self.timer_id.stop()
                self.timer_id.start(500)

        # Call base class method to continue normal event processing:
        return super(PlotTabWidgets, self).eventFilter(source, event)

#------------------------------------------------------------------------------
    def update_data(self):
        """
        Calculate subplots with new filter DATA and redraw them
        """
        logger.debug("update_data (filter designed)")
        self.pltHf.draw()
        self.pltPhi.draw()
        self.pltPZ.draw()
        self.pltTauG.draw()
        self.pltImpz.draw()
        self.plt3D.draw()

#------------------------------------------------------------------------------
    def update_view(self):
        """
        Update plot limits with new filter SPECS and redraw all subplots
        """
        logger.debug("update_view (specs changed)")
        self.pltHf.update_view()
        self.pltPhi.update_view()
        self.pltTauG.update_view()
        self.pltImpz.update_view()
#        self.pltPZ.draw()
#        self.plt3D.draw()
        
#------------------------------------------------------------------------

def main():
    import sys
    from pyfda import pyfda_rc as rc
    from ..compat import QApplication
    
    app = QApplication(sys.argv)
    app.setStyleSheet(rc.css_rc)

    mainw = PlotTabWidgets(None)
    mainw.resize(300,400)
    
    app.setActiveWindow(mainw) 
    mainw.show()
    
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()
