from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import AbstractContextManager

from readme_gen.repository.models import RepositoryContext


class RepositorySource(ABC):
    """
    Abstract source of a repository.

    A repository source resolves some user-provided input into a temporary or
    permanent local repository directory that can be consumed by the existing
    scanner.
    """

    @abstractmethod
    def open(self) -> AbstractContextManager[RepositoryContext]:
        """
        Open the repository source and return a context manager.

        Local repositories simply expose their existing directory.

        Remote repositories may create temporary files that must remain alive
        until the context manager exits.
        """
        raise NotImplementedError