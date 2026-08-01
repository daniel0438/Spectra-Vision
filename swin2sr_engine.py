import torch
import cv2
import numpy as np
from pathlib import Path
import sys


# point to official Swin2SR source
SWIN_ROOT = Path(__file__).parent / "swin2sr-main"
sys.path.insert(0, str(SWIN_ROOT))

from models.network_swin2sr import Swin2SR


class Swin2SREngine:

    def __init__(self, model_path):

        self.device = torch.device(
            "mps"
            if torch.backends.mps.is_available()
            else "cpu"
        )

        print(f"[Swin2SR] Device: {self.device}")


        self.model = Swin2SR(
            upscale=4,
            in_chans=3,
            img_size=64,
            window_size=8,
            img_range=1.,
            depths=[6,6,6,6,6,6],
            embed_dim=180,
            num_heads=[6,6,6,6,6,6],
            mlp_ratio=2,
            upsampler="nearest+conv",
            resi_connection="1conv"
        )


        print("[Swin2SR] Loading weights...")

        checkpoint = torch.load(
            model_path,
            map_location="cpu"
        )


        if "params_ema" in checkpoint:
            weights = checkpoint["params_ema"]
        elif "params" in checkpoint:
            weights = checkpoint["params"]
        else:
            weights = checkpoint


        self.model.load_state_dict(
            weights,
            strict=True
        )


        self.model.eval()

        self.model.to(self.device)


        print("[Swin2SR] Ready")



    @torch.inference_mode()
    def process(
        self,
        input_file,
        output_file
    ):

        print(
            f"[Swin2SR] Processing {input_file.name}"
        )


        img = cv2.imread(
            str(input_file),
            cv2.IMREAD_COLOR
        )


        if img is None:
            raise RuntimeError(
                f"Cannot read {input_file}"
            )


        img = cv2.cvtColor(
            img,
            cv2.COLOR_BGR2RGB
        )


        img = (
            img.astype(np.float32)
            / 255.0
        )


        img = np.transpose(
            img,
            (2,0,1)
        )


        tensor = torch.from_numpy(
            img
        ).unsqueeze(0)


        tensor = tensor.to(
            self.device
        )


        result = self.model(
            tensor
        )


        result = (
            result.squeeze(0)
            .clamp(0,1)
            .cpu()
            .numpy()
        )


        result = np.transpose(
            result,
            (1,2,0)
        )


        result = (
            result[:,:,::-1]
            *255
        ).astype(
            np.uint8
        )


        cv2.imwrite(
            str(output_file),
            result
        )


        print(
            f"[Swin2SR] Saved {output_file}"
        )
