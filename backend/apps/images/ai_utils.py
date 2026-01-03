from PIL import Image as PilImage
from transformers import CLIPProcessor, CLIPModel
import torch

# 预加载模型 (全局单例，避免每次请求都重载)
# weights='DEFAULT' 会自动下载预训练权重 (约 100MB)
model_id = "openai/clip-vit-base-patch32"

model = CLIPModel.from_pretrained(model_id)
processor = CLIPProcessor.from_pretrained(model_id)
print("CLIP 模型加载完成")

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

# 加载 ImageNet 类别标签 (英文)
# 为了不依赖外部文件，这里简化处理，通常 torchvision 会自动处理类别 ID
# 我们稍后直接用翻译库把英文结果转中文

def classify_image(image_file):
    """
    使用 CLIP 进行匹配
    """
    try:
        img = PilImage.open(image_file)
        
        # 处理输入：图片 + 我们定义的文本标签
        # padding=True, truncation=True 是为了处理文本长度
        inputs = processor(
            text=english_labels, 
            images=img, 
            return_tensors="pt", 
            padding=True
        )

        with torch.no_grad():
            outputs = model(**inputs)
        
        # 计算图片和每个文本标签的相似度 (logits_per_image)
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1) # 转化为概率百分比

        # 获取概率最高的 3 个标签
        values, indices = torch.topk(probs, 3)
        
        suggested_tags = []
        for i in range(3):
            idx = indices[0][i].item()
            score = values[0][i].item()
            
            # 只有置信度大于 10% 才展示，避免瞎猜
            if score > 0.1: 
                en_tag = english_labels[idx]
                cn_tag = CANDIDATE_LABELS[en_tag]
                suggested_tags.append(cn_tag)

        # 如果匹配度都很低，返回一个通用标签
        if not suggested_tags:
            return ["其他"]

        return suggested_tags

    except Exception as e:
        print(f"CLIP 分析出错: {e}")
        return []