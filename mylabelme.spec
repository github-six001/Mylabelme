# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path
import paddlex  # 确保在修改前先安装 paddlex
import paddleocr
import paddle
block_cipher = None

# 打包时，将本地的site-packages下的资源全部放入了与可执行文件（mylabelme.exe）同级的_internal中
site_packages_path = r"D:\Program Files\Python39\Lib\site-packages"


# 计算路径
LABELME_PATH = './labelme'
try:
    import osam
    import paddlex
    import paddle
    import paddleocr
    import os
    OSAM_PATH = os.path.dirname(osam.__file__)
    paddlex_version = os.path.join(os.path.dirname(paddlex.__file__), '.version')
    paddleocr_path = os.path.dirname(paddleocr.__file__)
except ImportError:
    OSAM_PATH = ''
a = Analysis(
    ['labelme\\__main__.py'],
    pathex=[os.path.abspath('.'),LABELME_PATH],
    binaries=paddle_binaries + [],
    datas=paddle_datas+ [
            # OSAM 模型文件
        (os.path.join(OSAM_PATH, '_models', 'yoloworld', 'clip', 'bpe_simple_vocab_16e6.txt.gz'),
         os.path.join('osam', '_models', 'yoloworld', 'clip')),

        # Labelme 配置文件
        (os.path.join(LABELME_PATH, 'config', 'default_config.yaml'),
         os.path.join('labelme', 'config')),

        # Labelme 图标文件
        (os.path.join(LABELME_PATH, 'icons', '*'),
         os.path.join('labelme', 'icons')),

        # 翻译文件
        (os.path.join(LABELME_PATH, 'translate', '*'),'translate'),

        # paddleocr文件
        (os.path.join(paddleocr_path, '*'),'paddleocr'),

        # paddlex_version
        (paddlex_version,'paddlex'),
          # --- 这是需要添加或修改的部分 ---
        ('models', 'models'),
#        (site_packages_path, '_internal'),
                # 配置文件等其他资源
#        ('config/*', 'config'),
    ],
    hiddenimports=[
    'paddleocr',
    'paddleocr.ppocr',
    'paddle',
    'paddle.nn',
    'paddle.nn.functional',
    'cv2',
    'numpy',
    'scipy',
    'PIL',
    'pkg_resources',
    'pyclipper',
    'shapely',
    'lmdb',
    'premailer',
    'cssutils'

            # 可能需要手动添加的隐藏依赖
        'osam',
        'labelme',
        'clip',
        'PIL',
        'PyQt5',
        'numpy',
        'scipy',
        'sklearn',
        'skimage',
        'cv2',
        'matplotlib',
        'qtpy',
#        'superqt',
        ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='mylabelme',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='mylabelme',
)
