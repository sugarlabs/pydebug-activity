#!/usr/bin/env python
# Copyright (C) 2008, One Laptop Per Child
#
# This program is jobjectree software; you can redistribute it and/or modify
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

import os
import time
from gettext import gettext as _
from project_glade import toplevel

#major packages
from gi.repository import Gtk
from gi.repository import GdkPixbuf

# Initialize logging.
import logging
from sugar3 import profile
from sugar3 import util
from sugar3 import logger
from sugar3.datastore import datastore

#Get the standard logging directory.
std_log_dir = logger.get_logs_dir()
_logger = logging.getLogger('PyDebug')


class DataStoreTree():

    column_names = [_('Name'), _('Size'), _('Last Changed')]
    
    def __init__(self, parent, widget=None,wTree=None):
        self.parent = parent
        self._activity = parent
        self.treeview = widget
        self.wTree = wTree

        self.init_model()
        self.init_columns()
        self.connect_object()
        self.limit=10
        self.journal_page_size =10
        self.journal_page_num = 0
        self.journal_max = 0
        self.new_directory()

        button = self.wTree.get_widget('from_journal')
        button.set_tooltip_text(_('Load the selected Journal XO (or tar.gz) file to the debug workplace'))

        button = self.wTree.get_widget('to_journal')
        button.set_tooltip_text(_('Zip up all the files in your debug workplace and store them in the Journal'))

    def connect_object(self,  wTree=None):
        mdict = {
            'younger_clicked_cb': self.newer_in_journal_cb,
            'older_clicked_cb': self.older_in_journal_cb,
            'from_journal_clicked_cb': self.load_from_journal_cb,
            'to_journal_clicked_cb': self.save_to_journal_cb,
        }

        self.wTree.signal_autoconnect(mdict)

    def init_model(self):
        #plan for the store: pixbuf, title, size, last-updated, tooltip, jobject-id
        self.journal_model = Gtk.TreeStore(GdkPixbuf.Pixbuf, str, str, str, str, str, str, str, str, str, str)

        if not self.treeview:
            self.treeview = Gtk.TreeView()

        self.treeview.set_model(self.journal_model)
        self.treeview.show()
        #self.treeview.has_tooltip = True
        #self.treeview.set_tooltip_column(10)
        #self.treeview.connect('query-tooltip',self.display_tooltip)
        self.show_hidden = False

    def init_columns(self):
        col = Gtk.TreeViewColumn()
        col.set_title(self.column_names[0])

        render_pixbuf = Gtk.CellRendererPixbuf()
        col.pack_start(render_pixbuf, expand=False)
        col.add_attribute(render_pixbuf, 'pixbuf', 0)

        render_text = Gtk.CellRendererText()
        col.pack_start(render_text, expand=True)
        col.add_attribute(render_text, 'text', 1)
        col.set_fixed_width(20)
        self.treeview.append_column(col)

        cell = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn(self.column_names[1], cell)
        col.add_attribute(cell, 'text', 2)
        self.treeview.append_column(col)

        cell = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn(self.column_names[2], cell)
        col.add_attribute(cell, 'text', 3)
        self.treeview.append_column(col)

    def get_datastore_list(self, next=False):
        dslist = []
        """
        if not next:
            self.journal_page_num -= 1
        else:
            self.journal_page_num += 1
        if self.journal_page_num < 0: self.journal_page_num = 0
        if self.journal_max != 0:
            if self.journal_page_num * self.journal_page_size >= self.journal_max:
                self.journal_page_num -= 1
        #_logger.debug('fetch datastore data. limit:%s. offset: %s'%(self.limit,self.journal_page_num * self.journal_page_size))
        #(results,count)=datastore.find({'limit':self.limit,'offset':self.journal_page_num * self.journal_page_size})
        """
        self.journal_model.clear()
        ds_list = []
        num_found = 0
        mime_list = [self._activity.MIME_TYPE,'application/zip']
        
        #build 650 doesn't seem to understand correctly the dictionary with a list right hand side
        info = self._activity.util.sugar_version()
        if len(info)>0:
            (major,minor,micro,release) = info
            _logger.debug('sugar version major:%s minor:%s micro:%s release:%s'%info)
        else:
            _logger.debug('sugar version failure')
            minor = 70

        try:
            if minor > 80:
                (ds_list,num_found) = datastore.find({'mime_type': mime_list})
            else:
                (results,count) = datastore.find({'mime_type': self._activity.MIME_TYPE})
                ds_list.extend(results)
                num_found += count            
                (results,count) = datastore.find({'mime_type': 'application/zip'})
                ds_list.extend(results)
        except Exception,e:
            _logger.error('datastore error %s'%e)
            return []

        if num_found < self.limit:
            self.journal_max = self.journal_page_num * self.journal_page_size + num_found

        _logger.debug( 'datastoretree-get_datastore_list: count= %s'%num_found)
        keys = ('title','size','timestamp','activity','package','mime_type','file_path')

        for jobject in ds_list:
            itemlist = [None,]
            datastoredict=jobject.get_metadata().get_dictionary() #get the property dictionary
            src = jobject.get_file_path() #returns the full path of the file
            datastoredict['object_id'] = jobject.object_id
            
            if False: #if  src null, there is no file related to this meta data
                jobject.destroy()
                continue	#go get the next iterations
            #add in the info that we intend to use
            if src:
                info = os.stat(src) #get the directory information about this file
                datastoredict['size'] = info.st_size
            else:
                 datastoredict['size'] = 0               

            datastoredict['file_path'] = src

            for key in keys:
                if datastoredict.has_key(key):
                    if key == 'timestamp':
                        pkg = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(float(datastoredict[key])))
                    elif key == 'title':
                        pkg = datastoredict[key][:18]
                    else:
                        pkg = '%s'%(datastoredict[key])
                else:
                    pkg = ''

                itemlist.append(pkg)

            itemlist.append(datastoredict['title'])
            itemlist.append(jobject.object_id)
            text = 'Mime_type: %s, Journal ID: %s, Bundle: %s'%(datastoredict.get('mime_type',''),
                                                                  datastoredict.get('object_id',''),
                                                                  datastoredict.get('package',''))
            itemlist.append(text)
            #_logger.debug('journal tooltip:%s'%text)
            dslist.append(itemlist)
            jobject.destroy()

        return dslist

    def new_directory(self,piter = None, next=True):
        journal_list = self.get_datastore_list(next)
        for journal_selected_data in journal_list:
            appended_iter = self.journal_model.append(piter, journal_selected_data )
            model=self.journal_model
            appended_path = model.get_path(appended_iter)
       
    def file_pixbuf(self, filename):
        folderpb = self.get_icon_pixbuf('STOCK_DIRECTORY')
        filepb = self.get_icon_pixbuf('STOCK_FILE')
        if os.path.isdir(filename):
            pb = folderpb
        else:
            pb = filepb

        return pb

    def get_icon_pixbuf(self, stock):
        return self.treeview.render_icon(stock_id=getattr(Gtk, stock),
                                size=Gtk.ICON_SIZE_MENU,
                                detail=None)

    def get_treeview(self):
        return self.treeview

    def newer_in_journal_cb(self,button):
        _logger.debug('younger call back')
        self.get_datastore_list(next=False)
        
    def older_in_journal_cb(self,button):
        _logger.debug('older call back')
        self.get_datastore_list(next=True)
        
    def save_to_journal_cb(self,button):
        self.parent.proj_funct.write_binary_to_datastore()
        
    def load_from_journal_cb(self,button):
        selection=self.treeview.get_selection()
        (model,iter)=selection.get_selected()
        if iter == None:
            self.parent.alert(_('Must select Journal item to Load'))
            return

        object_id = model.get(iter,9)
        _logger.debug('object id %s from journal'%object_id)
        self.parent.proj_funct.try_to_load_from_journal(object_id)
        
    def datastore_row_activated_cb(self):
        self.load_from_journal_cb()
    
    def display_tooltip(self, widget,x,y,mode,tooltip):
        _logger.debug('in display_tooltip')
        tooltip.show()
        return True


def main():
    Gtk.main()


if __name__ == "__main__":
    top = toplevel()
    top.show()

    main()

