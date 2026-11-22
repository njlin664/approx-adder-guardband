# blur.py - Day 16: a 5x5 image blur whose additions are done by YOUR approximate adders.
# Run with:  python3 blur.py        (self-test: checks the exact adder and the PSNR function)
# Other scripts import it:  from blur import load_images, blur, psnr
import numpy as np
from skimage import data
from skimage.color import rgb2gray
from skimage.util import img_as_ubyte
from golden import exact, trua, loa, esa, etaii

# 5x5 binomial kernel: the outer product of [1 4 6 4 1] with itself. The 25 weights add up
# to 256, so "multiply, add all 25, then shift right by 8" is a weighted average.
ROW = np.array([1, 4, 6, 4, 1])
KERNEL = np.outer(ROW, ROW)                      # 25 whole-number weights, total 256

# Ten standard test images that ship with scikit-image (the paper also used ten images).
IMAGE_NAMES = ["camera", "astronaut", "coins", "moon", "page",
               "chelsea", "coffee", "rocket", "brick", "grass"]

ADDERS = {"exact": lambda a, b, k: exact(a, b), "trua": trua, "loa": loa, "esa": esa,
          "etaii": etaii}                                    # ETAII added on Day 19


def load_images():
    """Return {name: 8-bit grayscale image} for the ten test images."""
    images = {}
    for name in IMAGE_NAMES:
        img = getattr(data, name)()
        if img.ndim == 3:                         # colour image: convert to gray
            img = img_as_ubyte(rgb2gray(img))
        images[name] = img.astype(np.int64)
    return images


def blur(img, design="exact", k=0):
    """Blur one image. Every one of the 24 additions per pixel goes through the chosen
    16-bit adder (design = exact, trua, loa, esa or etaii, with parameter k)."""
    add = ADDERS[design]
    h, w = img.shape
    padded = np.pad(img, 2, mode="edge")          # repeat the border pixels
    acc = np.zeros((h, w), dtype=np.int64)        # the 16-bit accumulator, one per pixel
    for dy in range(5):
        for dx in range(5):
            product = KERNEL[dy, dx] * padded[dy:dy + h, dx:dx + w]   # at most 36 x 255 = 9180
            acc = add(acc, product, k)            # the approximate addition happens here
            acc = np.minimum(acc, 0xFFFF)         # a 16-bit register cannot hold more
    return np.minimum(acc >> 8, 255)              # divide by 256, back to 0..255


def psnr(reference, test):
    """Peak signal-to-noise ratio in dB. Higher is better; identical images give infinity."""
    mse = np.mean((reference.astype(np.float64) - test.astype(np.float64)) ** 2)
    if mse == 0:
        return float("inf")
    return 10 * np.log10(255.0 ** 2 / mse)


if __name__ == "__main__":
    images = load_images()
    for name, img in images.items():
        print(f"{name:<10} {img.shape[1]:4d} x {img.shape[0]:<4d} pixels")

    # Test 1: with the exact adder, blur() must equal the textbook convolution.
    img = images["camera"]
    padded = np.pad(img, 2, mode="edge")
    h, w = img.shape
    reference = sum(KERNEL[dy, dx] * padded[dy:dy + h, dx:dx + w]
                    for dy in range(5) for dx in range(5)) >> 8
    assert np.array_equal(blur(img, "exact"), reference), "exact blur is wrong"
    print("test 1 passed: the exact adder reproduces the exact blur")

    # Test 2: PSNR of an image with itself is infinite; a known error gives a known value.
    assert psnr(img, img) == float("inf")
    off_by_one = np.minimum(img + 1, 255)         # every pixel 1 too bright (except 255s)
    print(f"test 2: PSNR(identical) = inf, PSNR(off by one) = {psnr(img, off_by_one):.2f} dB (about 48)")
    assert 47.5 < psnr(img, off_by_one) < 48.2
    print("ALL BLUR TESTS PASSED")
