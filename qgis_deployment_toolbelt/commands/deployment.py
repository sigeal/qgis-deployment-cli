#! python3  # noqa: E265

"""
    Sub-command in charge of running the main logic.

    Author: Julien M. (https://github.com/guts)
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import argparse
import logging
from os import environ, getenv
from pathlib import Path

from qgis_deployment_toolbelt.constants import get_qdt_working_directory
from qgis_deployment_toolbelt.jobs import JobsOrchestrator
from qgis_deployment_toolbelt.scenarios import ScenarioReader
from qgis_deployment_toolbelt.utils.bouncer import exit_cli_error, exit_cli_success
from qgis_deployment_toolbelt.utils.check_path import check_path

# submodules
from qgis_deployment_toolbelt.utils.file_downloader import download_remote_file_to_local

# #############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)


# ############################################################################
# ########## CLI #################
# ################################


def parser_main_deployment(
    subparser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Set the argument parser for deployment subcommand.

    Args:
        subparser (argparse.ArgumentParser): parser to set up

    Returns:
        argparse.ArgumentParser: parser ready to use
    """
    subparser.add_argument(
        "-s",
        "--scenario",
        help="Emplacement du fichier local.",
        default=getenv("QDT_SCENARIO_PATH", Path("./scenario.qdt.yml")),
        type=str,
        dest="scenario_filepath",
    )

    subparser.set_defaults(func=run)

    return subparser


# ############################################################################
# ########## MAIN ################
# ################################


def run(args: argparse.Namespace):
    """Run the main logic.

    Args:
        args (argparse.Namespace): arguments passed to the subcommand
    """
    logger.debug(f"Running {args.command} with {args}")

    # check if scenario file is local or remote
    if isinstance(args.scenario_filepath, str) and args.scenario_filepath.startswith(
        ("http",)
    ):
        args.scenario_filepath = download_remote_file_to_local(
            remote_url_to_download=args.scenario_filepath,
            local_file_path=Path("./downloaded_scenario.qdt.yml"),
        )

    # checks
    check_path(
        input_path=args.scenario_filepath,
        must_be_a_file=True,
        must_be_readable=True,
        must_exists=True,
    )

    # -- Load and validate scenario --
    scenario = ScenarioReader(in_yaml=Path(args.scenario_filepath))

    # Check the validity of the scenario
    scenario_validity = scenario.validate_scenario()
    if not scenario_validity[0]:
        result_scenario_validity = (
            "Scenario validation failed. Please check the scenario file."
            "\nValidation report:\n- {}".format("\n- ".join(scenario_validity[1]))
        )
        exit_cli_error(result_scenario_validity)

    # -- Run --

    # Use metadata to inform which scenario is running
    logger.info(
        "Running scenario: {title} ({id}). {description}".format(**scenario.metadata)
    )

    # Set environment vars for the scenario
    for var, value in scenario.settings.items():
        if value is not None:
            logger.debug(f"Setting environment variable QDT_{var} = {value}.")
            environ[f"QDT_{var}"] = str(value)
        else:
            logger.debug(f"Ignored None value: {var}.")

    qdt_local_working_folder = get_qdt_working_directory(
        specific_value=scenario.settings.get("LOCAL_QDT_WORKDIR"),
        identifier=scenario.metadata.get("id"),
    )
    logger.info(f"QDT working folder: " f"{qdt_local_working_folder}")

    # -- STEPS JOBS
    steps_ok = []
    orchestrator = JobsOrchestrator()

    # filter out unrecognized jobs
    for step in scenario.steps:
        if step.get("uses") not in orchestrator.jobs_ids:
            logger.warning(f"{step.get('uses')} not found in available jobs. Skipping.")
            continue
        else:
            steps_ok.append(step)

    # run job
    for step in steps_ok:
        logger.info(f"Running step: {step.get('uses')}")
        try:
            job = orchestrator.init_job_class_from_id(
                job_id=step.get("uses"), options=step.get("with")
            )
            job.run()
        except Exception as err:
            exit_cli_error(err)

    # exit nicely
    exit_cli_success("Deployment achieved!")
