"""Build drug -> target gene tables for the 38 O'Neil drugs.

Primary  (drug_targets.csv):       ChEMBL mechanism-of-action + DrugCentral MOA targets + 2 manual entries.
Contrast (drug_targets_dgidb.csv): DGIdb, all interactions, for the target-source sensitivity table.

Needs network once (ChEMBL REST API); outputs are small CSVs meant to be committed.
Run: python src/data/build_targets.py
"""
import gzip
import json
import urllib.request
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
RAW = HERE / "raw"
API = "https://www.ebi.ac.uk/chembl/api/data/"

# DrugComb name -> ChEMBL parent id. Picked by hand: the API name search is fuzzy.
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
# Not in ChEMBL. Verify these citations before the thesis uses them.
MANUAL = [
    ("MRK-003", g, "manual:gamma-secretase inhibitor (Lewis et al. 2007, Chem Biol)")
    for g in ["PSEN1", "PSEN2", "NCSTN", "APH1A", "PSENEN"]
] + [("MK-4541", "AR", "manual:SARM (Chisamore et al. 2016, PLoS One)")]
# In ChEMBL but without a mechanism record.
MANUAL += [("GELDANAMYCIN", g, "manual:HSP90 inhibitor") for g in ["HSP90AA1", "HSP90AB1"]]
MANUAL += [("L778123", g, "manual:FTase/GGTase-I inhibitor") for g in ["FNTA", "FNTB", "PGGT1B"]]


def get(path):
    with urllib.request.urlopen(API + path, timeout=120) as r:
        return json.load(r)


def chembl_targets():
    version = get("status.json")["chembl_db_version"]
    rows, names, target_cache = [], {}, {}
    for drug, cid in CHEMBL.items():
        names[drug] = get(f"molecule/{cid}.json")["pref_name"]
        for m in get(f"mechanism.json?molecule_chembl_id={cid}&limit=100")["mechanisms"]:
            tid = m["target_chembl_id"]
            if tid not in target_cache:
                target_cache[tid] = get(f"target/{tid}.json")
            t = target_cache[tid]
            if t["organism"] != "Homo sapiens":  # DNA, tubulin from other species, etc.
                continue
            for c in t["target_components"]:
                for s in c["target_component_synonyms"]:
                    if s["syn_type"] == "GENE_SYMBOL":
                        rows.append((drug, s["component_synonym"], f"chembl:{version}"))
    return pd.DataFrame(rows, columns=["drug", "gene", "source"]), names


def drugcentral_targets(names):
    dc = pd.read_csv(RAW / "drug.target.interaction.tsv.gz", sep="\t")
    dc = dc[(dc.MOA == 1) & (dc.ORGANISM == "Homo sapiens")]
    by_name = {n.lower(): d for d, n in names.items() if n}
    dc = dc[dc.DRUG_NAME.str.lower().isin(by_name)]
    # GENE can hold several symbols joined by '|' (complexes)
    rows = [(by_name[n.lower()], g, "drugcentral:2021_09_01")
            for n, gs in zip(dc.DRUG_NAME, dc.GENE) for g in str(gs).split("|")]
    return pd.DataFrame(rows, columns=["drug", "gene", "source"])


def dgidb_targets(names):
    # DGIdb concept ids are mostly ncit/rxcui, so match on the normalised drug name instead
    dg = pd.read_csv(RAW / "interactions.tsv", sep="\t", dtype=str).dropna(subset=["gene_name", "drug_name"])
    by_name = {n.upper(): d for d, n in names.items() if n}
    by_name.update({d: d for d in ["MK-4541", "MRK-003"]})
    drug = dg.drug_name.str.upper().map(by_name)
    keep = drug.notna()
    return pd.DataFrame({"drug": drug[keep], "gene": dg.gene_name[keep],
                         "source": "dgidb:" + dg.interaction_source_db_name[keep]})


def merge_sources(chembl, dc):
    # ChEMBL expands complexes into every subunit (bortezomib -> 38 proteasome genes);
    # where DrugCentral also annotates the drug, keep only the genes both agree on.
    both = set(chembl.drug) & set(dc.drug)
    agreed = chembl.merge(dc[["drug", "gene"]], on=["drug", "gene"])
    return pd.concat([chembl[~chembl.drug.isin(both)], dc[~dc.drug.isin(both)],
                      agreed, dc.merge(chembl[["drug", "gene"]], on=["drug", "gene"])])


def main():
    chembl, names = chembl_targets()
    primary = pd.concat([merge_sources(chembl, drugcentral_targets(names)),
                         pd.DataFrame(MANUAL, columns=["drug", "gene", "source"])])
    primary = (primary.groupby(["drug", "gene"]).source
               .agg(lambda s: ";".join(sorted(set(s)))).reset_index())
    primary.to_csv(HERE / "drug_targets.csv", index=False)
    dgidb_targets(names).drop_duplicates().to_csv(HERE / "drug_targets_dgidb.csv", index=False)

    n = primary.groupby("drug").gene.nunique()
    all_drugs = list(CHEMBL) + ["MK-4541", "MRK-003"]
    print(n.reindex(all_drugs).fillna(0).astype(int).to_string())
    print("no target:", [d for d in all_drugs if d not in n.index])


if __name__ == "__main__":
    main()
