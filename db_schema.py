

from sqlalchemy import create_engine
from sqlmodel import Field, SQLModel, Session, Relationship
from typing import Optional, List

class Taxon(SQLModel, table=True):
    id: int = Field(primary_key=True)
    parent_id: Optional[int] = Field(default=None, foreign_key="taxon.id")
    rank: Optional[str] = None

    parent: Optional["Taxon"] = Relationship(back_populates="children", sa_relationship_kwargs={"remote_side": "Taxon.id"})
    children: List["Taxon"] = Relationship(back_populates="parent")
    names: List["TaxonName"] = Relationship(back_populates="taxon")

class TaxonName(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    taxon_id: int = Field(foreign_key="taxon.id")
    name: str
    name_class: str

    taxon: Taxon = Relationship(back_populates="names")


# Replace with your actual file path
DATA_FILE = "data_files/small_names.dmp"
NODES_DATA = "data_files/small_nodes.dmp"

sqlite_file = "taxonomyq.db"
engine = create_engine(f"sqlite:///{sqlite_file}", echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)



