# Coupon Book

This is an old desktop app (2015) made in Python using WX. It was one of my first larger programs and GUIs.

It allows you to enter coupon data and sort them in various ways, such as by expiry date or product, so you can use them more effectively. Intended for the sort of person who receives and keeps tons of coupons in the mail. :)

## Setup

The program was written in Python 2.7.10. The only dependency not bundled is WX.

In this archival repo, I've also provided the original installer under setup, or you can build it yourself or run the executable directly. It's portable — the preferences dialog offers you the choice of save directory — but it does create a `Coupon Book` folder under your user's `Documents` folder by default. Config files are saved in the same directory as the executable.

## TODO (when this was still a going concern)

- faceted search
- toolbar
- help book (http://wxpython.org/Phoenix/docs/html/html.HtmlHelpController.html)
