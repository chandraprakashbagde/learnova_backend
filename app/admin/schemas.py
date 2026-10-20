from datetime import datetime, timezone

from pydantic import BaseModel, field_serializer


class MasterDataItemOut(BaseModel):
    """A subject or qualification as the admin UI consumes it.

    Mirrors `MasterDataItem` in
    `learnova_frontend/src/features/admin/api/adminMasterData.api.ts`.
    `created_at` is optional because the `subjects` table has no such column,
    and `teacher_count` is optional because it is derived, not stored.
    """

    id: int
    name: str
    created_at: datetime | None = None
    teacher_count: int | None = None

    @field_serializer("created_at")
    def _serialize_created_at(self, value: datetime | None) -> datetime | None:
        # MySQL DATETIME columns are returned naive but are always written in
        # UTC (`datetime.now(timezone.utc)`), so re-attach the offset —
        # otherwise the browser reads them as local time.
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value


class MasterDataListOut(BaseModel):
    """Paginated list envelope shared by GET /admin/subjects and
    GET /admin/qualifications."""

    items: list[MasterDataItemOut]
    total: int
    page: int
    page_size: int
