import os

from ImageReader import ImageReader
from ImageSegmenter import ImageSegmenter
from ImageStacker_OrthoOverlay import ImageStackerOrthoOverlay


class Scripts:
    def __init__(self):
        self.targets = input("输入目标图像文件夹路径:")
        self.overlays = input("输入覆盖图像文件夹路径:")
        self.savePath = input("输入保存路径:")

        self.targetImages = []
        self.overlayImages = []

        self._readImages()

    def _readImages(self):
        self.targetImages = ImageReader(self.targets).images
        self.overlayImages = ImageReader(self.overlays).images

    def process_images(self):
        """根据逻辑对图像进行分割、叠加并保存结果。"""
        for overlay_path in self.overlayImages:
            # 获取覆盖图像名称及其对应的 mcmeta 文件名称
            overlay_name = os.path.basename(overlay_path).replace(".png", "")
            overlay_mcmeta = overlay_name + ".png.mcmeta"

            # 读取 mcmeta 文件内容（如果存在）
            overlay_mcmeta_path = os.path.join(os.path.dirname(overlay_path), overlay_mcmeta)
            print(f"读取 mcmeta 文件: {overlay_mcmeta_path}")
            overlay_mcmeta_str = ""
            if os.path.exists(overlay_mcmeta_path):
                try:
                    with open(overlay_mcmeta_path, "r", encoding="utf-8") as mcmeta_file:
                        overlay_mcmeta_str = mcmeta_file.read()
                except Exception as e:
                    print(f"警告：读取 mcmeta 文件失败: {overlay_mcmeta_path}, 错误: {e}")

            # 创建覆盖图像对应的保存文件夹
            overlay_save_dir = os.path.join(self.savePath, overlay_name)
            os.makedirs(overlay_save_dir, exist_ok=True)

            for target_path in self.targetImages:
                # 分割覆盖图像
                overlay_segments = ImageSegmenter(overlay_path).images
                target_name = os.path.basename(target_path)

                # 分割目标图像
                target_segments = ImageSegmenter(target_path).images

                # 合成图像
                stacker = ImageStackerOrthoOverlay(overlay_segments, target_segments)
                stacker.apply_overlay_to_bottoms()
                stacker.merge_bottoms_vertically()

                # 保存合成结果图像
                result_path = os.path.join(overlay_save_dir, f"{target_name}")
                try:
                    stacker.result.save(result_path)
                    print(f"保存合成图像到: {result_path}")
                except Exception as e:
                    print(f"警告: 错误：保存合成图像失败: {result_path}, 错误: {e}")

                # 处理 mcmeta 文件
                target_mcmeta_path = os.path.join(overlay_save_dir, f"{target_name}.mcmeta")
                if overlay_mcmeta_str:  # 如果有 mcmeta 内容
                    try:
                        with open(target_mcmeta_path, "w", encoding="utf-8") as mcmeta_file:
                            mcmeta_file.write(overlay_mcmeta_str)
                        print(f"保存 mcmeta 文件到: {target_mcmeta_path}")
                    except Exception as e:
                        print(f"警告: 错误：保存 mcmeta 文件失败: {target_mcmeta_path}, 错误: {e}")
                else:
                    print(f"警告：未找到或读取 mcmeta 文件，跳过生成 {target_mcmeta_path}")


if __name__ == "__main__":
    scripts = Scripts()
    scripts.process_images()