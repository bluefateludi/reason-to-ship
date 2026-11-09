"""Render the bilingual README workflow PNGs with Pillow and Windows fonts."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "workflow"
INK = "#203C35"
MUTED = "#596D63"
GREEN = "#DDEEAE"
FONT = Path("C:/Windows/Fonts/msyh.ttc")
BOLD = Path("C:/Windows/Fonts/msyhbd.ttc")

COPY = {
    "zh-CN": {
        "title": "从项目问题，到有依据的交付",
        "subtitle": "Reason to Ship 如何陪你设计、实现，并接着做下去",
        "nodes": [
            ("带着真实任务开始", ["说清目标、约束与初步想法"]),
            ("了解你和项目", ["检查代码与已有上下文", "按当前主题的经验调整解释"]),
            ("一起确定方案", ["一次讨论一个关键决策", "你来决定取舍与实施范围"]),
            ("实现约定的改动", ["在已授权范围内辅助编码", "跟进异常与失败边界"]),
            ("用证据验证", ["运行相关测试，检查结果", "未解决的问题继续迭代"]),
            ("同意后保存上下文", ["偏好、学习证据、项目方案", "分别记录，并保留未决事项"]),
        ],
        "center": "你掌握决定，AI 陪你推进",
        "detail": "重要决策一起讨论，日常小改动继续推进",
        "return": ["下次任务", "接着做"],
        "forward": ["确定范围", "开始实现"],
        "foot": "学习证据区分自述经验与实际表现  ·  恢复上下文时核实项目现状",
    },
    "en": {
        "title": "From a project question to evidence",
        "subtitle": "How Reason to Ship supports design, implementation and continuity",
        "nodes": [
            ("Start with a real task", ["Share goals, constraints", "and your initial idea"]),
            ("Understand the context", ["Inspect code and saved notes", "Adapt to your topic experience"]),
            ("Decide together", ["Discuss one key decision", "You own tradeoffs and scope"]),
            ("Implement the plan", ["Help code within agreed scope", "Consider failure boundaries"]),
            ("Verify with evidence", ["Run relevant tests and inspect", "Iterate on unresolved issues"]),
            ("Save with consent", ["Preferences, learning evidence", "Project decisions and open items"]),
        ],
        "center": "Your decisions. AI alongside.",
        "detail": "Discuss key choices and keep everyday work moving",
        "return": ["Next task", "Resume"],
        "forward": ["Agree scope", "Implement"],
        "foot": "Separate self-report from observed reasoning  ·  Recheck project facts when resuming",
    },
}


def font(size, bold=False):
    return ImageFont.truetype(str(BOLD if bold else FONT), size)


def centered(draw, text, x, y, size, fill=INK, bold=False):
    face = font(size, bold)
    width = draw.textlength(text, font=face)
    draw.text((x-width/2, y), text, font=face, fill=fill)


def arrow(draw, start, end):
    draw.line((start, end), fill=INK, width=4)
    x, y = end
    dx, dy = end[0]-start[0], end[1]-start[1]
    if dx:
        direction = 1 if dx > 0 else -1
        points = [(x, y), (x-13*direction, y-7), (x-13*direction, y+7)]
    else:
        direction = 1 if dy > 0 else -1
        points = [(x, y), (x-7, y-13*direction), (x+7, y-13*direction)]
    draw.polygon(points, fill=INK)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    positions = [(70, 210), (560, 210), (1050, 210),
                 (1050, 630), (560, 630), (70, 630)]
    for lang, copy in COPY.items():
        image = Image.new("RGB", (1440, 960), "#F5F4ED")
        draw = ImageDraw.Draw(image)
        draw.text((70, 28), "REASON TO SHIP", font=font(22, True), fill=INK)
        draw.line((70, 77, 1370, 77), fill="#CED6C8", width=2)
        draw.text((70, 96), copy["title"], font=font(42, True), fill=INK)
        draw.text((70, 159), copy["subtitle"], font=font(23), fill=MUTED)
        for i, ((x, y), (title, lines)) in enumerate(zip(positions, copy["nodes"])):
            draw.rounded_rectangle((x, y, x+320, y+180), radius=18,
                                   fill=GREEN if i in (2, 5) else "#FFFFFF",
                                   outline="#CED6C8", width=2)
            draw.text((x+23, y+15), f"0{i+1}", font=font(20, True), fill=MUTED)
            title_size = 25
            while draw.textlength(title, font=font(title_size, True)) > 276:
                title_size -= 1
            draw.text((x+23, y+53), title, font=font(title_size, True), fill=INK)
            body_size = 20
            while max(draw.textlength(line, font=font(body_size)) for line in lines) > 274:
                body_size -= 1
            for line_index, line in enumerate(lines):
                draw.text((x+23, y+101+line_index*30), line, font=font(body_size), fill=MUTED)
        for x in (390, 880):
            arrow(draw, (x+16, 300), (x+154, 300))
        arrow(draw, (1210, 407), (1210, 613))
        for x in (1050, 560):
            arrow(draw, (x-16, 720), (x-154, 720))
        arrow(draw, (230, 613), (230, 407))
        for x, key in [(230, "return"), (1210, "forward")]:
            draw.rounded_rectangle((x-90, 474, x+90, 548), radius=8, fill="#F5F4ED")
            for j, line in enumerate(copy[key]):
                centered(draw, line, x, 481+j*28, 20, MUTED)
        centered(draw, copy["center"], 720, 465, 29, bold=True)
        centered(draw, copy["detail"], 720, 516, 21, MUTED)
        draw.line((70, 868, 1370, 868), fill="#CED6C8", width=2)
        centered(draw, copy["foot"], 720, 893, 22, MUTED)
        path = OUT / f"learning-cycle.{lang}.png"
        image.save(path, optimize=True)
        print(f"{path.name} / {path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
