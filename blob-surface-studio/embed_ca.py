"""Embed the Cα trace of a PDB file into index.html so the page opens without a file.

    python3 embed_ca.py 4F5S.pdb

Keeps the first model, the first chain, and altloc blank/A, like the page's own parser.
"""
import json
import pathlib
import re
import sys

AA = dict(ALA="A", ARG="R", ASN="N", ASP="D", CYS="C", GLN="Q", GLU="E", GLY="G", HIS="H", ILE="I",
          LEU="L", LYS="K", MET="M", PHE="F", PRO="P", SER="S", THR="T", TRP="W", TYR="Y", VAL="V")

out, chain = [], None
for line in open(sys.argv[1]):
    if line.startswith("ENDMDL") and out:
        break
    if not line.startswith("ATOM") or line[12:16].strip() != "CA" or line[16] not in " A":
        continue
    chain = chain or line[21]
    if line[21] != chain:
        continue
    out.append([int(line[22:26]), AA.get(line[17:20], "X"),
                round(float(line[30:38]), 2), round(float(line[38:46]), 2), round(float(line[46:54]), 2)])

page = pathlib.Path(__file__).with_name("index.html")
html = page.read_text()
html, n = re.subn(r"const EMBEDDED = \[.*?\];", lambda _: "const EMBEDDED = " + json.dumps(out, separators=(",", ":")) + ";", html, count=1, flags=re.S)
assert n == 1, "EMBEDDED line not found"
page.write_text(html)
print(f"embedded {len(out)} residues ({out[0][0]}-{out[-1][0]}) from chain {chain}")
