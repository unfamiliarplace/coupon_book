# Python 2.7.10
# Copyright August 2015 by Luke Sawczak

#-------------------------------------------
# Imports
#-------------------------------------------

import wx, os, sys
from wx.lib import filebrowsebutton
import ctypes.wintypes
from dateutil.parser import parse
from time import strftime
from cb import *
from messages import *


#-------------------------------------------
# Constants
#-------------------------------------------

# stackoverflow.com/questions/6227590/finding-the-users-my-documents-path
buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 1, buf)
DOC_FOLDER = buf.value

DEFAULT_SAVEDIR = os.path.join(DOC_FOLDER, 'Coupon Book')

PREFSDIR = 'config/'
PREFSNAME = 'cb.ini'
SAVENAME = 'default.cbf'

SEP = '@@@'

PRODUCT_TAG = 'Product'
EXPIRY_TAG = 'Expiry'
DEAL_TAG = 'Deal'
STORE_TAG = 'Store'
BRAND_TAG = 'Brand'
DATE_ADDED_TAG = 'Date added'

TAGS = [
    PRODUCT_TAG,
    DEAL_TAG,
    EXPIRY_TAG,
    STORE_TAG,
    BRAND_TAG,
    DATE_ADDED_TAG
    ]

COL_PRODUCT_I = 0
COL_DEAL_I = 1
COL_EXPIRY_I = 2
COL_STORE_I = 3
COL_BRAND_I = 4
COL_DATE_ADDED_I = 5

COL_PRODUCT_W = 170
COL_DEAL_W = 305
COL_EXPIRY_W = 125
COL_STORE_W = 125
COL_BRAND_W = 125
COL_DATE_ADDED_W = 180

SORT_TO_COL_DATA = {
    PRODUCT_TAG: (COL_PRODUCT_I, COL_PRODUCT_W),
    EXPIRY_TAG: (COL_EXPIRY_I, COL_EXPIRY_W),
    DEAL_TAG: (COL_DEAL_I, COL_DEAL_W),
    STORE_TAG: (COL_STORE_I, COL_STORE_W),
    BRAND_TAG: (COL_BRAND_I, COL_BRAND_W),
    DATE_ADDED_TAG: (COL_DATE_ADDED_I, COL_DATE_ADDED_W), 
    }

DEFAULT_DEFAULT_SORT = DATE_ADDED_TAG
DEFAULT_REVERSE_SORT = False


#-------------------------------------------
# Class functionality addition
#-------------------------------------------

def GetSelectedItems(self):
    
    selection = []
    index = self.GetFirstSelected()
    
    if index >= 0:
        selection.append(index)
        while len(selection) < self.GetSelectedItemCount():
            index = self.GetNextSelected(index)
            selection.append(index)
  
    return selection

wx.ListCtrl.GetSelectedItems = GetSelectedItems


#-------------------------------------------
# Frame of main app
#-------------------------------------------

class Mainframe(wx.Frame):
    
    def __init__(self, parent, title):
        """(Mainframe, Frame, str) -> Mainframe
        
        Construct the Mainframe.
        """
        
        #-------------------------------------------
        # Initialize
        #-------------------------------------------
        
        # No-resize style
        
        STYLE_FRAME_MAIN = wx.DEFAULT_FRAME_STYLE ^ \
                    (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        
        # Frame

        wx.Frame.__init__(self, parent, title = title, size = (1200, 700),
                          style = STYLE_FRAME_MAIN)
        
        self.icon = wx.Icon('cb.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        
        # Panel
        
        self.panel = wx.Panel(self, -1)
        self.panel.SetBackgroundColour('#C6C5EB') # lavender
        
        # Status bar
        
        self.statusbar = self.CreateStatusBar()
        
        # Initialize preferences if they exist
        
        if os.path.exists(PREFSDIR):
            self.default_sort, self.reverse_sort, self.savedir = \
                self.set_preferences(self.open_preferences())
        
        # If no preferences have yet been saved, use the defaults
    
        else:
            self.default_sort = DEFAULT_DEFAULT_SORT
            self.reverse_sort = DEFAULT_REVERSE_SORT
            self.savedir = DEFAULT_SAVEDIR
        
        # Initialize other core variables
        
        self.sort = self.default_sort
        self.query = ''
        self.restore_index = 0
        self.file_has_changed = False
        
        
        #-------------------------------------------
        # Menu bar
        #-------------------------------------------        
        
        # File menu
        
        self.file_menu = wx.Menu()
             
        self.menu_button_restore = self.file_menu.Append(wx.ID_OPEN, "&Restore", "Restore from last save")
        self.menu_button_save = self.file_menu.Append(wx.ID_SAVE, "&Save", "Save coupon book")       
        
        self.file_menu.AppendSeparator()
        
        self.menu_button_exit = self.file_menu.Append(wx.ID_EXIT, "E&xit", "Quit CB")
        
        # Edit menu
        
        self.edit_menu = wx.Menu()
        
        self.menu_button_add = self.edit_menu.Append(wx.ID_ADD, "&Add coupon", "Add coupon")
        
        self.edit_menu.AppendSeparator()
        
        self.menu_button_edit = self.edit_menu.Append(wx.ID_EDIT, "&Edit selected coupons", "Edit selected coupons")
        self.menu_button_delete = self.edit_menu.Append(wx.ID_DELETE, "Delete selected coupons", "Delete selected coupons")
        self.menu_button_duplicate = self.edit_menu.Append(wx.ID_COPY, "&Duplicate selected coupons", "Duplicate selected coupons")
        
        self.edit_menu.AppendSeparator()
        
        self.menu_button_undo = self.edit_menu.Append(wx.ID_UNDO, "&Undo", "Undo last action")
        self.menu_button_redo = self.edit_menu.Append(wx.ID_REDO, "&Redo", "Redo last action")
        
        self.edit_menu.AppendSeparator()
        
        self.menu_button_prefs = self.edit_menu.Append(wx.ID_PREFERENCES, "&Preferences...", "Edit preferences")         
        
        # View menu
        
        self.view_menu = wx.Menu()
        
        self.menu_button_sort_date_added = self.view_menu.Append(-1, 'Sort by date added', 'Sort by date added')
        self.menu_button_sort_product = self.view_menu.Append(-1, 'Sort by product', 'Sort by product')
        self.menu_button_sort_expiry = self.view_menu.Append(-1, 'Sort by expiry', 'Sort by expiry')
        self.menu_button_sort_store = self.view_menu.Append(-1, 'Sort by store', 'Sort by store')
        self.menu_button_sort_brand = self.view_menu.Append(-1, 'Sort by brand', 'Sort by brand')
        
        # Help menu
        
        self.help_menu = wx.Menu()
        
        self.menu_button_help = self.help_menu.Append(wx.ID_HELP, '&Help', 'How to use CB')    
        self.menu_button_about = self.help_menu.Append(wx.ID_ABOUT, "&About CB", "Information about CB")
        
        # They start disabled
        
        self.menu_button_undo.Enable(False)
        self.menu_button_redo.Enable(False)
        
        # Menu bar
        
        self.menu_bar = wx.MenuBar()
        
        self.menu_bar.Append(self.file_menu, "&File")
        self.menu_bar.Append(self.edit_menu, '&Edit')
        self.menu_bar.Append(self.view_menu, '&View')
        self.menu_bar.Append(self.help_menu, '&Help')
        
        self.SetMenuBar(self.menu_bar)
        
        
        #-------------------------------------------
        # Labels and fields
        #-------------------------------------------
        
        # The order of these declarations determines tab navigation order
        
        # Coupon box
        
        self.coupon_box = wx.ListCtrl(self.panel, -1, style=wx.LC_REPORT | wx.LC_HRULES)
        self.coupon_box.InsertColumn(COL_PRODUCT_I, PRODUCT_TAG, width=COL_PRODUCT_W)
        self.coupon_box.InsertColumn(COL_DEAL_I, DEAL_TAG, width=COL_DEAL_W)
        self.coupon_box.InsertColumn(COL_EXPIRY_I, EXPIRY_TAG, width=COL_EXPIRY_W)
        self.coupon_box.InsertColumn(COL_STORE_I, STORE_TAG, width=COL_STORE_W)
        self.coupon_box.InsertColumn(COL_BRAND_I, BRAND_TAG, width=COL_BRAND_W)
        self.coupon_box.InsertColumn(COL_DATE_ADDED_I, DATE_ADDED_TAG, width=COL_DATE_ADDED_W)
        
        # Adder labels      
        
        self.label_product = wx.StaticText(self.panel, label = 'Product (required)')
        self.label_deal = wx.StaticText(self.panel, label = 'Deal (required)')
        self.label_expiry = wx.StaticText(self.panel, label = 'Expiry')
        self.label_store = wx.StaticText(self.panel, label = STORE_TAG)
        self.label_brand = wx.StaticText(self.panel, label = BRAND_TAG)
        
        # Adder fields
        
        self.field_product = wx.TextCtrl(self.panel, style = wx.TE_PROCESS_ENTER)
        self.field_deal = wx.TextCtrl(self.panel, style = wx.TE_PROCESS_ENTER)
        self.field_expiry = wx.TextCtrl(self.panel, style = wx.TE_PROCESS_ENTER)
        self.field_store = wx.TextCtrl(self.panel, style = wx.TE_PROCESS_ENTER)
        self.field_brand = wx.TextCtrl(self.panel, style = wx.TE_PROCESS_ENTER)
        
        self.field_product.SetFocus() # Program's focus begins here
        
        # Adder button
        
        self.button_add = wx.Button(self.panel, label = 'Add')        
        
        # Sort buttons
        
        self.button_sort_date_added = wx.Button(self.panel, label = 'Sort by date added')
        self.button_sort_product = wx.Button(self.panel, label = 'Sort by product')
        self.button_sort_expiry = wx.Button(self.panel, label = 'Sort by expiry')
        self.button_sort_store = wx.Button(self.panel, label = 'Sort by store')
        self.button_sort_brand = wx.Button(self.panel, label = 'Sort by brand')
        
        # Search
        
        self.label_search = wx.StaticText(self.panel, label = 'Search')
        self.field_search = wx.TextCtrl(self.panel)
        self.button_clear_search = wx.Button(self.panel, label = 'Clear')        
        
        # Manipulate buttons
        
        self.button_edit = wx.Button(self.panel, label = 'Edit selected')
        self.button_delete = wx.Button(self.panel, label = 'Delete selected')
        self.button_duplicate = wx.Button(self.panel, label = 'Duplicate selected')
        
        # Toggle expired checkboxes
        
        self.checkbox_show_expired = wx.CheckBox(self.panel, label = 'Show expired')
        self.checkbox_show_unexpired = wx.CheckBox(self.panel, label = 'Show unexpired')
        
        self.checkbox_show_expired.SetValue(True)
        self.checkbox_show_unexpired.SetValue(True)        
        
        
        #-------------------------------------------
        # Sizers
        #-------------------------------------------
        
        # Coupon box
        
        self.sizer_coupons = wx.BoxSizer(wx.VERTICAL)
        self.sizer_coupons.Add(self.coupon_box, 1)
        
        # Sort box
        
        self.sizer_sort = wx.StaticBoxSizer(wx.StaticBox(self.panel), wx.VERTICAL)
        self.sizer_sort.Add(self.button_sort_date_added, 0, wx.TOP, border=3)
        self.sizer_sort.Add(self.button_sort_product, 0, wx.TOP, border=8)
        self.sizer_sort.Add(self.button_sort_expiry, 0, wx.TOP, border=8)
        self.sizer_sort.Add(self.button_sort_store, 0, wx.TOP, border=8)
        self.sizer_sort.Add(self.button_sort_brand, 0, wx.TOP, border=8)
        
        # Search box
        
        self.sizer_search = wx.StaticBoxSizer(wx.StaticBox(self.panel), wx.VERTICAL)
        self.sizer_search.Add(self.label_search, 0, wx.TOP, border=3)
        self.sizer_search.Add(self.field_search, 0, wx.EXPAND|wx.TOP, border=2)
        self.sizer_search.Add(self.button_clear_search, 0, wx.TOP, border=8)
        
        # Manipulate box
        
        self.sizer_manipulate = wx.StaticBoxSizer(wx.StaticBox(self.panel), wx.VERTICAL)
        self.sizer_manipulate.Add(self.button_edit, 0, wx.TOP, border=3)
        self.sizer_manipulate.Add(self.button_delete, 0, wx.TOP, border=8)
        self.sizer_manipulate.Add(self.button_duplicate, 0, wx.TOP, border=8)
        
        # Toggle view box
        
        self.sizer_toggle_view = wx.StaticBoxSizer(wx.StaticBox(self.panel), wx.VERTICAL)
        self.sizer_toggle_view.Add(self.checkbox_show_expired, 0, wx.TOP, border=3)
        self.sizer_toggle_view.Add(self.checkbox_show_unexpired, 0, wx.TOP, border=8)
        
        # Toolbox
        
        self.sizer_tools = wx.BoxSizer(wx.VERTICAL)
        self.sizer_tools.Add(self.sizer_sort, 4)
        self.sizer_tools.Add(self.sizer_search, 3, wx.EXPAND|wx.TOP, border=20)
        self.sizer_tools.Add(self.sizer_manipulate, 3, wx.EXPAND|wx.TOP, border=20)
        self.sizer_tools.Add(self.sizer_toggle_view, 2, wx.EXPAND|wx.TOP, border=20)
        self.sizer_tools.AddSpacer(5)

        # Top half
        
        self.sizer_top = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_top.Add(self.sizer_coupons, 2, wx.EXPAND)
        self.sizer_top.Add(self.sizer_tools, 1, wx.LEFT, border=10)
        
        # Add labels
        
        self.sizer_add_labels = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_add_labels.Add(self.label_product, 0)
        self.sizer_add_labels.Add(self.label_deal, 0, wx.LEFT, border=170)
        self.sizer_add_labels.Add(self.label_expiry, 0, wx.LEFT, border=265)
        self.sizer_add_labels.Add(self.label_store, 0, wx.LEFT, border=156)
        self.sizer_add_labels.Add(self.label_brand, 0, wx.LEFT, border=99)
        
        # Add fields
        
        self.sizer_add_fields = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_add_fields.Add(self.field_product, 8)
        self.sizer_add_fields.Add(self.field_deal, 11, wx.LEFT, border=15)
        self.sizer_add_fields.Add(self.field_expiry, 6, wx.LEFT, border=15)
        self.sizer_add_fields.Add(self.field_store, 4, wx.LEFT, border=15)
        self.sizer_add_fields.Add(self.field_brand, 4, wx.LEFT, border=15)
        self.sizer_add_fields.Add(self.button_add, 4, wx.LEFT, border=15)
        
        # Adder
        
        self.sizer_add = wx.StaticBoxSizer(wx.StaticBox(self.panel), wx.VERTICAL)
        self.sizer_add.Add(self.sizer_add_labels, 1)
        self.sizer_add.Add(self.sizer_add_fields, 4, wx.EXPAND|wx.TOP, border=2)
        
        # Main sizer
        
        self.sizer_main = wx.BoxSizer(wx.VERTICAL)
        self.sizer_main.Add(self.sizer_top, 6, wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        self.sizer_main.AddSpacer(5)
        self.sizer_main.Add(self.sizer_add, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
        
        
        #-------------------------------------------
        # Boot up coupon box and show frame
        #-------------------------------------------
        
        # These must happen after creation of UI elements
        
        self.update_column_headings()
        self.on_restore(None)
        self.automatic_backup('open')
        self.undo_stack = [self.repr_cbook()]
        self.set_file_changed(False)         
        
        # Ready to show
        
        self.SetSizer(self.sizer_main)
        self.SetAutoLayout(True)
        self.Show(True) 
        
        
        #-------------------------------------------
        # Bindings
        #-------------------------------------------
        
        # Menu items
        
        self.Bind(wx.EVT_MENU, self.on_restore, self.menu_button_restore)
        self.Bind(wx.EVT_MENU, self.on_save, self.menu_button_save)  
        self.Bind(wx.EVT_MENU, self.on_exit, self.menu_button_exit)
        
        self.Bind(wx.EVT_MENU, self.on_add, self.menu_button_add)
        self.Bind(wx.EVT_MENU, self.on_edit, self.menu_button_edit)
        self.Bind(wx.EVT_MENU, self.on_delete, self.menu_button_delete)
        self.Bind(wx.EVT_MENU, self.on_duplicate, self.menu_button_duplicate)
        self.Bind(wx.EVT_MENU, self.on_undo, self.menu_button_undo)
        self.Bind(wx.EVT_MENU, self.on_redo, self.menu_button_redo)
        self.Bind(wx.EVT_MENU, self.on_preferences, self.menu_button_prefs)
        
        self.Bind(wx.EVT_MENU, self.on_sort_by_date_added, self.menu_button_sort_date_added)
        self.Bind(wx.EVT_MENU, self.on_sort_by_product, self.menu_button_sort_product)
        self.Bind(wx.EVT_MENU, self.on_sort_by_expiry, self.menu_button_sort_expiry)
        self.Bind(wx.EVT_MENU, self.on_sort_by_store, self.menu_button_sort_store)
        self.Bind(wx.EVT_MENU, self.on_sort_by_brand, self.menu_button_sort_brand)
        
        self.Bind(wx.EVT_MENU, self.on_about, self.menu_button_about)
        self.Bind(wx.EVT_MENU, self.on_help, self.menu_button_help)
        
        
        # Manipulate buttons
        
        self.Bind(wx.EVT_BUTTON, self.on_add, self.button_add)
        self.Bind(wx.EVT_BUTTON, self.on_delete, self.button_delete)
        self.Bind(wx.EVT_BUTTON, self.on_edit, self.button_edit)
        self.Bind(wx.EVT_BUTTON, self.on_duplicate, self.button_duplicate)
        
        # Toggle checkboxes
        
        self.Bind(wx.EVT_CHECKBOX, self.on_checkbox_expired, self.checkbox_show_expired)
        self.Bind(wx.EVT_CHECKBOX, self.on_checkbox_expired, self.checkbox_show_unexpired)
        
        # Sort buttons
        
        self.Bind(wx.EVT_BUTTON, self.on_sort_by_date_added, self.button_sort_date_added)
        self.Bind(wx.EVT_BUTTON, self.on_sort_by_product, self.button_sort_product)
        self.Bind(wx.EVT_BUTTON, self.on_sort_by_expiry, self.button_sort_expiry)
        self.Bind(wx.EVT_BUTTON, self.on_sort_by_store, self.button_sort_store)
        self.Bind(wx.EVT_BUTTON, self.on_sort_by_brand, self.button_sort_brand)
        
        # Window close
        
        self.Bind(wx.EVT_CLOSE, self.on_window_close)
        
        # Search
        
        self.field_search.Bind(wx.EVT_TEXT, self.on_search)
        self.Bind(wx.EVT_BUTTON, self.on_clear_search, self.button_clear_search)
        
        # Coupon box hotkeys
        
        self.coupon_box.Bind(wx.EVT_CHAR, self.on_cb_char)
        
        # Add hotkeys
        
        self.field_product.Bind(wx.EVT_TEXT_ENTER, self.on_add)
        self.field_deal.Bind(wx.EVT_TEXT_ENTER, self.on_add)
        self.field_expiry.Bind(wx.EVT_TEXT_ENTER, self.on_add)
        self.field_store.Bind(wx.EVT_TEXT_ENTER, self.on_add)
        self.field_brand.Bind(wx.EVT_TEXT_ENTER, self.on_add)
        
        
        #-------------------------------------------
        # Accelerators
        #-------------------------------------------
        
        # Ctrl + S = save
        
        self.ctrl_s_id = wx.NewId()
        self.Bind(wx.EVT_MENU, self.on_save, id=self.ctrl_s_id)
        ctrl_s_combo = (wx.ACCEL_CTRL, ord('S'), self.ctrl_s_id)
        
        # Ctrl + D = duplicate
        
        self.ctrl_d_id = wx.NewId()
        self.Bind(wx.EVT_MENU, self.on_duplicate, id=self.ctrl_d_id)
        ctrl_d_combo = (wx.ACCEL_CTRL, ord('D'), self.ctrl_d_id)
        
        # Alt + A = add
        
        self.alt_a_id = wx.NewId()
        self.Bind(wx.EVT_MENU, self.on_add, id=self.alt_a_id)
        alt_a_combo = (wx.ACCEL_ALT, ord('A'), self.alt_a_id)
        
        # Ctrl + Z = undo
        
        self.ctrl_z_id = wx.NewId()
        self.Bind(wx.EVT_MENU, self.on_undo, id=self.ctrl_z_id)
        ctrl_z_combo = (wx.ACCEL_CTRL, ord('Z'), self.ctrl_z_id)
        
        # Ctrl + Y = redo
        
        self.ctrl_y_id = wx.NewId()
        self.Bind(wx.EVT_MENU, self.on_redo, id=self.ctrl_y_id)
        ctrl_y_combo = (wx.ACCEL_CTRL, ord('Y'), self.ctrl_y_id)
        
        # Ctrl + R = restore
        
        self.ctrl_r_id = wx.NewId()
        self.Bind(wx.EVT_MENU, self.on_restore, id=self.ctrl_r_id)
        ctrl_r_combo = (wx.ACCEL_CTRL, ord('R'), self.ctrl_r_id)
        
        # Alt + P = preferences
        
        self.alt_p_id = wx.NewId()
        self.Bind(wx.EVT_MENU, self.on_preferences, id=self.alt_p_id)
        alt_p_combo = (wx.ACCEL_ALT, ord('P'), self.alt_p_id)
        
        # Ctrl + E = edit
        
        self.ctrl_e_id = wx.NewId()
        self.Bind(wx.EVT_MENU, self.on_edit, id=self.ctrl_e_id)
        ctrl_e_combo = (wx.ACCEL_CTRL, ord('E'), self.ctrl_e_id)
        
        # Sum up combos and initialize table
        
        combos = [ctrl_s_combo,
                  ctrl_d_combo,
                  alt_a_combo,
                  ctrl_z_combo,
                  ctrl_y_combo,
                  ctrl_r_combo,
                  alt_p_combo,
                  ctrl_e_combo]
        self.accelerator_table = wx.AcceleratorTable(combos)
        self.SetAcceleratorTable(self.accelerator_table)
        
        
    #-------------------------------------------
    # Menu button event handlers
    #-------------------------------------------
    
    def on_restore(self, event):
        """(Mainframe, Event) -> None
        
        Restore the last save of the coupon book. If the last save differs
        from the current state, prompt the user before restoring.
        """
        
        if self.ask_file_save_restore():
         
            # Open, read, and use the saved coupon book to overwrite current
            
            saved_cbook = self.open_saved_cbook()
            self.cbook = self.read_cbook(saved_cbook)
            
            # Refresh, update status bar, and set changed flag
            
            self.refresh_view()
            self.statusbar.SetStatusText('Restored last save of the coupon book')
            self.set_file_changed(False)
        
        
    def on_save(self, event):
        """(Mainframe, Event) -> None
        
        Save the coupon book to the file.
        """        
        
        # Ensure the directory exists
        
        if not os.path.exists(self.savedir):
            os.makedirs(self.savedir)
        
        # Write the current coupon book to the file
        
        f = open(os.path.join(self.savedir, SAVENAME), 'w+')
        f.write(self.repr_cbook())
        f.close()
        
        # Update the status bar and set the changed flag
        
        self.register_change()
        self.statusbar.SetStatusText('Saved the coupon book')
        self.set_file_changed(False)
        
        
    def on_about(self, event):
        """(Mainframe, Event) -> None
        
        Show the about dialog.
        """         
        
        info = wx.AboutDialogInfo()
        
        info.SetIcon(self.icon)
        info.SetName(ABOUT_NAME)
        info.SetVersion(ABOUT_VERSION)
        info.SetDescription(ABOUT_DESCRIPTION)
        info.SetCopyright(ABOUT_COPYRIGHT)
        info.SetWebSite(ABOUT_WEBSITE)
        info.SetLicence(ABOUT_LICENCE)
        info.AddDeveloper(ABOUT_DEVELOPER)
        
        wx.AboutBox(info)
        
        
    def on_help(self, event):
        """(Mainframe, Event) -> None
        
        Show the help dialog.
        """         
        
        message = wx.MessageDialog(self, HELP_MESSAGE, \
                                   "Coupon Book help", wx.OK)
        message.ShowModal()
        message.Destroy()
          
    
    def on_exit(self, event, response = None):
        """(Mainframe, Event) -> None
        
        Close the window. First ask the user whether they want to save or
        scrap their work or cancel the close. This response is provided in
        advance if called by an OS window close.
        """         
        
        if not response:
            # This returns a no response if we don't need to ask.
            response = self.ask_file_save_exit()
        
        # Only close if not cancelled.
        if response != wx.ID_CANCEL:
            
            # Save if they say yes.
            if response == wx.ID_YES:
                self.on_save(None)
            
            # Otherwise just make a backup and quit.
            self.automatic_backup('exit')
            self.Close(True)
    
    
    #-------------------------------------------
    # Sort button handlers
    #-------------------------------------------
            
            
    def on_sort_by_date_added(self, event):
        """(Mainframe, Event) -> None
        
        Sort by date added (or reverse if already doing so).
        """ 
        
        self.sort_and_refresh(DATE_ADDED_TAG)
        
        
    def on_sort_by_product(self, event):
        """(Mainframe, Event) -> None
        
        Sort by product name (or reverse if already doing so).
        """ 
        
        self.sort_and_refresh(PRODUCT_TAG)
        
        
    def on_sort_by_expiry(self, event):
        """(Mainframe, Event) -> None
        
        Sort by expiry date (or reverse if already doing so).
        """
        
        self.sort_and_refresh(EXPIRY_TAG)
        
        
    def on_sort_by_store(self, event):
        """(Mainframe, Event) -> None
        
        Sort by store name (or reverse if already doing so).
        """   
        
        self.sort_and_refresh(STORE_TAG)
        
        
    def on_sort_by_brand(self, event):
        """(Mainframe, Event) -> None
        
        Sort by brand name (or reverse if already doing so).
        """   
        
        self.sort_and_refresh(BRAND_TAG)
        
    
    #-------------------------------------------
    # Other button event handlers
    #-------------------------------------------
        
    def on_undo(self, event):
        """(Mainframe, Event) -> None
        
        Undo the last action the user took.
        """         
        
        if not self.check_last_undo():
        
            # Move one up the stack of program states (towards the past).
            self.restore_index += 1
            
            # Extract the state from the stack and use it to overwrite current.
            last_backup = self.undo_stack[self.restore_index]
            self.cbook = self.read_cbook(last_backup)
            
            # Refresh the view and update the status bar.
            self.refresh_view()
            self.statusbar.SetStatusText('Undid last action')
            
            # Enable the redo button (even if it's already enabled).
            self.menu_button_redo.Enable()
            
            # Check if this was the oldest state and disable undo if so.
            if self.check_last_undo():
                self.menu_button_undo.Enable(False)
        
        
    def on_redo(self, event):
        """(Mainframe, Event) -> None
        
        Redo the last action the user undid.
        """         
        
        if not self.check_last_redo():
        
            # Move one down the stack of program states (towards the present).
            self.restore_index -= 1
            
            # Extract the state from the stack and use it to overwrite current.
            last_backup = self.undo_stack[self.restore_index]
            self.cbook = self.read_cbook(last_backup)
            
            # Refresh the view and update the status bar.
            self.refresh_view()
            self.statusbar.SetStatusText('Redid last action')
            
            # Enable the undo button (even if it's already enabled).
            self.menu_button_undo.Enable()
            
            # Check if this is the newest state and disable redo if so.
            if self.check_last_redo():
                self.menu_button_redo.Enable(False)
                
        
    def on_add(self, event):
        """(Mainframe, Event) -> None
        
        Add a coupon to the book if the information entered is valid.
        """         
        
        # Extract and strip data from the adder fields.
        product = self.field_product.GetValue().strip()
        deal = self.field_deal.GetValue().strip()
        expiry = self.field_expiry.GetValue().strip()
        store = self.field_store.GetValue().strip()
        brand = self.field_brand.GetValue().strip()
        
        # Validate the data.
        if self.validate_add(product, deal, expiry, store, brand):
            
            # Create the coupon and add it to our coupon book.
            coupon = Coupon(product, deal, expiry, store, brand)
            self.cbook.add(coupon)
            
            # Clear the adder fields.
            self.field_product.ChangeValue('')
            self.field_deal.ChangeValue('')
            self.field_expiry.ChangeValue('')
            self.field_store.ChangeValue('')
            self.field_brand.ChangeValue('')
            
            # Refresh the view and update the status bar.
            self.refresh_view()
            self.statusbar.SetStatusText('Added coupon for {}'.format(product))
            
            # Focus and select the added item.
            select_i = self.coupon_box.GetItemCount() - 1
            self.focus_coupon_box_item(select_i)
            
            # Register the new state.
            self.register_change()
            
            
    def on_delete(self, event):
        """(Mainframe, Event) -> None
        
        Delete all selected coupons.
        """         
        
        # Get the selected indices.
        selected = self.coupon_box.GetSelectedItems()
        
        if selected:
        
            # Get each coupon's data and delete it.
            for coupon_i in selected:
                coupon_data = self.extract_row_data(coupon_i)
                self.cbook.delete(coupon_data)
            
            # Refresh the view and update the status bar.
            self.refresh_view()
            self.statusbar.SetStatusText('Deleted {} item(s)'.format(len(selected)))
            
            # Register the new state.
            self.register_change()
        
        # None selected 
        else:
            wx.MessageBox('No coupons are selected.')
            self.coupon_box.SetFocus()
        
    
    def on_edit(self, event):
        """(Mainframe, Event) -> None
        
        Edit all selected coupons.
        """         
        
        # Get the selected indices.
        selected = self.coupon_box.GetSelectedItems()
        
        if selected:
            
            # This number affects the status bar update.
            # It can vary because the user can cancel an edit screen.
            num_changed = 0
            
            # Get each coupon's data and offer it up for editing.
            for coupon_i in selected:
                coupon_data = self.extract_row_data(coupon_i)
                i, coupon = self.cbook.match(coupon_data)
                
                # Extract in order to auto-fill the edit fields.
                old_data = coupon.get_data()
                
                # Initiate the dialog.
                dialog = EditCouponDialog(coupon_data = old_data,
                                          title = 'Edit Coupon'
                                          )
                response = dialog.ShowModal()
                
                # Extract the values and set the new data for the coupon.
                if response == wx.ID_OK:
                    
                    product = dialog.field_product.GetValue().strip()
                    deal = dialog.field_deal.GetValue().strip()
                    expiry = dialog.field_expiry.GetValue().strip()
                    store = dialog.field_store.GetValue().strip()
                    brand = dialog.field_brand.GetValue().strip()
                    
                    coupon.set_data(product, deal, expiry, store, brand)
                    
                    # Track that an edit was made.
                    if coupon.get_data() != old_data:
                        num_changed += 1
                
                dialog.Destroy()
            
            if num_changed:
                
                # Register the change and refresh the view.
                self.register_change()
                self.refresh_view()
                
                self.statusbar.SetStatusText('Edited {} item(s)'.format(num_changed))
            
            # Re-select the selection.
            for coupon in selected:
                self.focus_coupon_box_item(coupon)
        
        # None selected    
        else:
            wx.MessageBox('No coupons are selected.')
            self.coupon_box.SetFocus()
        
        
    def on_duplicate(self, event):
        """(Mainframe, Event) -> None
        
        Duplicate all selected coupons.
        """         
        
        # Get the selected indices.
        selected = self.coupon_box.GetSelectedItems()
        
        if selected:
            
            # Extract the coupon data.
            for coupon_i in selected:
                coupon_data = self.extract_row_data(coupon_i)
                i, coupon = self.cbook.match(coupon_data)
                
                # Make a new coupon and add it to the book.
                product, deal, expiry, store, brand, added = coupon.get_data()
                new_coupon = Coupon(product, deal, expiry, store, brand)
                self.cbook.add(new_coupon)
            
            # Register the change and refresh the view.
            self.register_change()
            self.refresh_view()
            
            # Select the new coupons by virtue of their being the most recent
            for i in self.get_most_recent(len(selected)):
                self.focus_coupon_box_item(i)
            
            self.statusbar.SetStatusText('Duplicated {} item(s)'.format(len(selected)))
            
            
        # None selected 
        else:
            wx.MessageBox('No coupons are selected.')
            self.coupon_box.SetFocus()
            
                
    def on_preferences(self, event):

        """Mainframe, Event) -> None
        
        Open the preferences dialog and update any data the user changes.
        """
        
        dialog = EditPreferencesDialog(title = 'Edit Preferences',
                                       default_sort = self.default_sort,
                                       reverse_sort = self.reverse_sort,
                                       savedir = self.savedir
                                       )
        response = dialog.ShowModal()
        
        # Extract the values and set the new data for the coupon.
        if response == wx.ID_OK:
            
            old_savedir = self.savedir
            
            # Set the preferences
            self.default_sort = dialog.radio_default_sort.GetStringSelection()[8:]
            self.default_sort = self.default_sort[0].upper() + self.default_sort[1:]
            self.reverse_sort = dialog.checkbox_reverse_sort.GetValue()
            self.savedir = dialog.button_savedir.GetValue()
            
            # Save the preferences and update the status bar
            self.save_preferences()            
            
            # If the save location has changed, save
            if old_savedir != self.savedir:
                self.on_save(None)
                self.statusbar.SetStatusText('Saved preferences and saved coupon book in new location')
            else:
                self.statusbar.SetStatusText('Saved preferences')
        
        # Destroy the dialog in any case
        dialog.Destroy()
            
            
    def on_clear_search(self, event):
        """(Mainframe, Event) -> None
        
        Clear the search field and refresh the view.
        """
        
        self.query = ''
        self.field_search.ChangeValue('')
        self.refresh_view()
        
    
    #-------------------------------------------
    # Nonstandard event handlers
    #-------------------------------------------
    
    def on_window_close(self, event):
        """(Mainframe, Event) -> None
        
        Catch an OS window close. If we can veto it, then first ask the user
        whether they want to save or scrap their work or cancel the close.
        """
        
         # We can stop the close if we like
        if event.CanVeto():
            
            # This returns a no response if we don't need to ask.
            response = self.ask_file_save_exit()
            
            if response == wx.ID_CANCEL:
                event.Veto()
            
            # If they say yes or no, handle it as a normal exit event
            else:
                self.on_exit(None, response)
         
        # If we can't stop the close we must destroy the frame   
        else:
            self.Destroy()
            
    
    def on_checkbox_expired(self, event):
        """(Mainframe, Event) -> None
        
        Simply trigger a view refresh. The view refresh algorithm checks the
        value of this checkbox.
        """
        
        self.refresh_view()
        
        
    def on_search(self, event):
        """(Mainframe, Event) -> None
        
        Set the search query and trigger a view refresh. The view refresh
        algorithm checks the query.
        """   
        
        self.query = self.field_search.GetValue().strip()
        self.refresh_view()
    
    
    def on_cb_char(self, event):
        """(Mainframe, Event) -> None
        
        Provide delete and Ctrl + A functionality for the coupon box, which
        otherwise lacks them.
        """
        
        # Determine the keycode
        key = event.GetKeyCode()
        
        # Delete
        if key == wx.WXK_DELETE or key == wx.WXK_NUMPAD_DELETE:
            self.on_delete(None)
        
        # Control + A has its own keycode
        elif key == 1:
            
            for i in range(0, self.coupon_box.GetItemCount()):
                self.coupon_box.Select(i)
        
        # Pass the event on in case it's neither of those
        else:
            event.Skip()
        
        
    #-------------------------------------------
    # Helpers
    #-------------------------------------------
    
    def sort_and_refresh(self, key):
        '''(Mainframe, str) -> None
        
        Sort and refresh the coupon box using the given key.
        Reverse the sort if the key was the last used (or unreverse if reversed).
        '''
        
        self.reverse_sort = False if self.sort != key else not self.reverse_sort
        self.sort = key
        self.update_column_headings()
        self.refresh_view()
        
    
    def focus_coupon_box_item(self, i):
        """(Mainframe, int) -> None
        
        Select and focus the given item, and give the coupon box focus.
        """
        
        self.coupon_box.Focus(i)            
        self.coupon_box.Select(i)
        self.coupon_box.SetFocus()    
    
    
    def check_query_match(self, coupon_data):
        """(Mainframe, tuple of (str, str, str, str, str) -> None
        
        Check whether any field in the given data matches the search query.
        """
        
        for field in coupon_data:
            
            # Normalize the results to avoid case sensitivity.
            if self.query.upper() in field.upper():
                return True
        
        return False
    
    
    def automatic_backup(self, name):
        """(Mainframe, str) -> None
        
        Back up the last good set of data, giving it a version of string name.
        """
                    
        if os.path.exists(os.path.join(self.savedir, SAVENAME)):
            
            # Read the existing file.
            f1 = open(os.path.join(self.savedir, SAVENAME), 'r')
            content = f1.read()
            f1.close()
            
            backup_name = os.path.join(
                self.savedir,
                SAVENAME[:-4] + '_backup_last_good_{}.cbf'.format(name)
                )
            
            # Write it to a new file.
            f2 = open(backup_name, 'w+')
            f2.write(content)
            f2.close()
    
    
    def extract_row_data(self, row):
        """(Mainframe, int) -> tuple of (str, srt, str, str, str, str)
        
        Given a row index in the coupon box, return each column's data.
        """
        
        product = self.coupon_box.GetItem(row, 0).GetText()
        deal = self.coupon_box.GetItem(row, 1).GetText()
        expiry = self.coupon_box.GetItem(row, 2).GetText()
        store = self.coupon_box.GetItem(row, 3).GetText()
        brand = self.coupon_box.GetItem(row, 4).GetText()
        date_added = self.coupon_box.GetItem(row, 5).GetText()
        
        return product, deal, expiry, store, brand, date_added
    
    
    def ask_file_save_exit(self):
        """(Mainframe) -> None
        
        If a filesave is pending on close, ask the user to save or drop the
        changes, or to cancel the close. If no filesave is pending, close.
        """
        
        if self.get_file_changed():
            
            # Create the dialog.
            dialog = wx.MessageDialog(
                None,
                'Do you want to save your changes before exiting?',
                'Save before exiting',
                wx.YES | wx.YES_DEFAULT | wx.NO | wx.CANCEL)
        
            # Get the response.
            response = dialog.ShowModal()
            dialog.Destroy()
            
            return response
        
        # Default is not to save if no changes have been made.
        else:
            return wx.ID_NO
        
    
    def ask_file_save_restore(self):
        """(Mainframe) -> None
        
        If a filesave is pending on restore, ask the user to confirm dropping
        the changes in favour of the restored save. If no filesave is pending,
        don't restore. (This should not be called when no filesave is pending.)
        """
        
        if self.get_file_changed():
            
            # Create the dialog.
            dialog = wx.MessageDialog(
                None,
                'Are you sure you want to restore your last save?',
                'Restore last save',
                wx.YES | wx.NO | wx.YES_DEFAULT)
            
            # Get the response.
            response = dialog.ShowModal()
            dialog.Destroy()
            
            return response
        
        # Default is not to take any action..
        else:
            return wx.ID_NO
        
        
    def read_cbook(self, cbook_s):
        """(Mainframe, str) -> Coupon_Book
        
        Read a string representing a Coupon_Book's data and create and return
        the resulting Coupon_Book.
        """
        
        cbook = Coupon_Book()
        
        # Written with newline characters to separate coupons.
        lines = cbook_s.split('\n')
        
        for line in lines:
            values = line.split(SEP)
            
            # Some lines may be ill-formed.
            if len(values) == 6:
                
                # Read, create, and add the coupon.
                product, deal, expiry, store, brand, added = values
                coupon = Coupon(product, deal, expiry, store, brand, added)
                cbook.add(coupon)
                
        return cbook
    
    
    def open_saved_cbook(self):
        """(Mainframe) -> str
        
        Open the save file and return the string resulting from reading it.
        """
        
        if not os.path.exists(os.path.join(self.savedir)):
            os.makedirs(self.savedir)
                    
        if os.path.exists(os.path.join(self.savedir, SAVENAME)):
                    
            f = open(os.path.join(self.savedir, SAVENAME), 'r')
            saved_cbook = f.read()
            f.close()
        
            return saved_cbook
        
        else:
            
            return ''
    
    
    def display_coupon(self, coupon_data):
        """(Mainframe, tuple of (str, str, str, str, str, str) -> None
        
        Update the coupon box by setting a coupon on a row.
        """
        
        # Insert the string item to begin the row.
        row = self.coupon_box.InsertStringItem(sys.maxint, coupon_data[0])
        
        # Set each subsequent column of the row.
        for i in range(1, len(coupon_data)):
            self.coupon_box.SetStringItem(row, i, coupon_data[i])
    
    
    def refresh_view(self):
        """(Mainframe) -> None
        
        Clear the coupon box and refill it with the contents of the current
        current coupon book, according to the sort function, the expired toggle,
        and the search query.
        """
        
        # Clear existing content.
        self.coupon_box.DeleteAllItems()
        
        # Get a sorted list of coupons from the coupon book.
        for coupon in self.cbook.sort_coupons(self.sort, self.reverse_sort):
            
            # Extract the data.
            coupon_data = coupon.get_data()
            
            # Check that it matches the search query. (Exclude date added.)
            if self.check_query_match(coupon_data[0:5]):
                
                # Display if expired and the user wants to see expired.
                if coupon.is_expired() and self.checkbox_show_expired.GetValue():
                    self.display_coupon(coupon_data)
                
                # Display if unexpired and the user wants to see unexpired.
                elif not coupon.is_expired() and self.checkbox_show_unexpired.GetValue():
                    self.display_coupon(coupon_data) 
        
    
    def register_change(self):
        """(Mainframe) -> None
        
        Make the current state the newest one in the undo stack, enable undo,
        and set the file changed flag.
        """
        
        # Chop away any redos (states that are newer than the current one),
        # reset the index, and add this one in.
        self.undo_stack = self.undo_stack[self.restore_index:]
        self.restore_index = 0
        self.undo_stack.insert(0, self.repr_cbook())
        
        # Set the undo and redo buttons.
        self.menu_button_undo.Enable()
        self.menu_button_redo.Enable(False)
        
        # Set the flag.
        self.set_file_changed()
    
    
    def check_last_undo(self):
        """(Mainframe) -> bool
        
        Return True iff we are at the bottom of the undo stack.
        """
        
        return self.restore_index == len(self.undo_stack) - 1
    
    
    def check_last_redo(self):
        """(Mainframe) -> bool
        
        Return True iff we are at the top of the undo stack.
        """
        
        return self.restore_index == 0
        
        
    def repr_cbook(self):
        """(Mainframe) -> str
        
        Return a string consisting of the contents of the coupon book. This
        consists of putting each coupon's fields, separated by SEP, on a line.
        """
        
        s = ''
        
        for coupon in self.cbook.get_coupons():
            s += (SEP.join(coupon.get_data()) + '\n')
            
        return s
        
        
    @classmethod
    def validate_add(self, product, deal, expiry, store, brand):
        """(Mainframe, str, str, str, str, str) -> bool
        
        Return True iff the coupon data being added or edited is valid.
        """
        
        # Ensure it has at least a product, deal details, and an expiry date.
        if (not product) or (not deal):
            dialog = wx.MessageBox('You must enter at least a product name '\
                + "and the deal's details.", 'Add coupon failed',
                wx.OK | wx.ICON_WARNING)
            
            return False
        
        # Try to parse the expiry date entered.
        try:
            parse(expiry)
        except:
            wx.MessageBox('The date could not be parsed.',
                          'Add coupon failed', wx.OK | wx.ICON_WARNING)
            return False
        
        # Check for the presence of the separator
        for field in product, deal, expiry, store, brand:
            if SEP in field:
                wx.MessageBox(
                    'The string "{}" is not allowed for technical reasons.'
                    .format(SEP))
                return False
        
        # Otherwise, this data is fine.
        return True
                
                
    def set_file_changed(self, change = True):
        """(Mainframe, bool) -> None
        
        Update the file changed flag and set the restore and save buttons.
        A False value for change means disable the buttons.
        """
        
        self.file_has_changed = change
        self.menu_button_restore.Enable(change)
        self.menu_button_save.Enable(change)
        
        
    def get_file_changed(self):
        """(Mainframe) -> bool
        
        Return True iff the file change flag is True.
        """
        
        return self.file_has_changed
    
    
    def get_most_recent(self, n):
        """(Mainframe, int) -> list of int
        
        Return an list of indices in the coupon box, sorted in descending order
        by the date the corresponding coupon was added.
        """
        
        # Build dict of date added to the indexes that include it
        date_to_i = {
            }
        
        for i in range(self.coupon_box.GetItemCount() - 1, -1, -1):
            
            # Last column is date added
            date = parse(self.coupon_box.GetItem(i, 5).GetText())
            
            if date not in date_to_i:
                date_to_i[date] = [i]
            else:
                date_to_i[date].append(i)
            
        
        # Get a sorted list of dates
        dates = date_to_i.keys()
        dates.sort(reverse=True)
        
        # Build list of final indexes
        final_indexes = []
        
        for date in dates:
            
            for i in date_to_i[date]:
                
                # Keep adding indexes until we have enough
                if len(final_indexes) < n:
                    final_indexes.append(i)
                
                # Then return
                else:
                    return final_indexes
                
    
    def open_preferences(self):
        """(Mainframe) -> str
        
        Open the preferences file and return a string of its contents.
        """
        
        if os.path.exists(os.path.join(PREFSDIR, PREFSNAME)):
                    
            f = open(os.path.join(PREFSDIR, PREFSNAME), 'r')
            prefs = f.read()
            f.close()
        
            return prefs
    
        
    def set_preferences(self, prefs):
        """(Mainframe, str) -> None
        
        Read the given string and set the preference variables.
        """
        
        lines = prefs.split('\n')
        
        default_sort = lines[0]
        
        # This is saved as a string...
        if lines[1] == 'False':
            reverse_sort = False
        elif lines[1] == 'True':
            reverse_sort = True
            
        savedir = lines[2]
        
        return default_sort, reverse_sort, savedir
        
      
    def repr_preferences(self):
        """(Mainframe) -> str
        
        Return a string consisting of the preference variables. This consists
        of putting each on a line in the order: sort, reverse_sort, savedir.
        """
            
        return '{}\n{}\n{}'.format(self.default_sort, self.reverse_sort, self.savedir)
      
     
    def save_preferences(self):
        """(Mainframe) -> None
        
        Save the preference variables to the preferences file.
        """
        
        # Ensure the directory exists
        
        if not os.path.exists(PREFSDIR):
            os.makedirs(PREFSDIR)
        
        # Write the current coupon book to the file
        
        f = open(os.path.join(PREFSDIR, PREFSNAME), 'w+')
        f.write(self.repr_preferences())
        f.close()
        
        
    def update_column_headings(self):
        """(Mainframe) -> None
        
        Change the header of a column in the coupon box. Use refresh_view()
        afterwards to populate the column again.
        """
        
        sort_heading = self.sort
        sort_i = SORT_TO_COL_DATA[sort_heading][0]
        sort_w = SORT_TO_COL_DATA[sort_heading][1]
        
        for i in range(len(TAGS)):
            
            self.coupon_box.DeleteColumn(i)
            
            if i != sort_i:
                
                self.coupon_box.InsertColumn(
                    col = i ,
                    heading = TAGS[i],
                    width = SORT_TO_COL_DATA[TAGS[i]][1]
                    )
                
            else:
                
                sort_heading = self.sort+ ' (Sort)' if not self.reverse_sort \
                    else self.sort + ' (Reverse sort)'
                
                self.coupon_box.InsertColumn(
                    col = sort_i ,
                    heading = sort_heading,
                    width = sort_w
                    )
        
            
            
#-------------------------------------------
# Dialog for editing a coupon
#-------------------------------------------

class EditCouponDialog(wx.Dialog):
    
    def __init__(self, coupon_data = ('', '', '', '', ''), *args, **kw):
        
        #-------------------------------------------
        # Initialize.
        #------------------------------------------- 
        
        super(EditCouponDialog, self).__init__(None, *args, **kw)
        
        self.panel = wx.Panel(self)
        
        self.SetSize((1200, 120))
        self.SetTitle("Edit Coupon")
        
        # Extract the data, with which the fields will be filled.
        product, deal, expiry, store, brand, added = coupon_data
        
        #-------------------------------------------
        # Labels and fields
        #-------------------------------------------
        
        # Labels for above editor fields
        
        self.label_product = wx.StaticText(self.panel, label = 'Product (required)')
        self.label_deal = wx.StaticText(self.panel, label = 'Deal (required)')
        self.label_expiry = wx.StaticText(self.panel, label = 'Expiry')
        self.label_store = wx.StaticText(self.panel, label = STORE_TAG)
        self.label_brand = wx.StaticText(self.panel, label = BRAND_TAG)
        
        # Editor fields
        
        self.field_product = wx.TextCtrl(self.panel, value=product, style=wx.TE_PROCESS_ENTER)
        self.field_deal = wx.TextCtrl(self.panel, value=deal, style=wx.TE_PROCESS_ENTER)
        self.field_expiry = wx.TextCtrl(self.panel, value=expiry, style=wx.TE_PROCESS_ENTER)
        self.field_store = wx.TextCtrl(self.panel, value=store, style=wx.TE_PROCESS_ENTER)
        self.field_brand = wx.TextCtrl(self.panel, value=brand, style=wx.TE_PROCESS_ENTER)
        
        # Focus begins on the product field.
        
        self.field_product.SetFocus()
        
        # OK and cancel buttons
        
        self.button_ok = wx.Button(self.panel, wx.ID_OK)
        self.button_cancel = wx.Button(self.panel, wx.ID_CANCEL)
        
        #-------------------------------------------
        # Sizers
        #-------------------------------------------
        
        # Edit headings
        
        self.sizer_headings = wx.BoxSizer(wx.HORIZONTAL)
        
        self.sizer_headings.Add(self.label_product, 0)
        self.sizer_headings.Add(self.label_deal, 0, wx.LEFT, border=143)
        self.sizer_headings.Add(self.label_expiry, 0, wx.LEFT, border=230)
        self.sizer_headings.Add(self.label_store, 0, wx.LEFT, border=137)
        self.sizer_headings.Add(self.label_brand, 0, wx.LEFT, border=98)
        
        # edit fields
        
        self.sizer_fields = wx.BoxSizer(wx.HORIZONTAL)
        
        self.sizer_fields = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_fields.Add(self.field_product, 8)
        self.sizer_fields.Add(self.field_deal, 11, wx.LEFT, border=15)
        self.sizer_fields.Add(self.field_expiry, 6, wx.LEFT, border=15)
        self.sizer_fields.Add(self.field_store, 4, wx.LEFT, border=15)
        self.sizer_fields.Add(self.field_brand, 4, wx.LEFT, border=15)
        self.sizer_fields.Add(self.button_ok, 4, wx.LEFT, border=15)
        self.sizer_fields.Add(self.button_cancel, 4, wx.LEFT, border=15)
        
        # Main sizer
                
        self.sizer_main = wx.BoxSizer(wx.VERTICAL)
        
        self.sizer_main.Add(self.sizer_headings, 1, wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        self.sizer_main.Add(self.sizer_fields, 4, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
        
        # Set sizer
        
        self.SetSizer(self.sizer_main)
        self.SetAutoLayout(True)
        
        # ---------------------------
        # Bindings
        # ---------------------------
        
        # Window close events
        
        self.Bind(wx.EVT_BUTTON, self.on_cancel, self.button_cancel)
        self.Bind(wx.EVT_CLOSE, self.on_window_close)
        self.Bind(wx.EVT_BUTTON, self.on_OK, self.button_ok)
        
        # Edit hotkeys
        
        self.field_product.Bind(wx.EVT_TEXT_ENTER, self.on_OK)
        self.field_deal.Bind(wx.EVT_TEXT_ENTER, self.on_OK)
        self.field_expiry.Bind(wx.EVT_TEXT_ENTER, self.on_OK)
        self.field_store.Bind(wx.EVT_TEXT_ENTER, self.on_OK)
        self.field_brand.Bind(wx.EVT_TEXT_ENTER, self.on_OK)
            
    # ---------------------------
    # Events
    # ---------------------------
    
    def on_OK(self, event):
        """(EditCouponDialog, Event) -> None
        
        Extract the coupon's data, validate it, and return.
        """
        
        # Extract the fields' data.
        p_product = self.field_product.GetValue().strip()
        p_deal = self.field_deal.GetValue().strip()
        p_expiry = self.field_expiry.GetValue().strip()
        p_store = self.field_store.GetValue().strip()
        p_brand = self.field_brand.GetValue().strip()
        
        # Validate this data. If it's validated, send the OK code and quit.
        if Mainframe.validate_add(p_product, p_deal, p_expiry, p_store, p_brand):
            self.SetReturnCode(wx.ID_OK)
            self.Close()
    
    
    def on_cancel(self, event):
        """(EditCouponDialog, Event) -> None
        
        Close via the cancel button.
        """
        
        self.Close(True)
        
        
    def on_window_close(self, event):
        """(EditCouponDialog, Event) -> None
        
        Destroy this dialog after a Windows window quit.
        """
        
        self.Destroy()
        
        
#-------------------------------------------
# Dialog for editing a coupon
#-------------------------------------------

class EditPreferencesDialog(wx.Dialog):
    
    def __init__(self, default_sort = '', reverse_sort = '', savedir = DEFAULT_SAVEDIR, *args, **kw):
        
        #-------------------------------------------
        # Initialize.
        #------------------------------------------- 
        
        super(EditPreferencesDialog, self).__init__(None, *args, **kw)
        
        self.panel = wx.Panel(self)
        
        self.SetSize((350, 350))
        self.SetTitle("Edit Preferences")
        
        #-------------------------------------------
        # Labels and fields
        #-------------------------------------------
        
        # Sort fields
        
        self.radio_default_sort = wx.RadioBox(
            self.panel,
            label = 'Choose the default sort order when opening the program',
            style = wx.RA_SPECIFY_ROWS,
            majorDimension = 5,
            choices = ['Sort by date added',
                       'Sort by product',
                       'Sort by expiry',
                       'Sort by store',
                       'Sort by brand'
                       ]
        )
        
        self.radio_default_sort.SetSelection(self.radio_default_sort.FindString('Sort by ' + default_sort))
        
        self.checkbox_reverse_sort = wx.CheckBox(self.panel, label = 'Reverse sort order?')
        self.checkbox_reverse_sort.SetValue(reverse_sort)
        
        # Save directory
        
        self.label_savedir = wx.StaticText(self.panel, label = 'Choose save directory')
        
        self.button_savedir = filebrowsebutton.DirBrowseButton(
            self.panel,
            labelText = 'Directory: ',
            newDirectory = True,
            startDirectory = savedir)
        
        self.button_savedir.SetValue(savedir)
        
        # OK and cancel buttons
        
        self.button_OK = wx.Button(self.panel, wx.ID_OK)
        self.button_cancel = wx.Button(self.panel, wx.ID_CANCEL)
        
        #-------------------------------------------
        # Sizers
        #-------------------------------------------
        
        # Sort
        
        self.sizer_sort = wx.BoxSizer(wx.VERTICAL)
        
        self.sizer_sort.Add(self.radio_default_sort, 4)
        self.sizer_sort.Add(self.checkbox_reverse_sort, 1, wx.TOP, border=5)
        
        # Static line
        
        self.sizer_sort.Add(wx.StaticLine(self.panel, style = wx.LI_HORIZONTAL))
        
        # Save dir
        
        self.sizer_savedir = wx.BoxSizer(wx.VERTICAL)
        
        self.sizer_savedir.Add(self.label_savedir, 0)
        self.sizer_savedir.Add(self.button_savedir, 3, wx.EXPAND|wx.TOP, border=2)
        
        # Static line
        
        self.sizer_savedir.Add(wx.StaticLine(self.panel, style = wx.LI_HORIZONTAL))
        
        # OK and cancel
        
        self.sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        
        self.sizer_buttons.Add(self.button_OK, 1)
        self.sizer_buttons.Add(self.button_cancel, 1, wx.LEFT, border=10)
        
        # Main sizer
                
        self.sizer_main = wx.BoxSizer(wx.VERTICAL)
        
        self.sizer_main.Add(self.sizer_sort, 5, wx.TOP|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=10)
        self.sizer_main.Add(self.sizer_savedir, 4, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
        self.sizer_main.Add(self.sizer_buttons, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.TOP|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
        
        # Set sizer
        
        self.SetSizer(self.sizer_main)
        self.SetAutoLayout(True)
        
        # ---------------------------
        # Bindings
        # ---------------------------
        
        # Window close events
        
        self.Bind(wx.EVT_BUTTON, self.on_cancel, self.button_cancel)
        self.Bind(wx.EVT_CLOSE, self.on_window_close)
        self.Bind(wx.EVT_BUTTON, self.on_OK, self.button_OK)
    
            
    # ---------------------------
    # Events
    # ---------------------------
    
    def on_OK(self, event):
        """(EditCouponDialog, Event) -> None
        
        Extract the coupon's data, validate it, and return.
        """
        
        self.SetReturnCode(wx.ID_OK)
        self.Close()
    
    
    def on_cancel(self, event):
        """(EditCouponDialog, Event) -> None
        
        Close via the cancel button.
        """
        
        self.Close(True)
        
        
    def on_window_close(self, event):
        """(EditCouponDialog, Event) -> None
        
        Destroy this dialog after a Windows window quit.
        """
        
        self.Destroy()
    
        
#-------------------------------------------
# Running the actual program
#-------------------------------------------

CB = wx.App(False)
frame = Mainframe(None, 'Coupon Book')
CB.MainLoop()