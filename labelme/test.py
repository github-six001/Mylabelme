import requests
import tarfile
import os


def download_model(model_url, save_path):
    """下载模型文件"""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    response = requests.get(model_url, stream=True)
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    # 解压
    with tarfile.open(save_path, 'r') as tar:
        tar.extractall(path=os.path.dirname(save_path))

    # 删除压缩包
    os.remove(save_path)


# 下载所有模型
models = {
    'det': 'https://paddleocr.bj.bcebos.com/PP-OCRv3/chinese/ch_PP-OCRv3_det_infer.tar',
    'rec': 'https://paddleocr.bj.bcebos.com/PP-OCRv3/chinese/ch_PP-OCRv3_rec_infer.tar',
    'cls': 'https://paddleocr.bj.bcebos.com/dygraph_v2.0/ch/ch_ppocr_mobile_v2.0_cls_infer.tar'
}

for model_type, url in models.items():
    print(f"正在下载 {model_type} 模型...")
    download_model(url, f'./models/{model_type}_model.tar')