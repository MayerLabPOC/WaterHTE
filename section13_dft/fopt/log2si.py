#!/usr/bin/env python3
import sys, os, re, glob

# This python script generates xyz reports for the supporting information

def warn(msg):
    sys.stderr.write(f"[log2si] {msg}\n")

def read_text(fn):
    with open(fn, "r", errors="ignore") as f:
        return f.read()

def find_last_scf_energy(text):
    m = None
    for m in re.finditer(r"SCF Done:\s+E\([RU]?[A-Za-z0-9\-]+\)\s*=\s*([\-]?\d+\.\d+)", text):
        pass
    if m: return float(m.group(1))
    m2 = None
    for m2 in re.finditer(r"\\HF=([\-]?\d+\.\d+)", text):
        pass
    return float(m2.group(1)) if m2 else None

def find_last_thermo(text, kind):
    pat = (r"Sum of electronic and thermal Enthalpies\s*=\s*([\-]?\d+\.\d+)"
           if kind=="H" else
           r"Sum of electronic and thermal Free Energies\s*=\s*([\-]?\d+\.\d+)")
    m=None
    for m in re.finditer(pat, text): pass
    return float(m.group(1)) if m else None

def find_negative_freqs(text):
    """Return all negative frequencies (imaginary modes) reported by Gaussian."""
    freqs=[]
    for line in re.findall(r"(?m)^\s*Frequencies --([^\n]+)", text):
        for n in re.findall(r"([\-]?\d+(?:\.\d+)?)", line):
            try:
                freq = float(n)
                if freq < 0:
                    freqs.append(freq)
            except ValueError:
                pass
    return freqs

def count_negative_freqs(text):
    return len(find_negative_freqs(text))

def format_freq_cm1(freq):
    """Format a frequency for compact SI output, e.g. -134 cm-1."""
    return f"{freq:.0f}" if abs(freq - round(freq)) < 0.05 else f"{freq:.1f}"

# Flexible archive finder: start at line-begin '1\' and end at a backslash then optional whitespace then '@'
_ARCHIVE_RE = re.compile(r"(?ms)^\s*1\\.*?(?:\\\s*@)")
def find_all_archives(text):
    return [m.group(0) for m in _ARCHIVE_RE.finditer(text)]

_CM = re.compile(r"\s*-?\d+\s*,\s*\d+\s*")

def pick_last_archive_with_geom(text):
    chosen=None
    for blk in find_all_archives(text):
        s = blk.replace("\n","")
        toks = [t for t in s.split("\\") if t.strip()!=""]
        cm_idx=-1
        for i,t in enumerate(toks):
            if _CM.fullmatch(t): cm_idx=i
        if cm_idx==-1: continue
        ok=False
        for j in range(cm_idx+1, len(toks)):
            t=toks[j].strip()
            if t=="@" or "=" in t: break
            if re.match(r"^\s*[A-Za-z]{1,2}\s*,", t):
                ok=True; break
        if ok: chosen=blk
    return chosen

def parse_archive_geometry(archive_block):
    s = archive_block.replace("\n","")
    toks = [t for t in s.split("\\") if t.strip()!=""]
    cm_idx=-1
    for i,t in enumerate(toks):
        if _CM.fullmatch(t): cm_idx=i
    if cm_idx==-1: return None
    atoms=[]
    for j in range(cm_idx+1, len(toks)):
        t = toks[j].strip()
        if t=="@" or "=" in t: break
        t = re.sub(r"\s+","", t)
        t = re.sub(r"^([A-Za-z]{1,2}),", r"\1,", t)
        t = re.sub(r"E([+\-])\s+", r"E\1", t, flags=re.IGNORECASE)
        parts = t.split(",")
        if len(parts)>=4 and re.fullmatch(r"[A-Za-z]{1,2}", parts[0]):
            try:
                el=parts[0].title(); x,y,z = float(parts[1]), float(parts[2]), float(parts[3])
                atoms.append((el,x,y,z))
            except: pass
    return atoms if atoms else None

def format_block(filename, E,H,G,NImag, atoms, imag_freqs=None):
    out=[]
    out.append(os.path.basename(filename))
    out.append(f"E = {E:15.6f}" if E is not None else "E =     (not found)")
    out.append(f"H = {H:15.6f}" if H is not None else "H =     (not found)")
    out.append(f"G = {G:15.6f}" if G is not None else "G =     (not found)")
    if NImag == 1 and imag_freqs:
        out.append(f"NImag=1 ({format_freq_cm1(imag_freqs[0])} cm-1)")
    else:
        out.append(f"NImag={NImag}")
    if atoms:
        for el,x,y,z in atoms:
            out.append(f"{el:<2s}{x:15.7f}{y:15.7f}{z:15.7f}")
    else:
        warn("geometry from final archive not found.")
    out.append("")
    return "\n".join(out)

def process_file(fn):
    text = read_text(fn)
    E = find_last_scf_energy(text)
    H = find_last_thermo(text, "H")
    G = find_last_thermo(text, "G")
    imag_freqs = find_negative_freqs(text)
    NImag = len(imag_freqs)
    arch = pick_last_archive_with_geom(text)
    atoms = parse_archive_geometry(arch) if arch else None
    return format_block(fn, E,H,G,NImag, atoms, imag_freqs)

def main():
    files = sorted(glob.glob("*.log"))
    if not files:
        warn("No .log files found in current directory.")
    with open("log2si_output.txt","w") as fout:
        for fn in files:
            try:
                block = process_file(fn)
                fout.write(block + "\n")
                print(fn)
            except Exception as e:
                warn(f"{fn}: failed with {type(e).__name__}: {e}")

if __name__=="__main__":
    main()
