#!/usr/bin/env python
# Copyright (C) 2009, George Hunt <georgejhunt@gmail.com>
# Copyright (C) 2009, One Laptop Per Child
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

#major packages
import os
from gettext import gettext as _

from gi.repository import Gtk
from gi.repository import Gdk

#sugar stuff
from sugar3.graphics.toolbutton import ToolButton

#application stuff
from editor import GtkSourceviewEditor
from page import SearchOptions
from page import S_WHERE

#import logging
from pydebug_logging import _logger


class EditorGui(GtkSourceviewEditor):

    def __init__(self, activity):
        self._activity = activity

        GtkSourceviewEditor.__init__(self, activity)

        #set the default contents for edit,override fixed font size
        self.font_size = activity.debug_dict.get('font_size', 8)
        self.find_window = None

        self.editbar = Gtk.Toolbar()
        self.last_folder = None
        editopen = ToolButton(stock_id=Gtk.STOCK_NEW)
        editopen.set_tooltip(_('New File'))
        editopen.connect('clicked', self._new_file_cb)
        editopen.add_accelerator('clicked', activity.accelerator, ord('N'), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        #editopen.props.accelerator = '<Ctrl>O'
        editopen.show()
        self.editbar.insert(editopen, -1)

        editfile = ToolButton(stock_id=Gtk.STOCK_OPEN)
        editfile.set_tooltip(_('Open File'))
        editfile.connect('clicked', self._read_file_cb)
        editfile.add_accelerator('clicked', activity.accelerator, ord('O'), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        #editfile.props.accelerator = '<Ctrl>O'
        editfile.show()
        self.editbar.insert(editfile, -1)

        editsave = ToolButton(stock_id=Gtk.STOCK_SAVE)
        editsave.set_tooltip(_('Save File'))
        editsave.add_accelerator('clicked', activity.accelerator, ord('S'), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        #editsave.props.accelerator = '<Ctrl>S'
        editsave.connect('clicked', self.save_cb)
        editsave.show()
        self.editbar.insert(editsave, -1)
        
        editsaveas = ToolButton(stock_id=Gtk.STOCK_SAVE_AS)
        editsaveas.set_tooltip(_('Save As'))
        #editsaveas.props.accelerator = '<Ctrl>S'
        editsaveas.connect('clicked', self.save_file_cb)
        editsaveas.show()
        self.editbar.insert(editsaveas, -1)

        separator = Gtk.SeparatorToolItem()
        separator.set_draw(True)
        separator.show()
        self.editbar.insert(separator, -1)
        
        editundo = ToolButton('undo')
        editundo.set_tooltip(_('Undo'))
        editundo.connect('clicked', self.undo)
        editundo.add_accelerator('clicked',activity.accelerator,ord('Z'), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        #editundo.props.accelerator = '<Ctrl>Z'
        editundo.show()
        self.editbar.insert(editundo, -1)

        editredo = ToolButton('redo')
        editredo.set_tooltip(_('Redo'))
        editredo.connect('clicked', self.redo)
        editredo.add_accelerator('clicked',activity.accelerator,ord('Y'), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        #editredo.props.accelerator = '<Ctrl>Y'
        editredo.show()
        self.editbar.insert(editredo, -1)

        separator = Gtk.SeparatorToolItem()
        separator.set_draw(True)
        separator.show()
        self.editbar.insert(separator, -1)
        
        editcut = ToolButton(stock_id=Gtk.STOCK_CUT)
        editcut.set_tooltip(_('Cut'))
        self.edit_cut_handler_id = editcut.connect('clicked', self.cut)
        editcut.add_accelerator('clicked',activity.accelerator,ord('X'), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        #editcut.props.accelerator = '<Ctrl>X'
        self.editbar.insert(editcut, -1)
        editcut.show()

        editcopy = ToolButton(stock_id=Gtk.STOCK_COPY)
        editcopy.set_tooltip(_('Copy'))
        self.edit_copy_handler_id = editcopy.connect('clicked', self.copy_to_clipboard_cb)
        editcopy.add_accelerator('clicked',activity.accelerator,ord('C'), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        #editcopy.props.accelerator = '<Ctrl>C'
        self.editbar.insert(editcopy, -1)
        editcopy.show()

        editpaste = ToolButton(stock_id=Gtk.STOCK_PASTE)
        editpaste.set_tooltip(_('Paste'))
        self.edit_paste_handler_id = editpaste.connect('clicked', self.paste)
        editpaste.add_accelerator('clicked',activity.accelerator,ord('V'), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        #editpaste.props.accelerator = '<Ctrl>V'
        editpaste.show()
        self.editbar.insert(editpaste, -1)

        editfind = ToolButton('viewmag1')
        editfind.set_tooltip(_('Find and Replace'))
        editfind.connect('clicked', self.show_find)
        editfind.add_accelerator('clicked',activity.accelerator,ord('F'), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        #editfind.props.accelerator = '<Ctrl>F'
        editfind.show()
        self.editbar.insert(editfind, -1)

        self.zoomout = ToolButton(stock_id=Gtk.STOCK_ZOOM_OUT)
        self.zoomout.set_tooltip(_('Zoom out'))
        self.zoomout.connect('clicked', self.__zoomout_clicked_cb)
        self.editbar.insert(self.zoomout, -1)
        self.zoomout.show()

        self.zoomin = ToolButton(stock_id=Gtk.STOCK_ZOOM_IN)
        self.zoomin.set_tooltip(_('Zoom in'))
        self.zoomin.connect('clicked', self.__zoomin_clicked_cb)
        self.editbar.insert(self.zoomin, -1)
        self.zoomin.show()

        stop_button = ToolButton('activity-stop')
        stop_button.set_tooltip(_('Stop'))
        stop_button.props.accelerator = '<Ctrl>Q'
        stop_button.connect('clicked', self.__stop_clicked_cb)
        self.editbar.insert(stop_button, -1)
        stop_button.show()

        self.editbar.show_all()
        
    def __stop_clicked_cb(self, button):
        self._activity.py_stop()

    def get_editbar(self):
        """return reference for placing on the Sugar main menu notebook"""
        return self.editbar

    def _new_file_cb(self, widget):
        """create a new empty file, add a sequence number if default exists"""
        full_path = self._activity.util.non_conflicting(self._activity.child_path,'Unsaved_Document.py')
        self.load_object(full_path,os.path.basename(full_path))
        
    def _read_file_cb(self,widget):
        """open up a file selector"""
        _logger.debug('Reading a file into editor')
        dialog = Gtk.FileChooserDialog("Open..",
                                       None,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        dialog.set_default_response(Gtk.ResponseType.OK)

        if self.last_folder == None:
            self.last_folder = self._activity.child_path

        if not self.last_folder:
            self.last_folder = self.activity_playpen                 

        if self.last_folder:
            dialog.set_current_folder(self.last_folder)      
        
        filter = Gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)
        
        filter = Gtk.FileFilter()
        filter.set_name("Python")
        filter.add_pattern("*.py")
        dialog.add_filter(filter)
        
        filter = Gtk.FileFilter()
        filter.set_name("Activity")
        filter.add_pattern("*.xo")
        dialog.add_filter(filter)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            _logger.debug(dialog.get_filename(), 'selected')
            fname = dialog.get_filename()
            self.last_folder = os.path.dirname(fname)
            self.load_object(fname,os.path.basename(fname))
            line = self.get_remembered_line_number(fname)
            if line:
                self.position_to(fname,line)

        elif response == Gtk.ResponseType.CANCEL:
            _logger.debug('File chooseer closed, no files selected')

        dialog.destroy()

    def save_file_cb(self, button):
        """
        impliments the SaveAs function
        """
        chooser = Gtk.FileChooserDialog(title=None, action=Gtk.FileChooserAction.SAVE,
                                        buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                 Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

        file_path = self.get_full_path()
        _logger.debug('Saving file %s'%(file_path))
        chooser.set_filename(file_path)
        response = chooser.run()
        new_fn = chooser.get_filename()
        chooser.destroy()

        if response == Gtk.ResponseType.CANCEL:
            return

        if response == Gtk.ResponseType.OK:
            self.save_cb(None, new_fn)
            
    def save_cb(self,button,new_fn=None):
        if new_fn:
            full_path = new_fn

        else:
            full_path = self.get_full_path()

        if os.path.basename(full_path).startswith('Unsaved_Document'):  # force a choice to keep or change the name
            #fd = open(full_path,'w')
            #fd.close()
            self.save_file_cb(None)            
            return

        page = self._get_page()

        if new_fn:
            page.fullPath = new_fn
            page.save(skip_md5 = True, new_file=new_fn)
        else:
            page.save()

        self.clear_changed_star()
        page.save_hash()
 
    def __zoomin_clicked_cb(self, button):
        self.font_size += 1
        self.change_font_size(self.font_size)
        self._activity.debug_dict['font_size'] = self.font_size
            
    def __zoomout_clicked_cb(self, botton):
        self.font_size -= 1
        self.change_font_size(self.font_size)
        self._activity.debug_dict['font_size'] = self.font_size
       
    ###   following routines are copied from develop_app for use with editor 
    def _replace_cb(self, button=None):
        ftext = self._search_entry.props.text
        rtext = self._replace_entry.props.text
        _logger.debug('replace %s with %s usiing options %r'%(ftext,rtext,self.s_opts))
        replaced, found = self.replace(ftext, rtext, self.s_opts)
        if found:
            self._replace_button.set_sensitive(True)

    def _search_entry_activated_cb(self, entry):
        text = self._search_entry.props.text
        if text:
            self._findnext_cb(None)       

    def _search_entry_changed_cb(self, entry):
        self.safe_to_replace = False
        text = self._search_entry.props.text
        if not text:
            self._findprev.set_sensitive(False)
            self._findnext.set_sensitive(False)

        else:
            self._findprev.set_sensitive(True)
            self._findnext.set_sensitive(True)
            if not self.s_opts.use_regex: #do not do partial searches for regex
                _logger.debug('finding:%s'%(text,))
                if self.find_next(text, 
                            SearchOptions(self.s_opts, 
                            stay=True, 
                            where = self.s_opts.where if self.s_opts.where != S_WHERE.multifile else S_WHERE.file)):
                    #no multifile, or focus gets grabbed
                    self._replace_button.set_sensitive(True)
                    
    def _replace_entry_changed_cb(self, entry):
        if self._replace_entry.props.text:
            self.safe_to_replace = True
            
    def _findprev_cb(self, button=None):
        ftext = self._search_entry.props.text
        if ftext:
            if self.find_next(ftext, SearchOptions(self.s_opts, forward=False)):
                self._replace_button.set_sensitive(True)
                        
    def _findnext_cb(self, button=None):
        ftext = self._search_entry.props.text
        _logger.debug('find next %s'%ftext)
        if ftext:
            if self.find_next(ftext, self.s_opts):
                self._replace_button.set_sensitive(True)

            self.set_focus()

    def show_find(self,button):
        """find_window is defined in project.glade"""
        if not self.find_window:
            self._find_width = 400
            self._find_height = 300
            self.find_window = self.wTree.get_widget("find")
            self.find_window.connect('destroy',self.close_find_window)
            self.find_window.connect('delete_event',self.close_find_window)
            self.find_connect()
            self.find_window.set_title(_('FIND OR REPLACE'))
            self.find_window.set_size_request(self._find_width,self._find_height)
            self.find_window.set_decorated(False)
            self.find_window.set_resizable(False)
            self.find_window.set_modal(False)
            self.find_window.connect('size_request',self._size_request_cb)
            self.find_window.set_transient_for(self._activity.window.get_toplevel())

        #if there is any selected text, put it in the find entry field, and grab focus
        selected = self.get_selected()
        _logger.debug('selected text is %s'%selected)
        self._search_entry.props.text = selected
        self._search_entry.grab_focus()
        self.find_window.show()
        
    def _size_request_cb(self, widget, req):
        x = Gdk.Screen.width() - self._find_width - 50
        self.find_window._width = req.width
        self.find_window._height = req.height
        self.find_window.move(x, 150)
        
    def find_connect(self):
        mdict = {
            'find_close_clicked_cb': self.close_find_window,
            #'find_entry_changed_cb': self.find_entry_changed_cb,
            #'replace_entry_changed_cb': self.replace_entry_changed_cb,
            'find_previous_clicked_cb': self._findprev_cb,
            'find_next_clicked_cb': self._findnext_cb,
            'find_entry_changed_cb': self._search_entry_changed_cb,
            'replace_entry_changed_cb': self._replace_entry_changed_cb,
            'replace_clicked_cb': self._replace_cb,
            #'replace_all_clicked_cb': self._findprev_cb,
        }

        self.wTree.signal_autoconnect(mdict)
        self._findnext = self.wTree.get_widget("find_next")
        self._findprev = self.wTree.get_widget("find_previous")
        self._search_entry = self.wTree.get_widget("find_entry")
        self._replace_entry = self.wTree.get_widget("replace_entry")
        self._replace_button = self.wTree.get_widget("replace")
        #self.replace_all = self.wTree.get_widget("replace_all")
        self.find_where = self.wTree.get_widget("find_where")

        
    def close_find_window(self,button):
        self.find_window.hide()
        return True

