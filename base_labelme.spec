# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

block_cipher = None

# 计算路径
LABELME_PATH = './labelme'
try:
    import osam

    OSAM_PATH = os.path.dirname(osam.__file__)

except ImportError:
    OSAM_PATH = ''

a = Analysis(
    ['labelme\\__main__.py'],
    pathex=[os.path.abspath('.'),LABELME_PATH],
    binaries=paddle_binaries +[],
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

         ],
    hiddenimports=[
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
        'superqt',
        ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='base_labelme',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
