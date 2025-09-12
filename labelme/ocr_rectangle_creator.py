# # -*- coding: utf-8 -*-
#

# OCR创建多边形页面
# import os
# import re
#
# from PyQt5 import QtCore, QtWidgets
# from paddleocr import PaddleOCR
# from labelme.shape import Shape
# import os
# import sys
# import tempfile
# import shutil
# import logging
# import cv2
# import numpy as np
#
# class OCRRectangleCreator:
#     """OCR矩形创建器，集成PaddleOCR功能"""
#
#     def __init__(self, main_window):
#         """
#         初始化OCR矩形创建器
#
#         Args:
#             main_window: MainWindow实例
#         """
#         self.main_window = main_window
#         self.ocr = None
#
#
#         self.ocr_engine = None
#         # self.setup_environment()
#         self.initialize_ocr()
#
#
#
#     def initialize_ocr(self):
#         """初始化PaddleOCR"""
#         try:
#
#             models_path = get_models_path()
#             det_model_path = os.path.join(models_path, "PP-OCRv5_server_det")
#             rec_model_path = os.path.join(models_path, "PP-OCRv5_server_rec")
#             self.ocr = PaddleOCR(
#                 use_doc_orientation_classify=False,
#                 use_doc_unwarping=False,
#                 det_model_dir=det_model_path,
#                 rec_model_dir=rec_model_path,
#                 use_textline_orientation=False)
#             print("PaddleOCR初始化成功")
#         except Exception as e:
#             print(f"PaddleOCR初始化失败: {e}")
#             self.ocr = None
#
#     def process_image_with_ocr(self, image_path):
#         """
#         使用PaddleOCR处理图像并返回识别结果
#
#         Args:
#             image_path: 图像文件路径
#
#         Returns:
#             list: OCR识别结果，包含文本位置和内容
#         """
#         if not self.ocr:
#             self.initialize_ocr()
#             if not self.ocr:
#                 self.main_window.errorMessage("错误", "OCR引擎初始化失败")
#                 return None
#
#         if not os.path.exists(image_path):
#             self.main_window.errorMessage("错误", f"图像文件不存在: {image_path}")
#             return None
#
#         try:
#             # 使用numpy读取文件
#             with open(image_path, 'rb') as f:
#                 img_array = np.frombuffer(f.read(), dtype=np.uint8)
#
#             # 解码图片
#             img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
#             img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#
#             # 使用PaddleOCR进行识别
#             result = self.ocr.ocr(img)
#             pointslist = result[0]['dt_polys']
#             txtlist = result[0]['rec_texts']
#             scores = result[0]['rec_scores']
#
#             # 解析结果
#             ocr_results = []
#
#             # 同时遍历坐标、文本和置信度
#             for i, (points, text, confidence) in enumerate(zip(pointslist, txtlist, scores)):
#                 # 处理坐标点
#                 x_coords = [p[0] for p in points]
#                 y_coords = [p[1] for p in points]
#                 x1, x2 = min(x_coords), max(x_coords)
#                 y1, y2 = min(y_coords), max(y_coords)
#                 # 构建OCR结果字典
#                 ocr_results.append({
#                     'points': points,
#                     'bbox': [x1, y1, x2, y2],
#                     'text': text,
#                     'confidence': confidence,
#                     'label': 'text'
#                 })
#             return ocr_results
#
#         except Exception as e:
#             self.main_window.errorMessage("OCR错误", f"OCR处理失败: {str(e)}")
#             return None
#
#     def create_rectangles_from_ocr(self, image_path, min_confidence=0.5, auto_label=True):
#         """
#         根据OCR结果批量创建矩形
#
#         Args:
#             image_path: 图像文件路径
#             min_confidence: 最小置信度阈值
#             auto_label: 是否自动使用识别文本作为标签
#
#         Returns:
#             int: 创建的矩形数量
#         """
#         # 先加载图像到LabelMe
#         if not self.main_window.loadFile(image_path):
#             return 0
#
#         # 进行OCR识别
#         ocr_results = self.process_image_with_ocr(image_path)
#         if not ocr_results:
#             return 0
#
#         # 过滤低置信度的结果
#         filtered_results = [r for r in ocr_results if r['confidence'] >= min_confidence]
#
#         if not filtered_results:
#             self.main_window.errorMessage("提示", "未找到符合条件的文本区域")
#             return 0
#
#         # 批量创建矩形
#         created_count = 0
#         for result in filtered_results:
#             bbox = result['bbox']
#             text = result['text']
#             confidence = result['confidence']
#
#             # 确定标签
#             if auto_label:
#                 label = text
#             else:
#                 label = "text"
#
#             is_chinese_text = self.is_chinese(text)
#
#             # 创建注释信息
#             if is_chinese_text:
#                 annotation = f"{text}"
#                 annotation_eng = None
#             else:
#                 annotation = None  # 对于非中文也使用中文标签保持一致性
#                 annotation_eng = f"{text}"
#
#             # 创建矩形
#             success = self.create_single_rectangle(
#                 bbox[0], bbox[1], bbox[2], bbox[3],
#                 label, annotation, annotation_eng
#             )
#
#             if success:
#                 created_count += 1
#
#         # 显示结果统计
#         self.main_window.status(
#             f"成功创建 {created_count} 个矩形标注 (总共识别到 {len(ocr_results)} 个文本区域)"
#         )
#
#         return created_count
#
#     def create_single_rectangle(self, x1, y1, x2, y2, label, annotation=None, annotation_eng=None):
#         """
#         创建单个矩形
#
#         Args:
#             x1, y1: 左上角坐标
#             x2, y2: 右下角坐标
#             label: 标签文本
#             annotation: 中文注释
#             annotation_eng: 英文注释
#
#         Returns:
#             bool: 是否创建成功
#         """
#         try:
#             # 检查是否已存在相同位置和标签的形状
#             for existing_shape in self.main_window.canvas.shapes:
#                 if (existing_shape.shape_type == "rectangle" and
#                         existing_shape.label == label and
#                         len(existing_shape.points) == 2 and
#                         abs(existing_shape.points[0].x() - x1) < 5 and
#                         abs(existing_shape.points[0].y() - y1) < 5 and
#                         abs(existing_shape.points[1].x() - x2) < 5 and
#                         abs(existing_shape.points[1].y() - y2) < 5):
#                     return False
#
#             #直接操作canvas
#             shape = Shape(
#                 label=label,
#                 annotation=annotation,
#                 annotation_eng=annotation_eng,
#                 shape_type="rectangle",
#             )
#             shape.addPoint(QtCore.QPointF(x1, y1))
#             shape.addPoint(QtCore.QPointF(x2, y2))
#             shape.close()
#             self.main_window.canvas.storeShapes()
#             self.main_window.loadShapes([shape], replace=False)
#             self.main_window.setDirty()
#             # self.main_window.addLabel(shape)
#             self.main_window.canvas.update()
#             return True
#         except Exception as e:
#             print(f"创建矩形失败: {e}")
#             return False
#
#     def show_ocr_dialog(self):
#         """
#         显示OCR处理对话框
#         """
#         if self.main_window.image.isNull():
#             self.main_window.errorMessage("错误", "请先加载图像")
#             return
#
#         dialog = QtWidgets.QDialog(self.main_window)
#         dialog.setWindowTitle("OCR批量创建矩形")
#         dialog.setModal(True)
#         dialog.resize(400, 300)
#
#         layout = QtWidgets.QVBoxLayout(dialog)
#
#         # 说明标签
#         label = QtWidgets.QLabel("使用PaddleOCR识别图像中的文本并自动创建矩形标注")
#         label.setWordWrap(True)
#         layout.addWidget(label)
#
#         # 置信度阈值
#         confidence_layout = QtWidgets.QHBoxLayout()
#         confidence_label = QtWidgets.QLabel("置信度阈值:")
#         confidence_spin = QtWidgets.QDoubleSpinBox()
#         confidence_spin.setRange(0.1, 1.0)
#         confidence_spin.setValue(0.5)
#         confidence_spin.setSingleStep(0.1)
#         confidence_layout.addWidget(confidence_label)
#         confidence_layout.addWidget(confidence_spin)
#         layout.addLayout(confidence_layout)
#
#         # 自动标签选项
#         auto_label_check = QtWidgets.QCheckBox("使用识别文本作为标签")
#         auto_label_check.setChecked(True)
#         layout.addWidget(auto_label_check)
#
#         # 进度标签
#         progress_label = QtWidgets.QLabel("准备开始...")
#         progress_label.setAlignment(QtCore.Qt.AlignCenter)
#         layout.addWidget(progress_label)
#
#         # 按钮
#         button_box = QtWidgets.QDialogButtonBox()
#         start_button = button_box.addButton("开始识别", QtWidgets.QDialogButtonBox.AcceptRole)
#         cancel_button = button_box.addButton("取消", QtWidgets.QDialogButtonBox.RejectRole)
#         layout.addWidget(button_box)
#
#         # 添加关闭计时器
#         close_timer = QtCore.QTimer()
#         close_timer.setSingleShot(True)
#         close_timer.timeout.connect(dialog.accept)
#
#         def start_processing():
#             progress_label.setText("正在处理中，请稍候...")
#             QtWidgets.QApplication.processEvents()  # 更新UI
#
#             min_confidence = confidence_spin.value()
#             auto_label = auto_label_check.isChecked()
#
#             # 获取当前图像路径
#             current_image = self.main_window.filename
#             if current_image:
#                 count = self.create_rectangles_from_ocr(
#                     current_image, min_confidence, auto_label
#                 )
#                 progress_label.setText(f"处理完成！创建了 {count} 个矩形标注")
#                 # 2秒后自动关闭
#                 close_timer.start(2000)
#             else:
#                 progress_label.setText("错误：无法获取当前图像路径")
#
#         start_button.clicked.connect(start_processing)
#         cancel_button.clicked.connect(dialog.reject)
#
#         dialog.exec_()
#
#     def is_chinese(self,string):
#
#         pattern = re.compile(r'[\u4e00-\u9fa5]+')
#
#         match = pattern.search(string)
#
#         return match is not None
#
#     def setup_environment(self):
#         """设置打包环境"""
#         if getattr(sys, 'frozen', True):
#             # 打包环境
#             self.fix_packed_environment()
#
#     def fix_packed_environment(self):
#         """修复打包后的环境"""
#         try:
#             # 设置临时目录用于存储模型文件
#             temp_dir = tempfile.gettempdir()
#             ocr_temp_dir = os.path.join(temp_dir, 'paddleocr_temp')
#             os.makedirs(ocr_temp_dir, exist_ok=True)
#
#             # 设置环境变量
#             os.environ['PADDLE_HOME'] = ocr_temp_dir
#             os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
#
#             # 复制必要的文件
#             self.copy_necessary_files(ocr_temp_dir)
#
#         except Exception as e:
#             logging.error(f"Environment fix failed: {e}")
#
#     def copy_necessary_files(self, target_dir):
#         """复制必要的文件到目标目录"""
#         try:
#             # 获取源文件路径
#             if hasattr(sys, '_MEIPASS'):
#                 base_path = sys._MEIPASS
#                 # 检查打包的文件是否存在
#                 packed_ocr_path = os.path.join(base_path, 'paddleocr')
#                 if os.path.exists(packed_ocr_path):
#                     # 复制整个 paddleocr 目录
#                     target_ocr_path = os.path.join(target_dir, 'paddleocr')
#                     if os.path.exists(target_ocr_path):
#                         shutil.rmtree(target_ocr_path)
#                     shutil.copytree(packed_ocr_path, target_ocr_path)
#         except Exception as e:
#             logging.warning(f"File copy failed: {e}")
# def get_models_path():
#     """获取模型文件路径"""
#     if getattr(sys, 'frozen', False):  # 打包环境
#         # 在打包环境中，资源文件通常在 _MEIPASS 目录下
#         base_path = sys._MEIPASS
#         base_path = os.path.join(base_path, "models")
#     else:  # 开发环境
#         base_path = os.path.dirname(os.path.abspath(__file__))
#         base_path = os.path.join(base_path, "..", "models")
#     return base_path