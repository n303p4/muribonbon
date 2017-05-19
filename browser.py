#!/usr/bin/env python3

"""
muribonbon

A barebones Web browser in PyQt5.

Requirements:

* Python 3.6 or higher
* PyQt 5.8 or higher
* BeautifulSoup 4
* validators

This browser calls for system native icons, so it'll only look presentable on Linux.
"""

# Standard library.
import sys
import urllib.parse

# Third-party modules.
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets
from PyQt5.QtCore import Qt
from bs4 import BeautifulSoup # This is more Pythonic than using JavaScript, and sometimes safer.
import validators

# Constants
TEXT_MATCHES_NEXT = ["next page", "next", ">", ">>"]
TEXT_MATCHES_PREVIOUS = ["previous page", "prev", "<", "<<"]

class MainWindow(QtWidgets.QMainWindow):
    """This class represents a main window for the browser."""

    def __init__(self, *args, **kwargs):
    
        super().__init__(*args, **kwargs)
        self._setup()
    
    def _setup(self):
        """Initialize the browser layout."""
        
        # Create toolbar.
        self.toolbar = QtWidgets.QToolBar("Main Toolbar", self)
        self.toolbar.setMovable(False)
        self.toolbar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.addToolBar(self.toolbar)

        # Create navigation actions.
        self.previous_action = QtWidgets.QAction(self)
        self.previous_action.setIcon(QtGui.QIcon.fromTheme("media-skip-backward"))
        self.previous_action.setShortcut("Ctrl+Shift+Left")
        self.previous_action.triggered.connect(self.previous)
        self.toolbar.addAction(self.previous_action)

        self.back_action = QtWidgets.QAction(self)
        self.back_action.setIcon(QtGui.QIcon.fromTheme("go-previous"))
        self.back_action.setShortcut("Alt+Left")
        self.back_action.triggered.connect(self.back)
        self.toolbar.addAction(self.back_action)

        self.forward_action = QtWidgets.QAction(self)
        self.forward_action.setIcon(QtGui.QIcon.fromTheme("go-next"))
        self.forward_action.setShortcut("Alt+Right")
        self.forward_action.triggered.connect(self.forward)
        self.toolbar.addAction(self.forward_action)
        
        self.next_action = QtWidgets.QAction(self)
        self.next_action.setIcon(QtGui.QIcon.fromTheme("media-skip-forward"))
        self.next_action.setShortcut("Ctrl+Shift+Right")
        self.next_action.triggered.connect(self.next)
        self.toolbar.addAction(self.next_action)
        
        self.stop_action = QtWidgets.QAction(self)
        self.stop_action.setIcon(QtGui.QIcon.fromTheme("process-stop"))
        self.stop_action.setShortcut("Esc")
        self.stop_action.triggered.connect(self.stop)
        self.stop_action.triggered.connect(self._update_location_bar)
        self.toolbar.addAction(self.stop_action)
        
        self.reload_action = QtWidgets.QAction(self)
        self.reload_action.setIcon(QtGui.QIcon.fromTheme("view-refresh"))
        self.reload_action.setShortcuts(["Ctrl+R", "F5"])
        self.reload_action.triggered.connect(self.reload)
        self.toolbar.addAction(self.reload_action)

        # Create location bar.
        self.location_bar = QtWidgets.QLineEdit(self)
        self.location_bar.returnPressed.connect(self.load_url)
        self.toolbar.addWidget(self.location_bar)

        # Create action that highlights location bar.
        self.open_action = QtWidgets.QAction(self)
        self.open_action.setShortcuts(["Ctrl+L", "Alt+D"])
        self.open_action.triggered.connect(self.location_bar.setFocus)
        self.open_action.triggered.connect(self.location_bar.selectAll)
        self.addAction(self.open_action)

        # Create tab actions.
        self.new_tab_action = QtWidgets.QAction(self)
        self.new_tab_action.setIcon(QtGui.QIcon.fromTheme("tab-new"))
        self.new_tab_action.setShortcut("Ctrl+T")
        self.new_tab_action.triggered.connect(self.new_tab)
        self.toolbar.addAction(self.new_tab_action)

        self.close_tab_action = QtWidgets.QAction(self)
        self.close_tab_action.setShortcut("Ctrl+W")
        self.close_tab_action.triggered.connect(self.close_tab)
        self.addAction(self.close_tab_action)

        # Create tab widget.
        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self._update_tab_titles)
        self.tab_widget.currentChanged.connect(self._update_location_bar)
        self.setCentralWidget(self.tab_widget)

        # Start off by making a new tab.
        self.new_tab()

    # Internal stuff. Don't call these, please.
    
    def _update_location_bar(self):
        """Update the text in the location bar."""
        
        webview = self.tab_widget.currentWidget()
        if isinstance(webview, QtWebEngineWidgets.QWebEngineView):
            url = webview.url().toString()
            self.location_bar.setText(url)

    def _update_tab_titles(self):
        """Update all the tab titles."""
        
        # Iterate through all tabs.
        for index in range(0, self.tab_widget.count()):
            webview = self.tab_widget.widget(index)
            
            if not isinstance(webview, QtWebEngineWidgets.QWebEngineView):
                continue
            
            # Truncate to 24 characters. If the title is an empty string then it's Untitled.
            title = webview.title()[:24] if len(webview.title()) > 0 else "(Untitled)"
            self.tab_widget.setTabText(index, title)
            
            # Are we on the current tab? Then set the window title.
            if webview == self.tab_widget.currentWidget():
                self.setWindowTitle(webview.title())

    # Navigation actions.
    
    def load_url(self):
        """Load the URL listed in the location bar."""
        
        webview = self.tab_widget.currentWidget()
        if isinstance(webview, QtWebEngineWidgets.QWebEngineView):
            url = QtCore.QUrl.fromUserInput(self.location_bar.text())
            webview.load(url)

    def back(self): 
        """Go back in history by one."""
        
        webview = self.tab_widget.currentWidget()
        if isinstance(webview, QtWebEngineWidgets.QWebEngineView):
            webview.back()

    def forward(self):
        """Go forward in history by one."""
        
        webview = self.tab_widget.currentWidget()
        if isinstance(webview, QtWebEngineWidgets.QWebEngineView):
            webview.forward()

    def previous(self):
        """Attempt to go to the previous page."""
        
        webview = self.tab_widget.currentWidget()
        if isinstance(webview, QtWebEngineWidgets.QWebEngineView):
            webview.page().toHtml(lambda html: self.go_by(html, "prev", TEXT_MATCHES_PREVIOUS))

    def next(self):
        """Attempt to go to the next page."""
        
        webview = self.tab_widget.currentWidget()
        
        if isinstance(webview, QtWebEngineWidgets.QWebEngineView):
            webview.page().toHtml(lambda html: self.go_by(html, "next", TEXT_MATCHES_NEXT))

    def go_by(self, html:str, relationship:str, text_matches:list=[]):
        """
        From an HTML string, parse out a link based on class, rel, or id.
        
        * html - A string that contains HTML data to be parsed.
        * relationship - The relationship that the link has relative to the current page.
        * text_matches (optional) - A list of substrings to be checked against in link innerHTML.
        """
        
        webview = self.tab_widget.currentWidget()
        if not isinstance(webview, QtWebEngineWidgets.QWebEngineView):
            return
        
        # Create a BeautifulSoup object.
        soup = BeautifulSoup(html)
        anchors = soup.find_all("a", href=True)
        
        # The to-be-determined URL.
        url = None
        
        # Check attributes for the desired relationship.
        for anchor in anchors:
            for attribute in ("class", "rel", "id"):
                if anchor.has_attr(attribute) and relationship in anchor[attribute]:
                    url = anchor["href"]
                    break
            if url:
                break
        
        # As a fallback, check text strings within the link itself.
        if not url:
            for anchor in anchors:
                for substring in text_matches:
                    if substring in anchor.text.lower():
                        url = anchor["href"]
                        break
        
        # Everything has failed, exit function.
        if not url:
            return
        
        # If the URL doesn't seem to be valid, it's probably a relative URL, so use urllib.parse.
        if not validators.url(url):
            url = urllib.parse.urljoin(webview.url().toString(), url)
        
        # Load the URL.
        webview.load(QtCore.QUrl(url))

    def stop(self):
        """Stop the current page load."""
    
        webview = self.tab_widget.currentWidget()
        if isinstance(webview, QtWebEngineWidgets.QWebEngineView):
            webview.stop()

    def reload(self):
        """Reload the current page."""
    
        webview = self.tab_widget.currentWidget()
        if isinstance(webview, QtWebEngineWidgets.QWebEngineView):
            webview.reload()

    # Tab actions.

    def new_tab(self):
        """Create a browser tab."""
        
        webview = QtWebEngineWidgets.QWebEngineView(self)
        
        webview.titleChanged.connect(self._update_tab_titles)
        webview.urlChanged.connect(self._update_location_bar)
        
        self.tab_widget.addTab(webview, "New Tab")
        self.tab_widget.setCurrentIndex(self.tab_widget.count()-1)
    
    def close_tab(self, index=None):
        """Close a browser tab."""
        
        if type(index) is not int:
            index = self.tab_widget.currentIndex()
        
        webview = self.tab_widget.widget(index)
        
        if webview:
            self.tab_widget.removeTab(index)
            webview.deleteLater()

def main(argv):
    app = QtWidgets.QApplication(argv)
    
    app.setApplicationName("Muribonbon")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main(sys.argv)
