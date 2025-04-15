
from db_schema import *

def parse_names_file(file_path: str):
    names = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4:
                tax_id, name_txt, _, name_class = parts[:4]
                try:
                    names.append(TaxonName(taxon_id=int(tax_id), name=name_txt, name_class=name_class))
                except ValueError:
                    print(f"Skipping invalid line: {line}")
    return names

def parse_nodes_file(file_path: str):
    taxa = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                tax_id_str, parent_id_str, rank = parts[:3]
                try:
                    tax_id = int(tax_id_str)
                    parent_id = int(parent_id_str)
                    taxa.append(Taxon(id=tax_id, parent_id=parent_id, rank=rank))
                except ValueError:
                    print(f"Skipping invalid line: {line}")
    return taxa


def populate_taxon_names(names_had: list[TaxonName]):
    with Session(engine) as session:
        session.add_all(names_had)
        session.commit()

def populate_taxon_parents(parents_had: list[Taxon]):
    with Session(engine) as session:
        session.add_all(parents_had)
        session.commit()


create_db_and_tables()
names = parse_names_file(DATA_FILE)
taxa = parse_nodes_file(NODES_DATA)
populate_taxon_names(names)
populate_taxon_parents(taxa)
print(f"Inserted {len(names)} taxon names into the database.")
print(f"Inserted {len(taxa)} taxon nodes into the database.")