# -*- coding: utf8 -*-
#
# XSL - graphical interface for SL
# Copyright (C) 2007-2016 Devaev Maxim
#
# This file is part of XSL.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import Qt
import Config
import Const
import Settings
import UserStyleCss
import IconsLoader
import PopupWindow
import TextSearchFrame
import TranslateBrowser


#####
def tr(str) :
	return Qt.QApplication.translate("@default", str)


#####
class TranslateWindow(PopupWindow.PopupWindow) :
	def __init__(self, parent = None) :
		PopupWindow.PopupWindow.__init__(self, parent)

		self.setObjectName("translate_window")

		#####

		self.main_layout = Qt.QVBoxLayout()
		self.main_layout.setContentsMargins(0, 0, 0, 0)
		self.main_layout.setSpacing(0)
		self.setLayout(self.main_layout)

		self.caption_frame = Qt.QFrame()
		self.caption_frame.setMouseTracking(True)
		self.caption_frame.setFrameShape(Qt.QFrame.Box)
		self.caption_frame.setFrameShadow(Qt.QFrame.Raised)
		if self.font().pixelSize() > 0 :
			self.caption_frame.setMaximumHeight((self.font().pixelSize()) * 4)
		elif self.font().pointSize() > 0 :
			self.caption_frame.setMaximumHeight((self.font().pointSize()) * 4)
		else :
			self.caption_frame.setMaximumHeight(40)
		self.main_layout.addWidget(self.caption_frame)

		self.caption_frame_layout = Qt.QHBoxLayout()
		self.caption_frame_layout.setContentsMargins(20, 1, 2, 1)
		self.caption_frame_layout.setSpacing(1)
		self.caption_frame.setLayout(self.caption_frame_layout)

		#####

		self.caption_label = Qt.QLabel()
		self.caption_label.setTextFormat(Qt.Qt.RichText)
		self.caption_label.setWordWrap(True)
		self.caption_frame_layout.addWidget(self.caption_label)

		self.close_button = Qt.QToolButton()
		self.close_button.setIcon(IconsLoader.icon("dialog-cancel"))
		self.close_button.setIconSize(Qt.QSize(16, 16))
		self.close_button.setFixedSize(Qt.QSize(16, 16))
		self.close_button.setCursor(Qt.Qt.ArrowCursor)
		self.close_button.setAutoRaise(True)
		self.caption_frame_layout.addWidget(self.close_button)

		self.translate_browser = TranslateBrowser.TranslateBrowser()
		self.main_layout.addWidget(self.translate_browser)

		self.text_search_frame = TextSearchFrame.TextSearchFrame()
		self.text_search_frame.hide()
		self.main_layout.addWidget(self.text_search_frame)

		#####

		self.connect(self.close_button, Qt.SIGNAL("clicked()"), self.close)

		self.connect(self.translate_browser, Qt.SIGNAL("showTextSearchFrameRequest()"), self.text_search_frame.show)
		self.connect(self.translate_browser, Qt.SIGNAL("hideTextSearchFrameRequest()"), self.text_search_frame.hide)
		self.connect(self.translate_browser, Qt.SIGNAL("setFoundRequest(bool)"), self.text_search_frame.setFound)
		self.connect(self.translate_browser, Qt.SIGNAL("newTabRequest()"), self.newTabRequestSignal)
		self.connect(self.translate_browser, Qt.SIGNAL("uFindRequest(const QString &)"), self.uFindRequestSignal)
		self.connect(self.translate_browser, Qt.SIGNAL("cFindRequest(const QString &)"), self.cFindRequestSignal)

		self.connect(self.text_search_frame, Qt.SIGNAL("findNextRequest(const QString &)"), self.translate_browser.findNext)
		self.connect(self.text_search_frame, Qt.SIGNAL("findPreviousRequest(const QString &)"), self.translate_browser.findPrevious)
		self.connect(self.text_search_frame, Qt.SIGNAL("instantSearchRequest(const QString &)"), self.translate_browser.instantSearch)

		self.connect(self.close_button, Qt.SIGNAL("clicked()"), self.close)


	### Public ###

	def setCaption(self, str) :
		self.caption_label.setText(Qt.QString("<html><head><style>%1</style></head>"
			"<body><font class=\"text_label_font\">%2</font></body></html>").arg(UserStyleCss.userStyleCss()).arg(str))

	def setText(self, text) :
		self.translate_browser.setText(text)

	def clear(self) :
		self.translate_browser.clear()

	###

	def saveSettings(self) :
		settings = Settings.settings()
		settings.setValue("translate_window/size", Qt.QVariant(self.size()))

	def loadSettings(self) :
		settings = Settings.settings()
		self.resize(settings.value("translate_window/size", Qt.QVariant(Qt.QSize(550, 400))).toSize())

	###

	def setFocus(self, reason = Qt.Qt.OtherFocusReason) :
		self.translate_browser.setFocus(reason)

	def show(self) :
		self.text_search_frame.hide()
		PopupWindow.PopupWindow.show(self)


	### Private ###
	### Signals ###

	def newTabRequestSignal(self) :
		self.emit(Qt.SIGNAL("newTabRequest()"))

	def uFindRequestSignal(self, word) :
		self.emit(Qt.SIGNAL("uFindRequest(const QString &)"), word)

	def cFindRequestSignal(self, word) :
		self.emit(Qt.SIGNAL("cFindRequest(const QString &)"), word)

