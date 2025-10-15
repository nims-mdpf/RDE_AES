from __future__ import annotations

from rdetoolkit.errors import catch_exception_with_message
from rdetoolkit.models.rde2types import RdeInputDirPaths, RdeOutputResourcePath
from rdetoolkit.rde2util import Meta

from modules_aes.graph_handler import GraphPlotter
from modules_aes.inputfile_handler import FileReader
from modules_aes.meta_handler import MetaParser
from modules_aes.structured_handler import StructuredDataProcesser


class AESProcessingCoordinator:
    """Coordinator class for managing AES processing modules.

    This class serves as a coordinator for AES processing modules, facilitating the use of
    various components such as file reading, metadata parsing, graph plotting, and structured
    data processing. It is responsible for managing these components and providing an organized
    way to execute the required tasks.

    Args:
        file_reader (FileReader): An instance of the file reader component.
        meta_parser (MetaParser): An instance of the metadata parsing component.
        graph_plotter (GraphPlotter): An instance of the graph plotting component.
        structured_processer (StructuredDataProcesser): An instance of the structured data
                                                        processing component.

    Attributes:
        file_reader (FileReader): The file reader component for reading input data.
        meta_parser (MetaParser): The metadata parsing component for processing metadata.
        graph_plotter (GraphPlotter): The graph plotting component for visualization.
        structured_processer (StructuredDataProcesser): The component for processing structured data.

    Example:
        custom_module = AESProcessingCoordinator(FileReader(), MetaParser(), GraphPlotter(), StructuredDataProcesser())
        # Note: The method 'execute_processing' hasn't been defined in the provided code,
        #       so its usage is just an example here.
        custom_module.execute_processing(srcpaths, resource_paths)

    """

    def __init__(
        self,
        file_reader: FileReader,
        meta_parser: MetaParser,
        graph_plotter: GraphPlotter,
        structured_processer: StructuredDataProcesser,
    ):
        self.file_reader = file_reader
        self.meta_parser = meta_parser
        self.graph_plotter = graph_plotter
        self.structured_processer = structured_processer


@catch_exception_with_message()
def dataset(
    srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath,
) -> None:
    """Process structured text files, extract metadata, and generate visualizations.

    Handles structured text parsing, metadata extraction, CSV generation, and graph creation.
    Additional processing steps can be implemented depending on project needs.

    Args:
        srcpaths (RdeInputDirPaths): Paths to input resources for processing.
        resource_paths (RdeOutputResourcePath): Paths to output resources for saving results.

    Returns:
        None

    Note:
        The actual function names and processing details may vary depending on the project.

    """
    rawfiles = resource_paths.rawfiles

    # Initialization
    raw_file_path_id = raw_file_path_para = raw_file_path_data = csv_file_path = None

    for path in rawfiles:
        if path.name == "id":
            raw_file_path_id = path
            csv_file_path = resource_paths.struct.joinpath(f"{raw_file_path_id.name}.csv")
        elif path.name == "para":
            raw_file_path_para = path
        elif path.name == "data":
            raw_file_path_data = path

    if raw_file_path_para is None or raw_file_path_data is None or csv_file_path is None:
        error_msg = "Missing required input files in resource_paths.rawfiles."
        raise ValueError(error_msg)

    metadata_def_path = srcpaths.tasksupport.joinpath("metadata-def.json")
    default_val_path = srcpaths.tasksupport.joinpath("default_value.csv")

    module = AESProcessingCoordinator(
        FileReader(),
        MetaParser(
            metadata_def_json_path=metadata_def_path,
            meta_default_vals_file_path=default_val_path,
        ),
        GraphPlotter(),
        StructuredDataProcesser(),
    )

    # Read Input File
    dct_hdr = data_mode = None
    dct_hdr, data_mode = module.file_reader.read_para_file(raw_file_path_para)

    if data_mode is None:
        error_msg = "data_mode is None. 'read_para_file' did not return a valid mode."
        raise ValueError(error_msg)

    data_obj = module.file_reader.read_data_spe_file(raw_file_path_data, data_mode, dct_hdr)

    if data_mode == "AES-survey":
        module.structured_processer.write_fnd_csv_file_survey(
            csv_file_path, dct_hdr, data_obj,
        )
    elif data_mode == "AES-narrow":
        module.structured_processer.write_fnd_csv_file_narrow(
            csv_file_path, dct_hdr, data_obj,
        )

    const_meta_info, repeated_meta_info = module.meta_parser.parse(dct_hdr, data_mode)
    module.meta_parser.save_meta(
        resource_paths.meta.joinpath("metadata.json"),
        Meta(metadata_def_path),
        const_meta_info=const_meta_info,
        repeated_meta_info=repeated_meta_info,
    )

    module.graph_plotter.plot_corrected_original(
        csv_file_path,
        resource_paths.main_image,
        resource_paths.other_image,
    )
