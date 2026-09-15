from fastapi import APIRouter, Depends

from app.auth.rbac import require_any_admin
from kazgaza_shared import ApplicationType

router = APIRouter(prefix="/application-types", tags=["application-types"])

LABELS_KK = {
    ApplicationType.METER_NOT_WORKING: "Счетчик жұмыс жасамайды",
    ApplicationType.MPI_REMOVAL: "МПИ-ге шешу",
    ApplicationType.GAS_LEAK: "Есептеу құралынан газ шығуы",
}


@router.get("", dependencies=[Depends(require_any_admin)])
async def list_application_types():
    return [{"value": t.value, "label_kk": LABELS_KK[t]} for t in ApplicationType]
