# -*- mode: python -*-
a = Analysis(['m:/luke/random/compsci/coupon_book/gui.py'],
             pathex=['M:\\Luke\\Random\\compsci\\coupon_book\\setup\\pc'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='Coupon Book.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False , icon='m:\\luke\\random\\compsci\\coupon_book\\cb.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='Coupon Book')
