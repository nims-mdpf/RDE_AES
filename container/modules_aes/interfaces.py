from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Generic, TypeVar

from rdetoolkit.models.rde2types import MetaType, RepeatedMetaType
from rdetoolkit.rde2util import Meta

T = TypeVar("T")


class IInputFileParser(ABC):
    """Abstract base class (interface) for input file parsers.

    This interface defines the contract that input file parser
    implementations must follow. The parsers are expected to read files
    from a specified path, parse the contents of the files, and provide
    options for saving the parsed data.

    Methods:
        read: A method expecting a file path and responsible for reading a file.

    Example implementations of this interface could be for parsing files
    of different formats like CSV, Excel, JSON, etc.

    """

    @abstractmethod
    def read_para_file(self, raw_file_path_para: Path) -> tuple[dict[str, Any], str | None]:
        """Read parameter file and return metadata dictionary and data mode."""
        raise NotImplementedError

    @abstractmethod
    def read_data_spe_file(self, raw_file_path_data: Path, data_mode: str, dct_hdr: dict[str, str | int | float | list[Any] | bool | dict[str, str]]) -> list[list[int]]:
        """Read data file and return data object."""
        raise NotImplementedError


class IStructuredDataProcesser(ABC):
    """Abstract base class (interface) for structured data parsers.

    This interface defines the contract that structured data parser
    implementations must follow. The parsers are expected to transform
    structured data, such as DataFrame, into various desired output formats.

    Methods:
        to_csv: A method that saves the given data to a CSV file.

    Implementers of this interface could transform data into various
    formats like CSV, Excel, JSON, etc.

    """

    @abstractmethod
    def write_fnd_csv_file_survey(self, csv_file_path: Path, dct_hdr: dict[str, str | int | float | list[Any] | bool | dict[str, str]], data_obj: list[list[int]]) -> None:
        """Write AES survey mode data to a CSV file."""
        raise NotImplementedError

    @abstractmethod
    def write_fnd_csv_file_narrow(self, csv_file_path: Path, dct_hdr: dict[str, str | int | float | list[Any] | bool | dict[str, str]], data_obj: list[list[int]]) -> None:
        """Write AES narrow mode data to a CSV file."""
        raise NotImplementedError


class IMetaParser(ABC, Generic[T]):
    """Abstract base class (interface) for meta information parsers.

    This interface defines the contract that meta information parser
    implementations must follow. The parsers are expected to save the
    constant and repeated meta information to a specified path.

    Method:
        save_meta: Saves the constant and repeated meta information to a specified path.
        parse: This method returns two types of metadata: const_meta_info and repeated_meta_info.
    """

    @abstractmethod
    def parse(self, dct_hdr: dict, data_mode: str | None) -> tuple[MetaType, RepeatedMetaType]:
        """Parse."""
        raise NotImplementedError

    @abstractmethod
    def save_meta(
        self,
        save_path: Path,
        meta_obj: Meta | None = None,
        *,
        const_meta_info: MetaType | None = None,
        repeated_meta_info: RepeatedMetaType | None = None,
    ) -> None:
        """Save meta information to a specified path."""
        raise NotImplementedError


class IGraphPlotter(ABC, Generic[T]):
    """Abstract base class (interface) for graph plotting implementations.

    This interface defines the contract that graph plotting
    implementations must follow. The implementations are expected
    to be capable of plotting a simple graph using a given pandas DataFrame.

    Methods:
        simple_plot: Plots a simple graph using the provided pandas DataFrame.

    """

    @abstractmethod
    def plot_corrected_original(self, csv_path: Path, out_dir_main_img: Path, out_dir_other_img: Path) -> None:
        """Plot corrected and original data from a CSV file."""
        raise NotImplementedError
