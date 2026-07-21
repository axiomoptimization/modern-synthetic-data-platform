from __future__ import annotations

import logging
from uuid import UUID

import polars as pl
from pydantic import BaseModel, ValidationError

from synthetic_data_platform.config import Settings
from synthetic_data_platform.models.agent import Agent
from synthetic_data_platform.models.claim import Claim
from synthetic_data_platform.models.customer import Customer
from synthetic_data_platform.models.payment import Payment
from synthetic_data_platform.models.policy import Policy
from synthetic_data_platform.telemetry.models import PipelineRun
from synthetic_data_platform.writers.parquet_writer import ParquetWriter


class ValidationService:
    """Reads Bronze Parquet data, applies data quality checks, and writes
    validated, deduplicated output to the Silver layer.

    Invalid or unreferenceable rows are dropped and recorded as telemetry
    warnings rather than halting the pipeline.
    """

    def validate_all(self, settings: Settings, run: PipelineRun, logger: logging.Logger) -> None:
        customer_ids = self.validate_entity(
            settings, run, logger, Customer, "customers", "customer_id"
        )
        agent_ids = self.validate_entity(settings, run, logger, Agent, "agents", "agent_id")
        policy_ids = self.validate_entity(
            settings,
            run,
            logger,
            Policy,
            "policies",
            "policy_id",
            foreign_keys={"customer_id": customer_ids, "agent_id": agent_ids},
        )
        self.validate_entity(
            settings,
            run,
            logger,
            Claim,
            "claims",
            "claim_id",
            foreign_keys={"policy_id": policy_ids},
        )
        self.validate_entity(
            settings,
            run,
            logger,
            Payment,
            "payments",
            "payment_id",
            foreign_keys={"policy_id": policy_ids},
        )

    def validate_entity(
        self,
        settings: Settings,
        run: PipelineRun,
        logger: logging.Logger,
        model_cls: type[BaseModel],
        file_name: str,
        primary_key: str,
        foreign_keys: dict[str, set[UUID]] | None = None,
    ) -> set[UUID]:
        bronze_path = settings.bronze_dir / f"{file_name}.parquet"
        if not bronze_path.exists():
            self._warn(run, logger, f"{file_name}: Bronze file not found, skipping validation")
            return set()

        rows = pl.read_parquet(bronze_path).to_dicts()
        valid_records: list[BaseModel] = []
        seen_keys: set[UUID] = set()

        for row in rows:
            try:
                record = model_cls(**row)
            except ValidationError as exc:
                self._warn(
                    run, logger, f"{file_name}: skipped invalid row ({exc.error_count()} error(s))"
                )
                continue

            key = getattr(record, primary_key)
            if key in seen_keys:
                self._warn(run, logger, f"{file_name}: skipped duplicate {primary_key} {key}")
                continue

            if foreign_keys and not self._references_are_valid(
                record, foreign_keys, file_name, run, logger
            ):
                continue

            seen_keys.add(key)
            valid_records.append(record)

        if valid_records:
            output_path = ParquetWriter().write(valid_records, settings.silver_dir, file_name)
            run.record_row_count(file_name, len(valid_records))
            run.add_output_location(str(output_path))
        else:
            self._warn(run, logger, f"{file_name}: no valid rows to write to Silver layer")

        return seen_keys

    def _references_are_valid(
        self,
        record: BaseModel,
        foreign_keys: dict[str, set[UUID]],
        file_name: str,
        run: PipelineRun,
        logger: logging.Logger,
    ) -> bool:
        for fk_field, valid_ids in foreign_keys.items():
            fk_value = getattr(record, fk_field)
            if fk_value not in valid_ids:
                message = f"{file_name}: skipped row with unknown {fk_field} {fk_value}"
                self._warn(run, logger, message)
                return False
        return True

    @staticmethod
    def _warn(run: PipelineRun, logger: logging.Logger, message: str) -> None:
        run.add_warning(message)
        logger.warning(message, extra={"run_id": run.run_id})
