"""Resize + compress source photos into web-ready assets in imgs/web/.

Originals are 2-4MB phone photos; shipping those to a mobile browser would
make the page crawl. Everything here is re-encoded at display size, EXIF
rotation baked in (and the EXIF block dropped so orientation can't be
applied twice), and cropped to the aspect ratio its frame actually uses.
"""
import os
from PIL import Image, ImageOps

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs")
OUT = os.path.join(SRC, "web")
os.makedirs(OUT, exist_ok=True)

# name -> (source file, output size, vertical centering)
# centering y: 0.0 keeps the top of the frame, 1.0 keeps the bottom.
# Portraits sit at 0.30 so faces stay clear of the caption gradient.
JOBS = {
    "park-plaza":  ("Park16256-114930-f65955407_3XL_upscayl_1x_upscayl-standard-4x.jpg", (1760, 1100), 0.50),
    # crop low: the green onyx floor is the room's signature, worth more
    # than the top of the blossom canopy
    "ivy-asia":    ("IVYdownload_upscayl_3x_upscayl-standard-4x.jpg",                    (1760, 1100), 0.70),

    "g-01": ("IMG_3618.JPG",                                 (900, 1125), 0.28),
    "g-02": ("20260605_185347.jpg",                          (900, 1125), 0.30),
    "g-03": ("100_0724.jpg",                                 (900, 1125), 0.30),
    "g-04": ("IMG_4537.JPG",                                 (900, 1125), 0.50),
    "g-05": ("IMG_9835.jpg",                                 (900, 1125), 0.30),
    "g-06": ("20260605_122745.jpg",                          (900, 1125), 0.32),
    "g-07": ("IMG_5267.jpg",                                 (900, 1125), 0.28),
    "g-08": ("IMG_1240.jpg",                                 (900, 1125), 0.30),
    "g-09": ("IMG_1260.jpg",                                 (900, 1125), 0.30),
    "g-10": ("100_0651.jpg",                                 (900, 1125), 0.30),
    "g-11": ("80c3bacc-a810-448a-b32d-53b1d26da198.JPG",     (900, 1125), 0.22),
    "g-12": ("100_0821.JPG",                                 (900, 1125), 0.30),
    # g-12.jpg is deliberately absent: its source (100_0821.JPG) is landscape
    # and was hand-cropped to portrait. Re-deriving it here would replace that
    # crop with a centred one and lose the framing.
}

total_before = total_after = 0
for name, (src, size, cy) in JOBS.items():
    path = os.path.join(SRC, src)
    before = os.path.getsize(path)
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    im = ImageOps.fit(im, size, method=Image.LANCZOS, centering=(0.5, cy))
    dest = os.path.join(OUT, name + ".jpg")
    im.save(dest, "JPEG", quality=78, optimize=True, progressive=True)
    after = os.path.getsize(dest)
    total_before += before
    total_after += after
    print("%-12s %-52s %7.0fKB -> %5.0fKB" % (name, src, before / 1024, after / 1024))

print("\ntotal %.1fMB -> %.2fMB" % (total_before / 1048576, total_after / 1048576))
