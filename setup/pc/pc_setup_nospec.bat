@echo on

pyinstaller --name="Coupon Book" ^
    --onedir --windowed ^
    --icon=m:/luke/random/compsci/coupon_book/cb.ico ^
    --upx-dir=c:\python27\scripts\upx391w\ ^
    m:/luke/random/compsci/coupon_book/gui.py

COPY "cb.ico" "dist/Coupon Book"