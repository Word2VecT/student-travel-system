import sys
import torch
from diffusers import (
    StableDiffusionXLPipeline,
    KDPM2AncestralDiscreteScheduler,
    AutoencoderKL,
)

UPLOAD_FOLDER = "/Users/tang/Pictures/travel"  # 确保此路径与 app.py 中一致

# 获取命令行参数作为生成图片的 prompt
if len(sys.argv) > 1:
    prompt = sys.argv[1]
else:
    prompt = "Default prompt"  # 默认提示词

# Load VAE component
vae = AutoencoderKL.from_pretrained(
    "madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16
)

# Configure the pipeline
pipe = StableDiffusionXLPipeline.from_pretrained(
    "Corcelio/mobius", vae=vae, torch_dtype=torch.float16
)
pipe.scheduler = KDPM2AncestralDiscreteScheduler.from_config(pipe.scheduler.config)
pipe.to("cuda")

# Define prompts and generate image
negative_prompt = ""

image = pipe(
    prompt,
    negative_prompt=negative_prompt,
    width=1024,
    height=1024,
    guidance_scale=4,
    num_inference_steps=50,
    clip_skip=3,
).images[0]

image.save(f"{UPLOAD_FOLDER}/generated_image.png")
