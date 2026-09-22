from pathlib import Path
from PIL import Image, ImageChops, ImageFilter
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "高清题图"
OUT.mkdir(exist_ok=True)

# 这些文件一张图里有两道题，拆开后在 README 中能以接近原始像素大小显示。
SPLIT_FILES = {
    "00-基础/01-第K大元素_合并两个有序数组.webp",
    "00-基础/02-排序_二分查找.webp",
    "01-哈希/01-两数之和_最长连续序列.webp",
    "01-哈希/02-TopK高频元素_字母异位词分组.webp",
    "02-双指针/01-移动零_三数之和.webp",
    "02-双指针/02-盛最多水的容器_接雨水.webp",
    "03-滑动窗口/02-无重复字符最长子串_找到所有字母异位词.webp",
    "04-子串/01-和为K的子数组_滑动窗口最大值.webp",
    "05-数组/01-最大子数组和_合并区间.webp",
    "05-数组/03-除自身以外数组乘积_缺失的第一个正数.webp",
}

ORDER = [
    "00-基础/01-第K大元素_合并两个有序数组.webp",
    "00-基础/02-排序_二分查找.webp",
    "00-基础/03-LRU-Cache.webp",
    "01-哈希/01-两数之和_最长连续序列.webp",
    "01-哈希/02-TopK高频元素_字母异位词分组.webp",
    "02-双指针/01-移动零_三数之和.webp",
    "02-双指针/02-盛最多水的容器_接雨水.webp",
    "03-滑动窗口/01-滑动窗口最大值.webp",
    "03-滑动窗口/02-无重复字符最长子串_找到所有字母异位词.webp",
    "04-子串/01-和为K的子数组_滑动窗口最大值.webp",
    "04-子串/02-最小覆盖子串.webp",
    "05-数组/01-最大子数组和_合并区间.webp",
    "05-数组/02-轮转数组.webp",
    "05-数组/03-除自身以外数组乘积_缺失的第一个正数.webp",
    "06-链表/01-反转链表.webp",
    "06-链表/02-合并两个有序链表.webp",
    "06-链表/03-删除链表倒数第N个节点.webp",
    "06-链表/04-环形链表.webp",
    "06-链表/05-环形链表II.webp",
    "06-链表/06-相交链表.webp",
    "06-链表/07-回文链表.webp",
    "06-链表/08-两两交换链表中的节点.webp",
    "07-BFS-DFS/01-二叉树层序遍历-BFS.webp",
    "07-BFS-DFS/02-岛屿数量-DFS.webp",
    "08-二叉树/01-二叉树最大深度.webp",
    "08-二叉树/02-二叉树前中后序遍历.webp",
    "09-栈/01-有效括号.webp",
    "09-栈/02-字符串解码.webp",
    "10-DP/01-爬楼梯.webp",
    "10-DP/02-最长递增子序列-LIS.webp",
]

def trim_white(im, threshold=247, pad=16):
    im = im.convert("RGB")
    # 找到非白色内容区域，去掉 PPT 导出后无意义的大块白边。
    gray = im.convert("L")
    mask = gray.point(lambda p: 255 if p < threshold else 0)
    box = mask.getbbox()
    if not box:
        return im
    l, t, r, b = box
    l = max(0, l - pad)
    t = max(0, t - pad)
    r = min(im.width, r + pad)
    b = min(im.height, b + pad)
    return im.crop((l, t, r, b))

def enhance(im):
    im = trim_white(im)
    # 小图放大到至少 1500px 宽，再轻微锐化；PNG 无二次有损压缩。
    if im.width < 1500:
        scale = 1500 / im.width
        im = im.resize((1500, round(im.height * scale)), Image.Resampling.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(radius=1.1, percent=125, threshold=2))

generated = []
for rel in ORDER:
    src = ROOT / rel
    if not src.exists():
        print("missing:", rel)
        continue
    im = Image.open(src).convert("RGB")
    stem = Path(rel).stem
    cat = Path(rel).parent.name
    cat_dir = OUT / cat
    cat_dir.mkdir(parents=True, exist_ok=True)

    if rel in SPLIT_FILES:
        # 中缝附近留一点重叠，避免恰好切掉边缘文字。
        mid = im.width // 2
        parts = [
            ("A", im.crop((0, 0, min(im.width, mid + 24), im.height))),
            ("B", im.crop((max(0, mid - 24), 0, im.width, im.height))),
        ]
    else:
        parts = [("", im)]

    for suffix, part in parts:
        hd = enhance(part)
        name = stem + (f"-{suffix}" if suffix else "") + ".png"
        dst = cat_dir / name
        hd.save(dst, "PNG", optimize=True)
        generated.append(dst.relative_to(ROOT).as_posix())

# 生成高清 README：不再把两道题挤在同一行；每张裁剪图单独占满宽度。
groups = {}
for p in generated:
    parts = Path(p).parts
    cat = parts[1]
    groups.setdefault(cat, []).append(p)

lines = [
    "# 华为高频手撕题总结｜高清阅读版",
    "",
    "> 这一版专门针对 GitHub README 阅读做了处理：**去白边、双题拆分、放大、轻锐化、PNG 无损输出**。  ",
    "> 不再把一张 16:9 大图硬缩到 README 宽度里，所以代码和中文小字会明显大很多。",
    "",
    "## 📥 PDF 下载",
    "",
    "- [高清阅读版 PDF（全部题目）](./下载/华为高频手撕题-高清阅读版.pdf)",
    "",
    "## 📚 题目",
    "",
]
for cat in sorted(groups):
    lines += [f"### {cat}", ""]
    for p in groups[cat]:
        title = Path(p).stem
        lines += [f"#### {title}", "", f"![{title}](./{p})", ""]
lines += [
    "---",
    "",
    "如果浏览器仍把图片缩小，可点击图片进入文件页，再点开原图；仓库内生成文件为 PNG。",
]
(ROOT / "README.md").write_text("\n".join(lines), encoding="utf-8")

# 生成可下载 PDF。按生成后的高清题图顺序，一张题图一页。
pdf_dir = ROOT / "下载"
pdf_dir.mkdir(exist_ok=True)
pages = []
for p in generated:
    im = Image.open(ROOT / p).convert("RGB")
    # PDF 页面按图片自身比例，避免再次缩放导致小字变细。
    pages.append(im)
if pages:
    pages[0].save(
        pdf_dir / "华为高频手撕题-高清阅读版.pdf",
        "PDF",
        resolution=150.0,
        save_all=True,
        append_images=pages[1:],
    )
print(f"generated {len(generated)} PNGs")
