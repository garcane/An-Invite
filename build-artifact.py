"""Build artifact.html: index.html with every photo inlined as a data URI.

A published artifact is a single HTML file served under a strict CSP, so
relative paths like imgs/web/g-01.jpg have nothing to resolve against.
Inlining is the only way the shared link shows photos.

Inlined copies are re-encoded smaller than the ones index.html links to —
base64 costs ~33% on top, and this all has to arrive in one response.
"""
import base64
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
from PIL import Image

# max width, jpeg quality — smaller than the linked assets on purpose
PROFILE = {"park-plaza": (1200, 70), "ivy-asia": (1200, 70)}
GALLERY_DEFAULT = (760, 68)


def encode(path):
    name = os.path.splitext(os.path.basename(path))[0]
    max_w, quality = PROFILE.get(name, GALLERY_DEFAULT)
    im = Image.open(path)
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    raw = buf.getvalue()
    return "data:image/jpeg;base64," + base64.b64encode(raw).decode("ascii"), len(raw)


def main():
    html = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
    total = 0
    count = 0

    def sub(match):
        nonlocal total, count
        rel = match.group(1)
        path = os.path.join(HERE, rel.replace("/", os.sep))
        if not os.path.exists(path):
            raise SystemExit("missing image: " + rel)
        uri, size = encode(path)
        total += size
        count += 1
        return 'src="' + uri + '"'

    out = re.sub(r'src="(imgs/[^"]+)"', sub, html)

    if 'src="imgs/' in out:
        raise SystemExit("some image refs were not inlined")

    dest = os.path.join(HERE, "artifact.html")
    open(dest, "w", encoding="utf-8").write(out)
    print("inlined %d images (%.2fMB of jpeg)" % (count, total / 1048576))
    print("artifact.html: %.2fMB" % (os.path.getsize(dest) / 1048576))


if __name__ == "__main__":
    main()
