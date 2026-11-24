"""SMILES for the O'Neil drugs -> data/processed/smiles.csv  (planner 3.2, 4.1).

    python -m src.data.smiles

Three tiers, logged per drug in `resolved_by`:
  1. chembl_id   curated ChEMBL id -> molecule endpoint (the reliable path)
  2. chembl_name exact name match, pref_name__iexact (NEVER the fuzzy search endpoint:
                 "gemcitabine" returns GEMCITABINE ELAIDATE, a different compound)
  3. manual      hand-entered for compounds ChEMBL has no structure for (Pt complexes)

Then RDKit standardisation: largest fragment (salt strip), uncharge, canonical tautomer,
canonical SMILES, InChIKey. Two names with the same InChIKey are the same compound and
must be merged, otherwise the leave-drug split leaks.
"""
import argparse
import json
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import inchi
from rdkit.Chem.MolStandardize import rdMolStandardize

RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "processed"
API = "https://www.ebi.ac.uk/chembl/api/data/"

# Curated ChEMBL ids for the 38 O'Neil drugs (verified one by one against pref_name).
CHEMBL = {
    "5-FU": "CHEMBL185", "ABT-888": "CHEMBL506871", "AZD1775": "CHEMBL1976040",
    "BEZ-235": "CHEMBL1879463", "BORTEZOMIB": "CHEMBL325041", "CARBOPLATIN": "CHEMBL1351",
    "CYCLOPHOSPHAMIDE": "CHEMBL88", "DASATINIB": "CHEMBL1421", "DEXAMETHASONE": "CHEMBL384467",
    "DINACICLIB": "CHEMBL2103840", "DOXORUBICIN": "CHEMBL53463", "ERLOTINIB": "CHEMBL553",
    "ETOPOSIDE": "CHEMBL44657", "GELDANAMYCIN": "CHEMBL278315", "GEMCITABINE": "CHEMBL888",
    "L778123": "CHEMBL279433", "LAPATINIB": "CHEMBL554", "METFORMIN": "CHEMBL1431",
    "METHOTREXATE": "CHEMBL34259", "MITOMYCINE": "CHEMBL105", "MK-2206": "CHEMBL1079175",
    "MK-4827": "CHEMBL1094636", "MK-5108": "CHEMBL3600873", "MK-8669": "CHEMBL2103839",
    "MK-8776": "CHEMBL2386889", "OXALIPLATIN": "CHEMBL414804", "PACLITAXEL": "CHEMBL428647",
    "PD325901": "CHEMBL507361", "SN-38": "CHEMBL837", "SORAFENIB": "CHEMBL1336",
    "SUNITINIB": "CHEMBL535", "TEMOZOLOMIDE": "CHEMBL810", "TOPOTECAN": "CHEMBL84",
    "VINBLASTINE": "CHEMBL159", "VINORELBINE": "CHEMBL553025", "ZOLINZA": "CHEMBL98",
}

# ChEMBL stores no structure for these Pt(II) complexes. Taken from PubChem CID 38904
# (carboplatin) and CID 5310940 (oxaliplatin); RDKit parses the dative-free form.
MANUAL = {
    "CARBOPLATIN": "O=C1O[Pt](N)(N)OC(=O)C12CCC2",
    "OXALIPLATIN": "O=C1O[Pt]2(OC1=O)[NH2][C@@H]1CCCC[C@H]1[NH2]2",
}

# No public structure: Merck internal codes. Kept out of the modelling set, reported as such.
NO_STRUCTURE = ["MK-4541", "MRK-003"]


def get(path):
    with urllib.request.urlopen(API + path, timeout=90) as r:
        return json.load(r)


def by_id(cid):
    m = get(f"molecule/{cid}.json")
    return (m.get("molecule_structures") or {}).get("canonical_smiles"), m.get("pref_name")


def by_name(name):
    d = get(f"molecule.json?pref_name__iexact={urllib.parse.quote(name)}&limit=1")
    for m in d.get("molecules", []):
        s = (m.get("molecule_structures") or {}).get("canonical_smiles")
        if s:
            return s, m.get("molecule_chembl_id")
    return None, None


_LARGEST = rdMolStandardize.LargestFragmentChooser()
_UNCHARGE = rdMolStandardize.Uncharger()
_TAUT = rdMolStandardize.TautomerEnumerator()


def standardise(smi):
    """Salt strip -> uncharge -> canonical tautomer -> canonical SMILES + InChIKey."""
    m = Chem.MolFromSmiles(smi)
    if m is None:
        return None, None, "parse_failed"
    m = rdMolStandardize.Cleanup(m)
    m = _LARGEST.choose(m)
    m = _UNCHARGE.uncharge(m)
    try:
        m = _TAUT.Canonicalize(m)
    except Exception:
        pass                                    # Pt complexes can trip the enumerator
    return Chem.MolToSmiles(m), inchi.MolToInchiKey(m), "ok"


def main():
    trip = pd.read_csv(OUT / "triples.csv")
    drugs = sorted(set(trip.drug_a) | set(trip.drug_b))
    rows = []
    for d in drugs:
        smi = src = cid = None
        if d in CHEMBL:
            smi, _ = by_id(CHEMBL[d])
            src, cid = "chembl_id", CHEMBL[d]
        if not smi:
            smi, cid2 = by_name(d)
            if smi:
                src, cid = "chembl_name", cid2
        if not smi and d in MANUAL:
            smi, src, cid = MANUAL[d], "manual", None
        if not smi:
            rows.append({"drug": d, "smiles": None, "resolved_by": "unresolved", "chembl_id": cid})
            continue
        can, key, status = standardise(smi)
        rows.append({"drug": d, "smiles": can, "inchikey": key, "raw_smiles": smi,
                     "resolved_by": src, "chembl_id": cid, "rdkit": status,
                     "n_atoms": Chem.MolFromSmiles(can).GetNumAtoms() if can else None})
    s = pd.DataFrame(rows)

    dup = s[s.inchikey.notna() & s.inchikey.duplicated(keep=False)].sort_values("inchikey")
    ok = s[s.smiles.notna() & (s.rdkit == "ok")]
    OUT.mkdir(parents=True, exist_ok=True)
    s.to_csv(OUT / "smiles.csv", index=False)

    rep = {"date": str(date.today()), "drugs_total": len(drugs), "resolved": len(ok),
           "unresolved": s[s.smiles.isna()].drug.tolist(),
           "by_tier": s.resolved_by.value_counts().to_dict(),
           "duplicate_inchikey": dup[["drug", "inchikey"]].to_dict("records"),
           "no_public_structure": NO_STRUCTURE,
           "atoms_min": int(ok.n_atoms.min()), "atoms_max": int(ok.n_atoms.max()),
           "atoms_median": float(ok.n_atoms.median())}
    kept = trip[trip.drug_a.isin(ok.drug) & trip.drug_b.isin(ok.drug)]
    rep["triples_before"] = len(trip)
    rep["triples_with_smiles"] = len(kept)
    rep["triples_dropped_pct"] = round(100 * (len(trip) - len(kept)) / len(trip), 1)
    (OUT / "provenance_smiles.json").write_text(json.dumps(rep, indent=1))

    print(f"resolved {len(ok)}/{len(drugs)}  tiers {rep['by_tier']}")
    print(f"unresolved: {rep['unresolved']}")
    print(f"duplicate InChIKey: {rep['duplicate_inchikey']}")
    print(f"atoms min/median/max {rep['atoms_min']}/{rep['atoms_median']}/{rep['atoms_max']}")
    print(f"triples {len(trip)} -> {len(kept)} ({rep['triples_dropped_pct']}% dropped)")
    return s


if __name__ == "__main__":
    import urllib.parse
    argparse.ArgumentParser().parse_args()
    main()
