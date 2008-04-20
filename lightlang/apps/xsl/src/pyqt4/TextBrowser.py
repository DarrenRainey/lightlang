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

from PyQt4 import Qt
import Config
import Const
import SLFind

#####
IconsDir = Config.Prefix+"/lib/xsl/icons/"

#####
class TranslateBrowser(Qt.QTextBrowser) :
	def __init__(self, parent = None) :
		Qt.QTextBrowser.__init__(self, parent)

		try : # FIXME: with PyQt-4.3
			self.setOpenLinks(False)
		except : pass

		#####

		self.clipboard = Qt.QApplication.clipboard()

		self.find_sound = SLFind.FindSound()

		#####

		self.connect(self, Qt.SIGNAL("anchorClicked(const QUrl &)"), self.findFromAnchor)


	### Private ###

	def findFromAnchor(self, url) :
		word = url.toString()
		if word.startsWith("#s") :
			word.remove(0, word.indexOf("_")+1)
			word = word.simplified()
			if word.isEmpty() :
				return
			self.find_sound.find(word)
		elif word.startsWith("http://", Qt.Qt.CaseInsensitive) :
			Qt.QDesktopServices.openUrl(url)

	###

	def uFind(self) :
		word = self.textCursor().selectedText().simplified()
		if not word.isEmpty() :
			self.uFindRequestSignal(word)

	def uFindInNewTab(self) :
		word = self.textCursor().selectedText().simplified()
		if not word.isEmpty() :
			self.newTabRequestSignal()
			self.uFindRequestSignal(word)

	def cFind(self) :
		word = self.textCursor().selectedText().simplified()
		if not word.isEmpty() :
			self.cFindRequestSignal(word)

	def cFindInNewTab(self) :
		word = self.textCursor().selectedText().simplified()
		if not word.isEmpty() :
			self.newTabRequestSignal()
			self.cFindRequestSignal(word)


	### Signals ###

	def newTabRequestSignal(self) :
		self.emit(Qt.SIGNAL("newTabRequest()"))

	def uFindRequestSignal(self, word) :
		self.emit(Qt.SIGNAL("uFindRequest(const QString &)"), word)

	def cFindRequestSignal(self, word) :
		self.emit(Qt.SIGNAL("cFindRequest(const QString &)"), word)


	### Handlers ###

	def mousePressEvent(self, event) :
		if event.button() == Qt.Qt.MidButton :
			word = self.textCursor().selectedText().simplified()
			if word.isEmpty() :
				word = self.clipboard.text(Qt.QClipboard.Selection).simplified()
			if not word.isEmpty() :
				self.newTabRequestSignal()
				self.uFindRequestSignal(word)
		else :
			Qt.QTextBrowser.mousePressEvent(self, event)

	def contextMenuEvent(self, event) :
		context_menu = self.createStandardContextMenu()
		text_cursor = self.textCursor()
		if not text_cursor.selectedText().simplified().isEmpty() :
			context_menu.addSeparator()
			context_menu.addAction(self.tr("Search"), self.uFind)
			context_menu.addAction(self.tr("Expanded search"), self.cFind)
			context_menu.addSeparator()
			context_menu.addAction(self.tr("Search (in new tab)"), self.uFindInNewTab)
			context_menu.addAction(self.tr("Expanded search (in new tab)"), self.cFindInNewTab)
		context_menu.exec_(event.globalPos())
		

#####
class TextBrowser(Qt.QWidget) :
	def __init__(self, parent = None) :
		Qt.QWidget.__init__(self, parent)

		self.main_layout = Qt.QVBoxLayout()
		self.main_layout.setMargin(0)
		self.main_layout.setSpacing(0)
		self.setLayout(self.main_layout)

		#####

		self.translate_browsers = []

		self.tab_widget = Qt.QTabWidget()
		self.main_layout.addWidget(self.tab_widget)

		self.add_tab_button = Qt.QToolButton()
		self.add_tab_button.setIcon(Qt.QIcon(IconsDir+"add_22.png"))
		self.add_tab_button.setIconSize(Qt.QSize(16, 16))
		self.add_tab_button.setCursor(Qt.Qt.ArrowCursor)
		self.add_tab_button.setAutoRaise(True)
		self.tab_widget.setCornerWidget(self.add_tab_button, Qt.Qt.TopLeftCorner)

		self.remove_tab_button = Qt.QToolButton()
		self.remove_tab_button.setIcon(Qt.QIcon(IconsDir+"remove_22.png"))
		self.remove_tab_button.setIconSize(Qt.QSize(16, 16))
		self.remove_tab_button.setCursor(Qt.Qt.ArrowCursor)
		self.remove_tab_button.setAutoRaise(True)
		self.tab_widget.setCornerWidget(self.remove_tab_button, Qt.Qt.TopRightCorner)

		#####

		self.connect(self.add_tab_button, Qt.SIGNAL("clicked()"), self.addTab)
		self.connect(self.remove_tab_button, Qt.SIGNAL("clicked()"), self.removeTab)

		self.connect(self.tab_widget, Qt.SIGNAL("currentChanged(int)"), self.tabChangedSignal)

		#####

		self.addTab()


	### Public ###

	def addTab(self) :
		self.translate_browsers.append(TranslateBrowser())
		index = len(self.translate_browsers) -1
		#
		self.connect(self.translate_browsers[index], Qt.SIGNAL("newTabRequest()"), self.addTab)
		self.connect(self.translate_browsers[index], Qt.SIGNAL("uFindRequest(const QString &)"),
			self.uFindRequestSignal)
		self.connect(self.translate_browsers[index], Qt.SIGNAL("cFindRequest(const QString &)"),
			self.cFindRequestSignal)
		#
		self.translate_browsers[index].setHtml(self.tr("<em>Empty</em>"))
		self.tab_widget.addTab(self.translate_browsers[index], self.tr("(Untitled)"))
		self.tab_widget.setCurrentIndex(index)
		self.tabChangedSignal()

	def removeTab(self, index = -1) :
		if self.tab_widget.count() == 1 :
			self.translate_browsers[0].setHtml(self.tr("<em>Empty</em>"))
			self.tab_widget.setTabText(0, self.tr("(Untitled)"))
		else :
			if index == -1 :
				index = self.tab_widget.currentIndex()
			self.tab_widget.removeTab(index)
			self.translate_browsers.pop(index)
		self.tabChangedSignal()

	###

	def count(self) :
		return self.tab_widget.count()

	def currentIndex(self) :
		return self.tab_widget.currentIndex()

	###

	def setText(self, index, text) :
		self.translate_browsers[index].setHtml(text)
		# TODO: add sound-link checks

	def setCaption(self, index, word) :
		self.tab_widget.setTabText(index, word)

	###

	def text(self, index = -1) :
		if index == -1 :
			index = self.tab_widget.currentIndex()
		return self.translate_browsers[index].toHtml()

	def caption(self, index = -1) :
		if index == -1 :
			index = self.tab_widget.currentIndex()
		return self.tab_widget.tabText(index)

	def browser(self, index = -1) :
		if index == -1 :
			index = self.tab_widget.currentIndex()
		return self.translate_browsers[index]

	def document(self, index = -1 ) :
		if index == -1 :
			index = self.tab_widget.currentIndex()
		return self.translate_browsers[index].document()

	###

	def clearPage(self, index = -1) :
		if index == -1 :
			index = self.tab_widget.currentIndex()
		self.translate_browsers[index].setHtml(self.tr("<em>Empty</em>"))
		self.tab_widget.setTabText(index, self.tr("(Untitled)"))

	def clearAll(self) :
		while self.count() != 1 :
			Qt.QCoreApplication.processEvents()
			self.removeTab(0)
		self.clearPage(0)

	def clear(self, index = -1) :
		if index == -1 :
			index = self.tab_widget.currentIndex()
		self.translate_browsers[index].clear()
		self.tab_widget.setTabText(index, Qt.QString())

	###

	def findNext(self, index, word) :
		return self.translate_browsers[index].find(word)

	def findPrevious(self, index, word) :
		return self.translate_browsers[index].find(word, Qt.QTextDocument.FindBackward)

	###

	def zoomIn(self, index = -1, range = 1) :
		if index == -1 :
			index = self.tab_widget.currentIndex()
		self.translate_browsers[index].zoomIn(range)

	def zoomOut(self, index = -1, range = 1) :
		if index == -1 :
			index = self.tab_widget.currentIndex()
		self.translate_browsers[index].zoomOut(range)


	### Signals ###

	def tabChangedSignal(self) :
		self.emit(Qt.SIGNAL("tabChanged(int)"), self.tab_widget.currentIndex())

	def uFindRequestSignal(self, word) :
		self.emit(Qt.SIGNAL("uFindRequest(const QString &)"), word)

	def cFindRequestSignal(self, word) :
		self.emit(Qt.SIGNAL("uFindRequest(const QString &)"), word)


	### Handlers ###

	def mouseDoubleClickEvent(self, event) :
		self.addTab()