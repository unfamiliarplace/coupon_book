#-------------------------------------------
# Help messages
#------------------------------------------- 

HELP_GENERAL = """COUPON BOOK

Coupon Book (CB) is a coupon manager.

Add coupons by typing in the bar at the bottom of the window. For example, you could enter a coupon for pizza at Dominos where the deal is $2 off a large and it expires on December 5. Once you have a list of coupons, you can sort, search, edit, delete, and duplicate them, or restrict your selection to those that have expired. You also save, restore, undo, and redo commands at your disposal.
"""

HELP_HOTKEYS = """HOTKEYS

Coupon Book has a menu item or button for every function, but there are also
a number of hotkeys available to help you navigate it easily.

Ctrl-S: Save
Ctrl-R: Restore last save
Alt-A: Add coupon
Ctrl-D: Duplicate selected coupons
Ctrl-E: Edit selected coupons
Ctrl-Z: Undo
Ctrl-Y: Redo
Alt-A: Edit preferences
Ctrl-A (on coupon box): Select all coupons
Delete (on coupon box): Delete selected coupons

The usual text-editing hotkeys are available for the text fields.
"""

HELP_SAVE = """SAVE AND RESTORE

You have only one coupon book file, which you can save at any time by pressing Ctrl-S. You will also be prompted to save it when you exit, if you have made any changes since your last save.

This same coupon data will be restored when you open the program. If you want to restore your coupons to their state the last time you saved, press Ctrl-R. 

Also, an automatic backup is made every time the program is successfully opened and again when it is successfully exited. Look for these files in your user's Documents folder, under Coupon Book, if you want to restore them (which you can do by renaming one to default.cbf).
"""

HELP_UNDO = """UNDO

You can undo all the steps you've taken since opening the program. Just press Ctrl-Z to undo one step at a time. If you want to redo a step you've undone, press Ctrl-Y. If you reach the oldest or the newest state, these buttons in the menu will be greyed out.

If you save, you will lose your redo history. The same thing holds if undo a step and then take any new actions. Your undo history, however, remains until you close the program.
"""

HELP_SORT = """SORT

You can sort the list of coupons by five vectors: the date added, the product name, the expiry date, the store name, or the brand name. Click on a button to sort by that vector. If you click on the same one again, you can get a reverse sort. The default sort is by date added.

The current sort, or reverse sort, is indicated on the column headings.
"""

HELP_SEARCH = """SEARCH

Type some text in the search box, and the list of coupons will instantly filter to your selection. All columns except date added are included in the search. You can easily clear the search text by pressing the Clear button.
"""

HELP_ADD = """ADD COUPON

To add a coupon, enter values for the product and the details of the deal. Add an expiry date if it has one. The expiry date will be intelligently parsed, so if you type "jan 5", you will get January 5 of the current year. If the coupon has a specific store or brand requirement, you can enter those too. Then click Add to add it to the list.
"""

HELP_EDIT = """EDIT

Select one or more coupons and click Edit to open a window where you can edit their data. You will edit the selected coupons one after another.
"""

HELP_DELETE = """DELETE

Select one or more coupons and click Delete to delete them. Don't worry; you can always undo this step or restore to a previous save!
"""

HELP_DUPLICATE = """DUPLICATE

Select one or more coupons and click Duplicate to make a copy of each. The selection will switch to the new coupons. Don't forget that you can edit them afterwards if they differ from existing coupons by only one or two details.
"""

HELP_TOGGLE_EXPIRED = """SHOW EXPIRED

Use the checkboxes to choose which types of coupons you want to see: those that are expired, those that are still current, or both. This could be useful for deleting coupons that have expired, for example.
"""

HELP_PREFERENCES = """PREFERENCES

Certain aspects of Coupon Book can be customized. To change your preferences, press Ctrl-E. You can change two preferences: the default sort order you see when you open the program, and the location of your save file. This is your "My Documents" folder by default.

When changing your save file location, note that the program will immediately save in the new location. However, the old location will not be cleared out. If you want to do so, you should manually delete those files.
"""

HELP_WRAPUP = """
If you have any questions, write to Luke Sawczak at luke@unfamiliarplace.com.

Thank you for using Coupon Book!
"""

HELP_MESSAGE = '\n'.join((HELP_GENERAL, HELP_HOTKEYS, HELP_SAVE, HELP_SORT,
                        HELP_SEARCH, HELP_ADD, HELP_EDIT, HELP_DELETE,
                        HELP_DUPLICATE, HELP_TOGGLE_EXPIRED, HELP_PREFERENCES,
                        HELP_WRAPUP))

#-------------------------------------------
# About messages
#------------------------------------------- 

ABOUT_DESCRIPTION = """Coupon Book (CB) is a coupon manager.
Features include tracking coupon expiry dates, product names, and stores,
custom sort methods, and search.
"""

ABOUT_LICENCE = """Coupon Book is free software; you can redistribute 
it and/or modify it under the terms of the GNU General Public License as 
published by the Free Software Foundation, either version 2 of the License, 
or (at your option) any later version.

Coupon Book is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details. You should have 
received a copy of the GNU General Public License along with File Hunter; 
if not, write to the Free Software Foundation, Inc., at 59 Temple Place, 
Suite 330, Boston, MA  02111-1307  USA
"""

ABOUT_NAME = 'Coupon Book'
ABOUT_VERSION = '1.02'
ABOUT_COPYRIGHT = '(C) 2015 Luke Sawczak'
ABOUT_WEBSITE = ('http://unfamiliarplace.com', 'My homepage')
ABOUT_DEVELOPER = 'Luke Sawczak'