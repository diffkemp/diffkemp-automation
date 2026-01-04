"""File for saving results to SqLite DB."""
import logging
from typing import List, Optional, Sequence

from sqlalchemy import (Boolean, Column, DateTime, Enum, ForeignKey, Integer,
                        String, Table, create_engine)
from sqlalchemy.orm import registry, relationship, sessionmaker

from automation.models.results.commits import ResultCommit
from automation.models.results.function import FunctionResult
from automation.models.results.result import ResultBase
from automation.models.results.results import ResultSubType
from automation.models.results.types import (ComparisonStatus,
                                             DiffKempResultType)
from automation.models.results.versions import ResultVersion
from automation.utils import RESULTS_DB_PATH

mapper_registry = registry()

# Single table for both ResultCommit and ResultVersion
results_table = Table(
    "results",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False),
    Column("config_file_name", String, nullable=False),
    Column("diffkemp_sha", String, nullable=False),
    Column("equal", Integer, nullable=False),
    Column("non_equal", Integer, nullable=False),
    Column("unknown", Integer, nullable=False),
    Column("error", Integer, nullable=False),
    Column("no_differing", Integer),
    Column("date", DateTime),
    Column("comparison_status", Enum(ComparisonStatus)),
    # Column for distinguishing between ResultCommit and ResultVersion
    Column("type", String(20)),
    # ResultCommit specific columns
    Column("commit", String),
    Column("all_diffs_matched", Boolean),
    # ResultVersion specific columns
    Column("old_tag", String),
    Column("new_tag", String),
)

function_results_table = Table(
    "function_results",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False),
    Column("diffkemp_result", Enum(DiffKempResultType), nullable=False),
    Column("result_id", Integer, ForeignKey("results.id"), nullable=False),
)

mapper_registry.map_imperatively(FunctionResult, function_results_table)
mapper_registry.map_imperatively(
    ResultBase,  # type: ignore
    results_table,
    properties={
        "_functions_list": relationship(FunctionResult)
    },
    polymorphic_on=results_table.c.type,
    polymorphic_identity="base",
)
mapper_registry.map_imperatively(
    ResultCommit,
    inherits=ResultBase,
    polymorphic_identity="commit"
)
mapper_registry.map_imperatively(
    ResultVersion,
    inherits=ResultBase,
    polymorphic_identity="version"
)
engine = create_engine(
    f"sqlite:///{RESULTS_DB_PATH}",
    echo=logging.root.isEnabledFor(logging.DEBUG),
)
mapper_registry.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


class ResultsRepo:
    """Repository for working with results in DB."""
    def add_multiple(
        self,
        results_list: Sequence[ResultSubType],
    ) -> None:
        """Add multiple results to DB."""
        for result in results_list:
            functions_map = result.functions  # type: ignore
            functions_list = list(functions_map.values())
            result._functions_list = functions_list  # type: ignore

        with Session() as session:
            session.add_all(results_list)
            session.commit()
            # Expunge objects to detach from session before cleanup
            session.expunge_all()

    def add(self, result: ResultSubType) -> None:
        """Add result to database."""
        functions_list = list(result.functions.values())  # type: ignore
        result._functions_list = functions_list  # type: ignore

        with Session() as session:
            session.add(result)
            session.commit()
            # Expunge object to detach from session before cleanup
            session.expunge(result)

    def get_commits(
        self,
        config_file_name: Optional[str] = None,
        commit: Optional[str] = None,
        diffkemp_sha: Optional[str] = None,
    ) -> List[ResultCommit]:
        """Returns list of results for commits from DB."""
        with Session() as session:
            query = session.query(ResultCommit)
            if config_file_name:
                query = query.where(
                     results_table.c.config_file_name == config_file_name)
            if commit:
                query = query.where(
                     results_table.c.commit == commit)
            if diffkemp_sha:
                query = query.where(
                     results_table.c.diffkemp_sha == diffkemp_sha)
            results = query.order_by(results_table.c.date.desc()) \
                           .all()
            self._results_fun_list_to_dict(results)
        return results

    def get_versions(
        self,
        config_file_name: Optional[str] = None,
        old_tag: Optional[str] = None,
        new_tag: Optional[str] = None,
        diffkemp_sha: Optional[str] = None,
    ) -> List[ResultVersion]:
        """Returns list of results for versions from DB."""
        with Session() as session:
            query = session.query(ResultVersion)
            if config_file_name:
                query = query.where(
                     results_table.c.config_file_name == config_file_name)
            if old_tag:
                query = query.where(
                     results_table.c.old_tag == old_tag)
            if new_tag:
                query = query.where(
                     results_table.c.new_tag == new_tag)
            if diffkemp_sha:
                query = query.where(
                     results_table.c.diffkemp_sha == diffkemp_sha)
            results = query.order_by(results_table.c.date.desc()) \
                           .all()
            self._results_fun_list_to_dict(results)
        return results

    def _results_fun_list_to_dict(
        self,
        results: Sequence[ResultSubType],
    ) -> None:
        """Transform DB saved functions."""
        for result in results:
            self._result_fun_list_to_dict(result)

    def _result_fun_list_to_dict(self, result: ResultSubType | None) -> None:
        if result is None:
            return
        if (hasattr(result, "_functions_list")
                and result._functions_list):  # type: ignore
            result.functions = {
                func.name: func
                for func in result._functions_list  # type: ignore
            }
            # Safe deletion
            if hasattr(result, "_functions_list"):
                delattr(result, "_functions_list")
