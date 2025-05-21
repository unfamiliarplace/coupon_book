# Python 2.7.10
# Copyright August 2015 by Luke Sawczak

#-------------------------------------------
# Imports
#-------------------------------------------

from dateutil.parser import parse
from time import strftime
from datetime import datetime


#-------------------------------------------
# Constants
#-------------------------------------------

NO_EXPIRY_VAL = "Doesn't expire"
ANY_VAL = "Any"

#-------------------------------------------
# Coupon functionality
#-------------------------------------------

class Coupon(object):
    
    def __init__(self, product, deal, expiry, store, brand, added = None):
        """(Coupon, str, str, str, str, str, str) -> Coupon
        
        Construct the Coupon.
        """
        
        # Needed because u'' (passed by gui) does not evaluate to False
        store = store if store != '' else ANY_VAL
        brand = brand if brand != '' else ANY_VAL
        expiry = expiry if expiry != '' else NO_EXPIRY_VAL
        
        added = added if added else self.format_current_time()
        
        self.set_data(product, deal, expiry, store, brand, added)
        
    
    def get_data(self):
        """(Coupon) -> tuple of (str, str, str, str, str, str)
        
        Return a tuple of the coupon's data.
        """
        
        return (self._product,
                self._deal,
                self._expiry,
                self._store,
                self._brand,
                self._added)
    
    
    def set_data(self, product, deal, expiry, store, brand, added = None):
        """(Coupon, str, sr, str, str, str, str, str) -> None
        
        Receive and format all data and set the date added.
        """
        
        # Needed because u'' (passed by gui) does not evaluate to False
        
        store = store if store != '' else ANY_VAL
        brand = brand if brand != '' else ANY_VAL      
        
        self._product = self.capitalize(product)
        self._deal = self.capitalize(deal)
        
        if expiry == '':
            self._expiry = NO_EXPIRY_VAL
        elif expiry != NO_EXPIRY_VAL:
            self._expiry = self.format_expiry(parse(expiry))
        else:
            self._expiry = expiry
        
        self._store = self.capitalize(store)
        self._brand = self.capitalize(brand)
        
        self._added = added if added else self._added
    
        
    def format_expiry(self, dt):
        """(Coupon, datetime) -> str
        
        Return a formatted string of the given datetime expiry date.
        """
        
        month = dt.strftime('%B')
        
        # The day should not have a 0 in front of it.
        day = dt.strftime('%d')
        if day[0] == '0':
            day = day[1]
            
        year = dt.strftime('%Y')
        return month + ' ' + day + ', ' + year
    
    
    def format_current_time(self):
        """(Coupon) -> str
        
        Return a formatted string of the current time.
        """
        
        date = self.format_expiry(datetime.now())
        time = strftime('%H:%M:%S')
        return date + ' at ' + time
    
    
    def get_sortable_date_added(self):
        """(Coupon) -> datetime
        
        Return a parsed datetime of the date added.
        """
        
        return parse(self._added, fuzzy=True)
    
    
    def get_sortable_expiry(self):
        """(Coupon) -> datetime
        
        Return a parsed datetime of the expiry date.
        """
        
        if self._expiry != NO_EXPIRY_VAL:
            return parse(self._expiry, fuzzy=True)
        else:
            return parse('December 31, 9999')
    
    
    def get_sortable_product(self):
        """(Coupon) -> str
        
        Return a case-insensitive string of the product name.
        """
        
        return self._product.upper()
    
    
    def get_sortable_store(self):
        """(Coupon) -> str
        
        Return a case-insensitive string of the store name.
        """
        
        return self._store.upper()
    
    
    def get_sortable_brand(self):
        """(Coupon) -> str
        
        Return a case-insensitive string of the brand name.
        """
        
        return self._brand.upper()
    
    
    def is_expired(self):
        """(Coupon) -> bool
        
        Return True iff this coupon is expired.
        """
        
        # Check whether the expiry date is earlier than today's date.
        if self._expiry == NO_EXPIRY_VAL:
            return False
        else:
            return parse(self._expiry) < parse(strftime('%B %d, %Y'))
    
    
    def capitalize(self, s):
        """(Coupon, str) -> str
        
        Return a copy of the string with the first letter capitalized and the
        rest of the string (if there is any) in its original case.
        """
        
        first = s[0].upper()
        
        return first if len(s) == 1 else first + s[1:]
    

#-------------------------------------------
# Coupon Book functionality
#-------------------------------------------

class Coupon_Book(object):
    
    # A table of the sorting keywords to the function used as the sorting key.
    KEYWORD_TO_FUNCTION = {
        None: Coupon.get_sortable_date_added,
        'Date added': Coupon.get_sortable_date_added,
        'Product': Coupon.get_sortable_product,
        'Expiry': Coupon.get_sortable_expiry,
        'Store': Coupon.get_sortable_store,
        'Brand': Coupon.get_sortable_brand,
    }    
    
    
    def __init__(self):
        """(Coupon_Book) -> None
        
        
        Construct with an empty list of coupons.
        """
        
        self._coupons = []
        
        
    def add(self, coupon):
        """"(Coupon_Book, Coupon) -> None
        
        Add the given Coupon to the Coupon_Book.
        """
        
        self._coupons.append(coupon)
    
    
    def get_coupons(self):
        """"(Coupon_Book) -> list of Coupons
        
        Return a shallow copy of the list of Coupons.
        """
        
        return self._coupons[:]
    
    
    def sort_coupons(self, keyword, reverse):
        """(Coupon_Book, str, bool) -> list of Coupons
        
        Return a shallow copy of the list of coupons that have been sorted
        according to the keyword, and reversed iff reverse is True.
        """
        
        coupons = self._coupons[:]
        key = self.KEYWORD_TO_FUNCTION[keyword]
        coupons.sort(key = key, reverse = reverse)
        
        return coupons
    
    
    def delete(self, data):
        """(Coupon_Book, tuple of (str, str, str, str, str, str)
        
        Delete the first Coupon that matches the given data.
        """
        
        i, coupon = self.match(data)
        return self._coupons.pop(i)
        
            
    def match(self, data):
        """(Coupon_Book, tuple of (str, str, str, str, str, str)
        
        Find the first Coupon that matches the given data.
        """
        
        i = 0
        while i < len(self._coupons):
            if self._coupons[i].get_data() == data:
                return i, self._coupons[i]
            i += 1