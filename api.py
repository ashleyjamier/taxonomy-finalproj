from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session, select
from typing import Optional, List
from pydantic import BaseModel

from db_schema import Taxon, TaxonName
from db_schema import engine  # make sure engine is imported from a separate file

router = APIRouter()

class TaxonNameRead(BaseModel):
    name: str
    name_class: str

    class Config:
        orm_mode = True


class TaxonRead(BaseModel):
    id: int
    rank: Optional[str]
    parent_id: Optional[int]
    scientific_name: Optional[str]
    names: List[TaxonNameRead] = []
    children: List[int] = []

    class Config:
        orm_mode = True


@router.get("/taxa", response_model=TaxonRead)
def get_taxon(tax_id: int = Query(..., description="Taxon ID to retrieve")):
    with Session(engine) as session:
        taxon = session.get(Taxon, tax_id)
        if not taxon:
            raise HTTPException(status_code=404, detail="Taxon not found")

        scientific_name = next((n.name for n in taxon.names if n.name_class == "scientific name"), None)
        children_ids = [child.id for child in taxon.children]

        # Explicitly structure names for response_model
        name_list = [{"name": n.name, "name_class": n.name_class} for n in taxon.names]

        return TaxonRead(
            id=taxon.id,
            rank=taxon.rank,
            parent_id=taxon.parent_id,
            scientific_name=scientific_name,
            names=name_list,
            children=children_ids,
        )


@router.get("/search")
def search_names(keyword: str, mode: str, page: int = 1, items_per_page: int = 10):
    with Session(engine) as session:
        query = select(TaxonName)

        if mode == "contains":
            query = query.where(TaxonName.name.contains(keyword))
        elif mode == "starts with":
            query = query.where(TaxonName.name.startswith(keyword))
        elif mode == "ends with":
            query = query.where(TaxonName.name.endswith(keyword))

        results = session.exec(query.offset((page - 1) * items_per_page).limit(items_per_page)).all()

        # Include taxon_id in your API response!
        return [{"taxon_id": n.taxon_id, "name": n.name, "name_class": n.name_class} for n in results]
