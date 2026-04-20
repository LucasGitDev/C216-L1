from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from threading import Lock

from fastapi import HTTPException, status

from app.core.config import get_settings


@dataclass
class MicrowaveState:
    id: int
    is_on: bool
    power: int
    content: str
    ends_at: datetime | None
    cycle_completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class MicrowaveService:
    def __init__(
        self,
        *,
        initial_count: int,
        default_power: int,
        min_power: int,
        max_power: int,
    ) -> None:
        self._initial_count = initial_count
        self._default_power = default_power
        self._min_power = min_power
        self._max_power = max_power
        self._lock = Lock()
        self._microwaves: dict[int, MicrowaveState] = {}
        self._next_id = 1

        for _ in range(initial_count):
            self._create_state()

    def reset_store(self, *, initial_count: int | None = None) -> None:
        with self._lock:
            self._microwaves = {}
            self._next_id = 1
            preload_count = self._initial_count if initial_count is None else initial_count
            for _ in range(preload_count):
                self._create_state()

    def list_microwaves(self) -> list[dict[str, object]]:
        with self._lock:
            return [self._serialize_state(state) for state in self._microwaves.values()]

    def get_microwave(self, microwave_id: int) -> dict[str, object]:
        with self._lock:
            state = self._get_state_or_404(microwave_id)
            return self._serialize_state(state)

    def create_microwave(self, *, power: int | None = None, content: str = "") -> dict[str, object]:
        with self._lock:
            self._validate_power(power or self._default_power)
            state = self._create_state(power=power, content=content)
            return self._serialize_state(state)

    def delete_microwave(self, microwave_id: int) -> None:
        with self._lock:
            self._get_state_or_404(microwave_id)
            del self._microwaves[microwave_id]

    def start_microwave(
        self,
        microwave_id: int,
        *,
        duration_seconds: int,
        content: str,
        power: int | None = None,
    ) -> dict[str, object]:
        with self._lock:
            state = self._get_state_or_404(microwave_id)
            self._refresh_state(state)

            if state.is_on:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="microwave is already running",
                )

            selected_power = power if power is not None else state.power
            self._validate_power(selected_power)

            if not content.strip():
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="content must not be empty",
                )

            now = self._now()
            state.is_on = True
            state.power = selected_power
            state.content = content.strip()
            state.ends_at = now + timedelta(seconds=duration_seconds)
            state.cycle_completed_at = None
            state.updated_at = now

            return self._serialize_state(state)

    def stop_microwave(self, microwave_id: int) -> dict[str, object]:
        with self._lock:
            state = self._get_state_or_404(microwave_id)
            self._refresh_state(state)

            if not state.is_on:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="microwave is already stopped",
                )

            now = self._now()
            state.is_on = False
            state.ends_at = None
            state.cycle_completed_at = None
            state.updated_at = now

            return self._serialize_state(state)

    def reset_microwave(self, microwave_id: int) -> dict[str, object]:
        with self._lock:
            state = self._get_state_or_404(microwave_id)
            self._reset_state(state)
            return self._serialize_state(state)

    def _create_state(self, power: int | None = None, content: str = "") -> MicrowaveState:
        now = self._now()
        state = MicrowaveState(
            id=self._next_id,
            is_on=False,
            power=power if power is not None else self._default_power,
            content=content,
            ends_at=None,
            cycle_completed_at=None,
            created_at=now,
            updated_at=now,
        )
        self._microwaves[state.id] = state
        self._next_id += 1
        return state

    def _reset_state(self, state: MicrowaveState) -> None:
        now = self._now()
        state.is_on = False
        state.power = self._default_power
        state.content = ""
        state.ends_at = None
        state.cycle_completed_at = None
        state.updated_at = now

    def _refresh_state(self, state: MicrowaveState) -> None:
        if state.ends_at is None:
            return

        now = self._now()
        if state.ends_at <= now:
            state.is_on = False
            state.ends_at = None
            state.cycle_completed_at = now
            state.updated_at = now

    def _serialize_state(self, state: MicrowaveState) -> dict[str, object]:
        self._refresh_state(state)

        remaining_seconds = 0
        status_value = "finished" if state.cycle_completed_at is not None else "idle"

        if state.is_on and state.ends_at is not None:
            remaining_seconds = max(int((state.ends_at - self._now()).total_seconds()), 0)
            status_value = "running"

        return {
            "id": state.id,
            "is_on": state.is_on,
            "status": status_value,
            "power": state.power,
            "content": state.content,
            "ends_at": state.ends_at,
            "remaining_seconds": remaining_seconds,
            "created_at": state.created_at,
            "updated_at": state.updated_at,
        }

    def _validate_power(self, power: int) -> None:
        if not self._min_power <= power <= self._max_power:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"power must be between {self._min_power} and {self._max_power}",
            )

    def _get_state_or_404(self, microwave_id: int) -> MicrowaveState:
        state = self._microwaves.get(microwave_id)
        if state is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="microwave not found",
            )
        return state

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC)


settings = get_settings()
microwave_service = MicrowaveService(
    initial_count=settings.initial_microwave_count,
    default_power=settings.default_microwave_power,
    min_power=settings.min_microwave_power,
    max_power=settings.max_microwave_power,
)
