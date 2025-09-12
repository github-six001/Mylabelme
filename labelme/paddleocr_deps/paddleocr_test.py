# PaddleOCR测试脚本
try:
    from paddleocr import PaddleOCR
    print("PaddleOCR导入成功")
except ImportError as e:
    print(f"PaddleOCR导入失败: {e}")
    sys.exit(1)

try:
    import paddle
    print("PaddlePaddle导入成功")
except ImportError as e:
    print(f"PaddlePaddle导入失败: {e}")
    sys.exit(1)

print("所有依赖导入成功")
