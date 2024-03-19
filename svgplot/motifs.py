import numpy as np
from .axis import Axis
from .svgfigure import SVGFigure
import re
from enum import Enum
import pandas as pd
import svgplot

# https://bioconductor.org/packages/release/bioc/vignettes/universalmotif/inst/doc/IntroductionToSequenceMotifs.pdf

BASE_IDS = {0: "A", 1: "C", 2: "G", 3: "T"}
BASE_COLORS = {
    "A": "mediumseagreen",
    "G": "orange",
    "C": "royalblue",
    "T": "red",
    "-": "black",
}

# tweak letters to appear the same height
Y_SCALE_FACTORS = {"A": 1.02, "C": 1, "G": 1, "T": 1.02}
H = 100

# scale around this letter size
LW = 48

IC_TOTAL = 2


class Mode(Enum):
    PROB = 0
    BITS = 1

    def __str__(self):
        return str(self.name)


class TitlePos(Enum):
    NONE = 0
    TOP = 1
    RIGHT = 2


def add_homer_motifs_by_range(
    svg: SVGFigure,
    ids: list[int],
    mode: Mode = Mode.BITS,
    rev_comp=False,
    pos: tuple[int, int] = (0, 0),
    height: int = 100,
    letter_width: int = 48,
    title_pos=TitlePos.TOP,
    offset=220,
    prefix="motif",
):
    x, y = pos
    y1 = y

    for i in ids:
        add_homer_motif(
            svg,
            f"{prefix}{i}.motif",
            mode=mode,
            rev_comp=rev_comp,
            pos=(x, y1),
            height=height,
            letter_width=letter_width,
            title_pos=title_pos,
        )
        y1 += offset


def parse_homer_motifs(file: str, rev_comp: bool = False):
    motifs = []
    bases = []
    name = ""
    score = -1

    print(file)

    with open(file, "r") as f:
        for line in f:
            line = line.rstrip()

            if line.startswith(">"):
                if len(bases) > 0:
                    print(file, name)
                    df = pd.DataFrame(bases, columns=["a", "c", "g", "t"])
                    if rev_comp:
                        dfrc = pd.DataFrame()
                        dfrc["a"] = df.iloc[:, 3].values
                        dfrc["c"] = df.iloc[:, 2].values
                        dfrc["g"] = df.iloc[:, 1].values
                        dfrc["t"] = df.iloc[:, 0].values
                        df = dfrc

                    motifs.append([name, score, df])
                    bases = []

                tokens = line[1:].split("\t")
                name = re.sub(r"^.+BestGuess:", "", tokens[1])
                score = float(tokens[2])
            else:
                bases.append([float(x) for x in line.split("\t")])

    # add the last motif
    df = pd.DataFrame(bases, columns=["a", "c", "g", "t"])

    if rev_comp:
        dfrc = pd.DataFrame()
        dfrc["a"] = df.iloc[:, 3].values[::-1]
        dfrc["c"] = df.iloc[:, 2].values[::-1]
        dfrc["g"] = df.iloc[:, 1].values[::-1]
        dfrc["t"] = df.iloc[:, 0].values[::-1]
        df = dfrc

    motifs.append([name, score, df])

    return motifs


def add_homer_motif(
    svg: SVGFigure,
    file: str,
    mode: Mode = Mode.PROB,
    rev_comp=False,
    pos: tuple[int, int] = (0, 0),
    height: int = 100,
    title_pos=TitlePos.TOP,
    letter_width: int = 48,
    gap: int = 50,
):
    motifs = parse_homer_motifs(file, rev_comp)

    add_homer_motifs(
        svg, motifs, mode, rev_comp, pos, height, title_pos, letter_width, gap
    )


def add_homer_motifs(
    svg: SVGFigure,
    motifs: list,
    mode: Mode = Mode.PROB,
    rev_comp=False,
    pos: tuple[int, int] = (0, 0),
    height: int = 100,
    title_pos=TitlePos.TOP,
    letter_width: int = 48,
    gap: int = 50,
):
    x, y = pos

    x_scale_factor = letter_width / LW
    y_scale_factor = height / H

    rc = 1

    bases = []

    y1 = y

    for motif in motifs:
        name = motif[0]
        df = motif[2]
        df = df.div(df.sum(axis=1), axis=0)

        #print(name)
        #print(df)

        x1 = x

        w = letter_width * df.shape[0]

        if title_pos == TitlePos.TOP:
            svg.add_text_bb(
                name, x=x + letter_width * df.shape[0] / 2, y=y1 - 30, align="c"
            )
        elif title_pos == TitlePos.RIGHT:
            svg.add_text_bb(name, x=x + w + 50, y=y1 + height / 2)
        else:
            pass

        svgplot.add_x_axis(
            svg,
            pos=(x1, y1 + height),
            axis=svgplot.Axis(
                lim=[0, df.shape[0]],
                ticks=[x + 0.5 for x in range(df.shape[0])],
                ticklabels=[x + 1 for x in range(df.shape[0])],
                w=letter_width * df.shape[0],
            ),
        )

        if mode == Mode.BITS:
            svgplot.add_y_axis(
                svg,
                pos=(x1, y1),
                axis=svgplot.Axis(lim=[0, 2], ticks=[0, 2], w=height, label="Bits"),
                title_offset=60,
            )
        else:
            svgplot.add_y_axis(
                svg,
                pos=(x1, y1),
                axis=svgplot.Axis(lim=[0, 1], ticks=[0, 1], w=height, label="Prob"),
                title_offset=60,
            )

        for r in range(df.shape[0]):
            idx = np.argsort(df.iloc[r, :])  # np.argmax(df.iloc[i, :])

            if mode == Mode.BITS:
                U = 0
                for c in idx:
                    p = df.iloc[r, c]  # 1 if c == r else 0 #
                    if p > 0:
                        U += p * np.log2(p)

                U = -U

                ic_final = IC_TOTAL - U
            else:
                ic_final = IC_TOTAL

            ic_frac = ic_final / IC_TOTAL

            y2 = y1 + height
            y3 = y2

            for c in idx:
                base = BASE_IDS[c]
                color = BASE_COLORS[base]
                p = df.iloc[r, c]  # 1 if c == r else 0

                y_scale = p * 2 * ic_frac * y_scale_factor * Y_SCALE_FACTORS[base]
                h = p * ic_frac * height
                t = svg.text(
                    base,
                    weight="bold",
                    css={"fill": color, "font-size": "70"},
                    baseline="auto",
                )
                t = svg.scale(t, x=x_scale_factor, y=y_scale)
                t = svg.trans(t, x=x1, y=y3)
                svg.add(t)

                y3 -= h

            x1 += letter_width

        y1 += 2 * height
