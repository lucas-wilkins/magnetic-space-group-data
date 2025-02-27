import re

from msgmodels.groups import MagneticSpaceGroupData

def latex_format_symbol(raw_text):
    """ Format a symbol using latex notation"""
    # Find the lattice system part

    if raw_text[1] == "_":
        lattice_system = raw_text[:3]
        rest = raw_text[3:]

        if lattice_system[-1] in "123456789" and rest[0] in "abcs":
            lattice_system = lattice_system[:2] + "{" + lattice_system[2:] + rest[0] + "}"
            rest = rest[1:]

    else:
        lattice_system = raw_text[:1]
        rest = raw_text[1:]

    rest = re.sub(r"-(.)", r"\\bar{\1}", rest)

    if rest.endswith("]"):
        # We've got a subscript part
        parts = re.split(r"_*\[", rest)

        rest = parts[0][:-2]
        subscript = parts[0][-1:] + "[" + parts[1]

        subscript = "_{" + subscript + "}"

    else:
        subscript = ""


    latex_string = lattice_system + " " + rest + subscript


    return latex_string

latex_format_uni_symbol = latex_format_symbol
latex_format_bns_symbol = latex_format_symbol
latex_format_og_symbol = latex_format_symbol

def latex_dump(data: MagneticSpaceGroupData, filename: str):
    """
    Create a tex file with all the group names
    """

    preamble = r"""
    \documentclass[10pt]{article}
    \usepackage{longtable}
    \usepackage{lscape}
    
    \title{Latex Formatting of Magnetic Space Groups}
    
    \begin{document}
    
    \maketitle
    
    \begin{landscape}
    \begin{longtable}{c|cc|cc|cc}
      Number & UNI & & BNS & & OG & \\
      \hline
    """

    end = """\end{longtable}
    \end{landscape}
    \end{document}
    """

    with open(filename, 'w') as file:
        file.write(preamble)

        for group in data.groups:
            parts = [
                str(group.number),
                r"\verb|" + group.symbol + "|",
                "$"+group.latex_symbol+"$",
                r"\verb|" + group.bns.symbol + "|",
                "$"+group.bns.latex_symbol+"$",
                r"\verb|" + group.og.symbol + "|",
                "$"+group.og.latex_symbol+"$"]

            file.write(" & ".join(parts))
            file.write("\\\\\n")

        file.write(end)