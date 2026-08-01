from pathlib import Path
import time
import logging

from swin2sr_engine import Swin2SREngine


BASE = Path(__file__).parent


INPUT_DIR = BASE / "input_images"
OUTPUT_DIR = BASE / "output_images"
LOG_DIR = BASE / "logs"


MODEL = (
    BASE
    / "swin2sr-main"
    / "models"
    / "Swin2SR_RealworldSR_X4_64_BSRGAN_PSNR.pth"
)


SUPPORTED = [
    ".png",
    ".jpg",
    ".jpeg",
    ".webp"
]


INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)


logging.basicConfig(
    filename=LOG_DIR / "swin2sr.log",
    level=logging.INFO,
    format="%(asctime)s %(message)s"
)



def process_image(engine, image):

    output = (
        OUTPUT_DIR
        /
        f"{image.stem}_Swin2SR.png"
    )


    if output.exists():
        return


    start = time.time()


    try:

        engine.process(
            image,
            output
        )


        elapsed = time.time() - start


        logging.info(
            "%s %.2fs",
            image.name,
            elapsed
        )


        print(
            f"✓ {image.name}  ({elapsed:.2f}s)"
        )


    except Exception as e:

        logging.exception(e)

        print(
            "FAILED:",
            image.name,
            e
        )



def main():

    print("==============================")
    print(" Swin2SR MPS Image Engine")
    print("==============================")


    engine = Swin2SREngine(
        MODEL
    )


    print("Watching:")
    print(INPUT_DIR)
    print("")


    processed = set()


    while True:


        images = [
            x for x in INPUT_DIR.iterdir()
            if x.suffix.lower() in SUPPORTED
        ]


        for image in images:

            if image not in processed:

                # wait until file copy finishes
                old_size = -1

                while True:
                    new_size = image.stat().st_size

                    if new_size == old_size:
                        break

                    old_size = new_size
                    time.sleep(0.5)


                process_image(
                    engine,
                    image
                )


                processed.add(image)


        time.sleep(1)



if __name__ == "__main__":
    main()