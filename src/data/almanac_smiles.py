"""SMILES for the ALMANAC drugs -> data/processed/almanac_smiles.csv  (external set).

    python -m src.data.almanac_smiles

DrugComb stores the ALMANAC drugs under NCI's own names: generic names, trade names, NSC
codes, salts, two bare ChEMBL ids, one CAS number and one IUPAC string. Resolution is tiered
and every drug records the tier it came from in `resolved_by`:

  1. oneil     the name, or its alias below, is already in data/processed/smiles.csv -> reuse
               that exact structure, so a compound shared with training is byte-identical
  2. manual    cisplatin, carboplatin, oxaliplatin: the registries store the ligands as
               separate fragments and the salt stripper would keep only [Pt]Cl2
  3. unichem   the name IS a ChEMBL id -> UniChem v1 -> InChI -> RDKit
  4. cactus    NCI CACTUS structure resolver on the name, the salt-stripped name, the name
               without its parenthetical
  5. unichem+  a curated ChEMBL id for the seven drugs CACTUS does not know (it stops at
               roughly 2010), each one checked by molecular formula before it is accepted

ChEMBL's own API was the first choice, as in src.data.smiles, and is not used here: on
2026-11-23 `molecule.json?pref_name__iexact=` hangs past 60 s and `molecule/<id>.json`
answers HTTP 500, so the O'Neil resolver would not run today either. UniChem (also EBI) is
up, which is why ChEMBL ids still resolve. Wikidata was tried as a third source and dropped:
its query service was rate-limiting to one request a minute during an outage, and a source
that answers or not depending on the day has no place in a data pipeline.

CACTUS can return a structure without stereochemistry. That changes
nothing the model sees: atom features are symbol / degree / H count / implicit valence /
aromaticity, bonds carry no stereo, and the Morgan generator is built without chirality. It
would matter if the thesis ever reported a stereo-dependent descriptor, and it does not.

The run prints every compound whose standardised form lost more than 40% of its heavy atoms,
which is how a stripped coordination complex or a mis-stripped prodrug shows up.
"""
import argparse
import json
import re
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger

from src.data.smiles import MANUAL, standardise

RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "processed"
CACTUS = "https://cactus.nci.nih.gov/chemical/structure/"
UNICHEM = "https://www.ebi.ac.uk/unichem/api/v1/compounds"
UA = "Mozilla/5.0 (compatible; syngt-thesis-data-prep)"
CACHE = Path("/tmp/claude-0/almanac_smiles_cache.json")

SALT = re.compile(r"\s+(HYDROCHLORIDE|SULFATE|SULPHATE|CITRATE|DITARTRATE|TARTRATE|MESYLATE"
                  r"|PHOSPHATE|SODIUM|DISODIUM|MALEATE|BASE|HCL|ACETATE)$")

# Hand-checked renames, each confirmed against the structure that came back.
ALIAS = {
    "1-(5-DEOXYPENTOFURANOSYL)-5-FLUORO-4-{[(PENTYLOXY)CARBONYL]AMINO}PYRIMIDIN-2(1H)-ONE":
        "CAPECITABINE",
    "ADM HYDROCHLORIDE": "DOXORUBICIN",
    "ANTIBIOTIC AD 32": "VALRUBICIN",
    "ANTIBIOTIC AY 22989": "SIROLIMUS",
    "CISPLATINO": "CISPLATIN",
    "ELOXATIN (TN) (SANOFI SYNTHELAB)": "OXALIPLATIN",
    "EMCYT (PHARMACIA)": "ESTRAMUSTINE",
    "GEMZAR (LILLY)": "GEMCITABINE",
    "NAVELBINE DITARTRATE (TN)": "VINORELBINE",
    "ZOLINZA": "VORINOSTAT",
    "AZACYTIDINE": "AZACITIDINE",
    "5-FLUORO-2'-DEOXYURIDINE": "FLOXURIDINE",
    "ACTINOMYCIN D": "DACTINOMYCIN",
    "THIOGUANINE": "TIOGUANINE",
    "URACIL MUSTARD": "URAMUSTINE",
    "TRIETHYLENEMELAMINE": "TRETAMINE",
    # ALMANAC's bleomycin is the clinical sulfate, a mixture; A2 is 55-70% of it and is the
    # only component any registry gives a structure for. Recorded as an approximation.
    "BLEOMYCIN": "BLEOMYCIN A2",
    # NSC codes, one CAS number and the two ChEMBL ids, identified through CACTUS /names and
    # UniChem (formula + InChI) before being looked up as compounds:
    "NSC 85998": "STREPTOZOCIN",
    "NSC-127716": "DECITABINE",
    "NSC141540": "ETOPOSIDE",
    "NSC256439": "IDARUBICIN",
    "NSC733504": "EVEROLIMUS",
    "34793-34-5": "NELARABINE",          # 2-amino-6-methoxypurine arabinoside, NSC 686673
    "CO-V": "PENTOSTATIN",               # 2'-deoxycoformycin
}

# ChEMBL17639 is cladribine and CHEMBL277800 clofarabine (UniChem formulas C10H12ClN5O3 and
# C10H11ClFN5O3); both are resolved by id, so the names are left as they come.
MANUAL_EXTRA = {"CISPLATIN": "N[Pt](N)(Cl)Cl", **MANUAL}

# Excluded on purpose, with the reason kept next to the data.
#
# `standardise()` runs rdMolStandardize.Cleanup, whose MetalDisconnector cuts metal-ligand
# bonds, and then keeps the largest fragment. For carboplatin that leaves cyclobutane-1,1-
# dicarboxylic acid and for oxaliplatin 1,2-diaminocyclohexane: BOTH are already in the
# training set that way (data/processed/smiles.csv), platinum-free, so ALMANAC reusing those
# structures is consistent with what the model was trained on. Cisplatin has no organic
# ligand at all, so the same pipeline turns it into a single nitrogen atom. A one-atom
# molecule is not a usable input, and giving cisplatin its platinum back would hand the
# model an atom type it never saw in training, so the drug leaves the external set and the
# 4,736 triples it appears in are reported as dropped.
EXCLUDE = {"CISPLATINO": "standardiser strips the Pt centre and nothing organic is left"}

# CACTUS knows almost nothing approved after about 2010, so these seven need an id. Each was
# found by name in UniChem or, for cabazitaxel, through its InChIKey, and each is pinned to
# its molecular formula here so a wrong id fails loudly instead of inserting another drug.
CURATED_CHEMBL = {
    "SIROLIMUS": ("CHEMBL413", "C51H79NO13"),
    "CRIZOTINIB": ("CHEMBL601719", "C21H22Cl2FN5O"),
    "VEMURAFENIB": ("CHEMBL1229517", "C23H18ClF2N3O3S"),
    "VISMODEGIB": ("CHEMBL473417", "C19H14Cl2N2O3S"),
    "RUXOLITINIB": ("CHEMBL1789941", "C17H18N6"),
    "NILOTINIB": ("CHEMBL255863", "C28H22F3N7O"),
    "CABAZITAXEL": ("CHEMBL1201748", "C45H57NO14"),
}


def _get(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data,
                                 headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode()


def cached(key, fn):
    """Disk cache of successful lookups only.

    A failure is NOT cached: Wikidata was rate-limiting to one request a minute while this
    was written, so caching the 429 would have turned a temporary refusal into a permanently
    unresolved drug.
    """
    c = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    if key in c:
        return c[key]
    try:
        v = fn()
    except Exception:                      # a dead source must not lose the other 101 drugs
        return None
    if v is None:
        return None
    c[key] = v
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(c))
    return v


def by_cactus(name):
    def go():
        t = _get(CACTUS + urllib.parse.quote(name) + "/smiles").strip().split("\n")[0]
        return t if t and "<" not in t else None
    return cached("cactus:" + name, go)


def by_unichem(chembl_id, formula=None):
    """ChEMBL id -> UniChem InChI -> RDKit SMILES, refusing a formula mismatch.

    The formula check is what makes a hand-written ChEMBL id safe: a wrong id returns a
    perfectly valid structure of a different drug. It caught one while this was written -
    the first id tried for cabazitaxel answered C17H17N3O2S.ClH.
    """
    def go():
        body = json.dumps({"type": "sourceID", "compound": chembl_id, "sourceID": 1}).encode()
        d = json.loads(_get(UNICHEM, body, {"Content-Type": "application/json"}))
        got = d["compounds"][0]["inchi"]
        if formula and got["formula"] != formula:
            raise ValueError(f"{chembl_id}: formula {got['formula']}, expected {formula}")
        m = Chem.MolFromInchi(got["inchi"])
        return Chem.MolToSmiles(m) if m else None
    return cached("unichem:" + chembl_id, go)


def variants(name):
    v = [name, SALT.sub("", name).strip(), re.sub(r"\s*\(.*?\)", "", name).strip()]
    return [x for x in dict.fromkeys(v) if x]


def resolve(name, oneil):
    """-> (raw_smiles, tier, query_used)"""
    if name in EXCLUDE:
        return None, "excluded", EXCLUDE[name]
    if name in oneil:
        return oneil[name], "oneil", name
    look = ALIAS.get(name, name)
    pre = "alias+" if look != name else ""
    if look in MANUAL_EXTRA:
        return MANUAL_EXTRA[look], pre + "manual", look
    if look in oneil:
        return oneil[look], pre + "oneil", look
    if re.match(r"^CHEMBL\d+$", look):
        s = by_unichem(look)
        if s:
            return s, "unichem", look
    if look in CURATED_CHEMBL:
        cid, formula = CURATED_CHEMBL[look]
        s = by_unichem(cid, formula)
        if s:
            return s, pre + "unichem_curated", f"{look} = {cid}"
    for v in variants(look):
        s = by_cactus(v)
        if s:
            return s, pre + "cactus", v
    return None, "unresolved", look


def main():
    trip = pd.read_csv(OUT / "almanac_triples.csv")
    names = sorted(set(trip.drug_a) | set(trip.drug_b))
    o = pd.read_csv(OUT / "smiles.csv")
    o = o[o.smiles.notna() & (o.rdkit == "ok")]
    oneil = dict(zip(o.drug, o.smiles))

    rows = []
    for n in names:
        raw, tier, used = resolve(n, oneil)
        if raw is None:
            rows.append({"drug": n, "smiles": None, "resolved_by": tier, "query": used})
            print(f"  {n[:52]:54s} {tier.upper():16s} {used}")
            continue
        can, key, status = standardise(raw)
        m0, m1 = Chem.MolFromSmiles(raw), (Chem.MolFromSmiles(can) if can else None)
        rows.append({"drug": n, "smiles": can, "inchikey": key, "raw_smiles": raw,
                     "resolved_by": tier, "query": used, "rdkit": status,
                     "n_atoms": m1.GetNumAtoms() if m1 else None,
                     "n_atoms_raw": m0.GetNumAtoms() if m0 else None})
        print(f"  {n[:52]:54s} {tier:16s} {str(key):29s} {(can or '')[:36]}")
    s = pd.DataFrame(rows)
    s.to_csv(OUT / "almanac_smiles.csv", index=False)

    ok = s[s.smiles.notna() & (s.rdkit == "ok")]
    shrunk = ok[ok.n_atoms < 0.6 * ok.n_atoms_raw]
    dup = ok[ok.inchikey.duplicated(keep=False)].sort_values("inchikey")
    kept = trip[trip.drug_a.isin(ok.drug) & trip.drug_b.isin(ok.drug)]
    shared = sorted(set(ok.inchikey) & set(o.inchikey.dropna()))
    rep = {"date": str(date.today()), "drugs_total": len(names), "resolved": len(ok),
           "unresolved": s[s.smiles.isna() & (s.resolved_by == "unresolved")].drug.tolist(),
           "excluded": {k: v for k, v in EXCLUDE.items()},
           "by_tier": s.resolved_by.value_counts().to_dict(),
           "lost_atoms_in_standardisation":
               shrunk[["drug", "n_atoms_raw", "n_atoms"]].to_dict("records"),
           "duplicate_inchikey": dup[["drug", "inchikey"]].to_dict("records"),
           "shared_inchikeys_with_oneil": len(shared),
           "triples_before": len(trip), "triples_with_smiles": len(kept),
           "triples_dropped_pct": round(100 * (len(trip) - len(kept)) / len(trip), 1)}
    (OUT / "provenance_almanac_smiles.json").write_text(json.dumps(rep, indent=1))
    print(f"\nresolved {len(ok)}/{len(names)}  tiers {rep['by_tier']}")
    print(f"unresolved: {rep['unresolved']}")
    print(f"lost >40% of heavy atoms: {rep['lost_atoms_in_standardisation']}")
    print(f"duplicate InChIKey: {rep['duplicate_inchikey']}")
    print(f"shares {len(shared)} compounds with O'Neil")
    print(f"triples {len(trip)} -> {len(kept)} ({rep['triples_dropped_pct']}% dropped)")
    return s


if __name__ == "__main__":
    argparse.ArgumentParser().parse_args()
    main()
