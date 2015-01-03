#!/usr/bin/env python
from __future__ import division, print_function

import signature
from qdataarg import QDataArg

from PyQt4 import QtCore, QtGui


class QCall(QtGui.QGroupBox):
    def __init__(self, app, callid):
        QtGui.QGroupBox.__init__(self)
        self.app = app
        self.callid = callid
        self.sig = None

        self.UI_init()
        self.movers_setvisibility()

    def UI_init(self):
        sampler = self.app.samplers[self.app.sampler]
        routines = [r for r in self.app.signatures.keys()
                    if r in sampler["kernels"]]


        layout = QtGui.QGridLayout()
        self.setLayout(layout)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)

        # buttons
        buttonsL = QtGui.QHBoxLayout()
        layout.addLayout(buttonsL, 0, 0)

        # buttons > remove
        self.Qt_removeS = QtGui.QStackedWidget()
        buttonsL.addWidget(self.Qt_removeS)
        remove = QtGui.QToolButton()
        self.Qt_removeS.addWidget(remove)
        icon = self.style().standardIcon(QtGui.QStyle.SP_DialogDiscardButton)
        remove.setIcon(icon)
        remove.clicked.connect(self.remove_click)
        self.Qt_removeS.addWidget(QtGui.QWidget())

        # buttons > down
        self.Qt_movedownS = QtGui.QStackedWidget()
        buttonsL.addWidget(self.Qt_movedownS)
        movedown = QtGui.QToolButton()
        movedown.setArrowType(QtCore.Qt.DownArrow)
        self.Qt_movedownS.addWidget(movedown)
        movedown.clicked.connect(self.movedown_click)
        self.Qt_movedownS.addWidget(QtGui.QWidget())

        # buttons > up
        self.Qt_moveupS = QtGui.QStackedWidget()
        buttonsL.addWidget(self.Qt_moveupS)
        moveup = QtGui.QToolButton()
        moveup.setArrowType(QtCore.Qt.UpArrow)
        self.Qt_moveupS.addWidget(moveup)
        moveup.clicked.connect(self.moveup_click)
        self.Qt_moveupS.addWidget(QtGui.QWidget())

        # buttons
        buttonsL.addStretch(1)

        # routine
        routine = QtGui.QLineEdit()
        layout.addWidget(routine, 1, 0)
        routine.callid = self.callid
        routine.argid = 0
        routine.setProperty("valid", False)
        routine.textChanged.connect(self.arg_change)
        completer = QtGui.QCompleter(routines, routine)
        routine.setCompleter(completer)

        # spaces
        layout.setColumnStretch(100, 1)

        # attributes
        self.Qt_args = [routine]
        self.Qt_arglabels = [None]
        self.sig = None

    def movers_setvisibility(self):
        ncalls = len(self.app.calls)
        if ncalls > 1:
            self.Qt_removeS.setCurrentIndex(0)
            if self.callid > 0:
                self.Qt_moveupS.setCurrentIndex(0)
            else:
                self.Qt_moveupS.setCurrentIndex(1)
            if self.callid < ncalls - 1:
                self.Qt_movedownS.setCurrentIndex(0)
            else:
                self.Qt_movedownS.setCurrentIndex(1)
        else:
            self.Qt_removeS.setCurrentIndex(1)
            self.Qt_moveupS.setCurrentIndex(1)
            self.Qt_movedownS.setCurrentIndex(1)

    def args_init(self):
        call = self.app.calls[self.callid]
        assert isinstance(call, signature.Call)
        assert len(self.Qt_args) == 1
        for argid, arg in enumerate(call.sig):
            if isinstance(arg, signature.Name):
                continue  # routine name
            Qarglabel = QtGui.QLabel(arg.name)
            self.layout().addWidget(Qarglabel, 0, argid)
            self.Qt_arglabels.append(Qarglabel)
            Qarglabel.setAlignment(QtCore.Qt.AlignCenter)
            if isinstance(arg, signature.Flag):
                Qarg = QtGui.QComboBox()
                Qarg.addItems(arg.flags)
                Qarg.currentIndexChanged.connect(self.arg_change)
            elif isinstance(arg, (signature.Dim, signature.Scalar,
                                  signature.Ld, signature.Inc)):
                Qarg = QtGui.QLineEdit()
                Qarg.textChanged.connect(self.arg_change)
            elif isinstance(arg, signature.Data):
                Qarg = QDataArg(self)
            Qarg.argid = argid
            Qarg.setProperty("invalid", True)
            self.layout().addWidget(Qarg, 1, argid)
            self.Qt_args.append(Qarg)
        self.sig = call.sig
        self.useld_apply()
        self.usevary_apply()

    def args_clear(self):
        for Qarg in self.Qt_args[1:]:
            Qarg.deleteLater()
        self.Qt_args = self.Qt_args[:1]
        for Qarglabel in self.Qt_arglabels[1:]:
            Qarglabel.deleteLater()
        self.Qt_arglabels = self.Qt_arglabels[:1]
        self.sig = None

    def useld_apply(self):
        if not self.sig:
            return
        useld = self.app.useld
        for argid, arg in enumerate(self.sig):
            if isinstance(arg, (signature.Ld, signature.Inc)):
                self.Qt_arglabels[argid].setVisible(useld)
                self.Qt_args[argid].setVisible(useld)

    def usevary_apply(self):
        for Qarg in self.Qt_args:
            if isinstance(Qarg, QDataArg):
                Qarg.usevary_apply()

    def args_set(self, fromargid=None):
        call = self.app.calls[self.callid]
        # set widgets
        if not isinstance(call, signature.Call):
            self.args_clear()
            return
        if call.sig != self.sig:
            self.args_clear()
            self.args_init()
        # set values
        for Qarg, arg, val in zip(self.Qt_args, call.sig, call):
            Qarg.setProperty("invalid", val is None)
            Qarg.style().unpolish(Qarg)
            Qarg.style().polish(Qarg)
            Qarg.update()
            if Qarg.argid == fromargid:
                continue
            val = "" if val is None else str(val)
            if isinstance(arg, (signature.Name, signature.Dim,
                                signature.Scalar, signature.Ld,
                                signature.Inc)):
                Qarg.setText(val)
            elif isinstance(arg, signature.Flag):
                Qarg.setCurrentIndex(Qarg.findText(val))
            elif isinstance(arg, signature.Data):
                Qarg.set()

    def data_viz(self):
        if not self.sig:
            return
        for argid in self.app.calls[self.callid].sig.dataargs():
            self.Qt_args[argid].viz()

    # event handlers
    def remove_click(self):
        self.app.UI_call_remove(self.callid)

    def moveup_click(self):
        self.app.UI_call_moveup(self.callid)

    def movedown_click(self):
        self.app.UI_call_movedown(self.callid)

    def arg_change(self):
        sender = self.app.sender()
        if isinstance(sender, QtGui.QLineEdit):
            # adjust widt no matter where the change came from
            val = str(sender.text())
            if sender.argid != 0:
                size = sender.minimumSizeHint()
                width = sender.fontMetrics().width(val)
                width += sender.minimumSizeHint().width()
                height = sender.sizeHint().height()
                sender.setFixedSize(max(height, width), height)
        if self.app.setting:
            return
        if isinstance(sender, QtGui.QComboBox):
            val = str(sender.currentText())
        if not val:
            val = None
        self.app.UI_arg_change(self.callid, sender.argid, val)