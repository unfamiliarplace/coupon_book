@echo on

pyinstaller "Coupon Book.spec"

COPY "cb.ico" "dist/Coupon Book"