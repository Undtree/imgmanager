from PIL import Image as PilImage
from transformers import CLIPProcessor, CLIPModel
import torch
import os

# 自动检测设备。由于我的缓存不够，求助显存。
# 优先使用 CUDA (NVIDIA)，其次使用 MPS (Mac M1/M2/M3)，最后兜底 CPU
device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
print(f"正在使用计算设备: {device}")

model_id = "openai/clip-vit-base-patch32"

offline_path = "/app/offline_model"
local_path = "../local_clip_model"
print(f"{local_path}")

if os.path.exists(os.path.join(offline_path, "config.json")):
    print(f"使用本地离线模型: {offline_path}")
    model_id = offline_path
elif os.path.exists(os.path.join(local_path, "config.json")):
    print(f"使用本地离线模型: {local_path}")
    model_id = local_path
else:
    print("未找到离线模型，尝试在线下载...")
    model_id = "openai/clip-vit-base-patch32"

# 加载模型并立即移动到指定设备 (降低系统内存占用)
try:
    model = CLIPModel.from_pretrained(model_id, use_safetensors=True).to(device)
    processor = CLIPProcessor.from_pretrained(model_id, use_safetensors=True)
    print(f"CLIP 模型加载完成 (运行于 {device})")
except Exception as e:
    print(f"模型加载失败: {e}")
    # 可以在这里做一些错误处理，比如回退到 CPU

CANDIDATE_LABELS = {
    "landscape": "风景",
    "seashore": "海边",
    "mountain": "山脉",
    "forest": "森林",
    "sky": "天空",
    "person": "人物",
    "man": "男人",
    "woman": "女人",
    "cat": "猫",
    "dog": "狗",
    "flower": "花朵",
    "tree": "树木",
    "food": "美食",
    "building": "建筑",
    "car": "汽车",
    "screenshot": "截图",
    "text": "文字资料"
}
english_labels = list(CANDIDATE_LABELS.keys())

def classify_image(image_file):
    """
    使用 CLIP 进行匹配
    """
    try:
        img = PilImage.open(image_file)
        
        # 处理输入：生成 Tensor
        inputs = processor(
            text=english_labels, 
            images=img, 
            return_tensors="pt", 
            padding=True
        )

        # inputs 是一个字典，包含 pixel_values 等，需要逐个移动
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
        
        # 计算相似度
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1)

        # 获取结果 (结果还在显卡上，转回 CPU 取值)
        values, indices = torch.topk(probs, 3)
        
        suggested_tags = []
        for i in range(3):
            idx = indices[0][i].item() # .item() 会自动从 GPU 取回数值到 CPU
            score = values[0][i].item()
            
            if score > 0.1: 
                en_tag = english_labels[idx]
                cn_tag = CANDIDATE_LABELS[en_tag]
                suggested_tags.append(cn_tag)

        if not suggested_tags:
            return ["其他"]
        
        image_file.seek(0)

        return suggested_tags

    except Exception as e:
        print(f"CLIP 分析出错: {e}")
        # 如果显存爆了 (CUDA Out of memory)，可以在这里尝试清空缓存
        if "CUDA out of memory" in str(e):
            torch.cuda.empty_cache()
        return []