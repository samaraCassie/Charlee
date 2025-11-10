"""CRUD operations for database models."""

from typing import Optional
from sqlalchemy.orm import Session
from database.models import BigRock, Tarefa
from database.schemas import BigRockCreate, BigRockUpdate, TarefaCreate, TarefaUpdate


# ==================== Big Rock CRUD ====================


def get_big_rock(db: Session, big_rock_id: int) -> Optional[BigRock]:
    """Get a single BigRock by ID."""
    return db.query(BigRock).filter(BigRock.id == big_rock_id).first()


def get_big_rocks(
    db: Session, skip: int = 0, limit: int = 100, ativo_apenas: bool = False
) -> list[BigRock]:
    """Get list of BigRocks."""
    query = db.query(BigRock)

    if ativo_apenas:
        query = query.filter(BigRock.ativo)

    return query.offset(skip).limit(limit).all()


def create_big_rock(db: Session, big_rock: BigRockCreate) -> BigRock:
    """Create a new BigRock."""
    db_big_rock = BigRock(**big_rock.model_dump())
    db.add(db_big_rock)
    db.commit()
    db.refresh(db_big_rock)
    return db_big_rock


def update_big_rock(
    db: Session, big_rock_id: int, big_rock_update: BigRockUpdate
) -> Optional[BigRock]:
    """Update a BigRock."""
    db_big_rock = get_big_rock(db, big_rock_id)
    if not db_big_rock:
        return None

    update_data = big_rock_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_big_rock, field, value)

    db.commit()
    db.refresh(db_big_rock)
    return db_big_rock


def delete_big_rock(db: Session, big_rock_id: int) -> bool:
    """Delete a BigRock (soft delete by setting ativo=False)."""
    db_big_rock = get_big_rock(db, big_rock_id)
    if not db_big_rock:
        return False

    db_big_rock.ativo = False
    db.commit()
    return True


# ==================== Tarefa CRUD ====================


def get_tarefa(db: Session, tarefa_id: int) -> Optional[Tarefa]:
    """Get a single Tarefa by ID."""
    return db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()


def get_tarefas(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    big_rock_id: Optional[int] = None,
    tipo: Optional[str] = None,
) -> list[Tarefa]:
    """Get list of Tarefas with optional filters."""
    query = db.query(Tarefa)

    if status:
        query = query.filter(Tarefa.status == status)

    if big_rock_id:
        query = query.filter(Tarefa.big_rock_id == big_rock_id)

    if tipo:
        query = query.filter(Tarefa.tipo == tipo)

    return query.order_by(Tarefa.deadline.asc().nullslast()).offset(skip).limit(limit).all()


def create_tarefa(db: Session, tarefa: TarefaCreate) -> Tarefa:
    """Create a new Tarefa."""
    db_tarefa = Tarefa(**tarefa.model_dump())
    db.add(db_tarefa)
    db.commit()
    db.refresh(db_tarefa)
    return db_tarefa


def update_tarefa(db: Session, tarefa_id: int, tarefa_update: TarefaUpdate) -> Optional[Tarefa]:
    """Update a Tarefa."""
    db_tarefa = get_tarefa(db, tarefa_id)
    if not db_tarefa:
        return None

    update_data = tarefa_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tarefa, field, value)

    db.commit()
    db.refresh(db_tarefa)
    return db_tarefa


def marcar_tarefa_concluida(db: Session, tarefa_id: int) -> Optional[Tarefa]:
    """Mark a Tarefa as completed."""
    db_tarefa = get_tarefa(db, tarefa_id)
    if not db_tarefa:
        return None

    db_tarefa.marcar_concluida()
    db.commit()
    db.refresh(db_tarefa)
    return db_tarefa


def reabrir_tarefa(db: Session, tarefa_id: int) -> Optional[Tarefa]:
    """Reopen a completed Tarefa."""
    db_tarefa = get_tarefa(db, tarefa_id)
    if not db_tarefa:
        return None

    db_tarefa.reabrir()
    db.commit()
    db.refresh(db_tarefa)
    return db_tarefa


def delete_tarefa(db: Session, tarefa_id: int) -> bool:
    """Delete a Tarefa permanently."""
    db_tarefa = get_tarefa(db, tarefa_id)
    if not db_tarefa:
        return False

    db.delete(db_tarefa)
    db.commit()
    return True
