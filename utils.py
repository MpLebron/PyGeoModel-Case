from glob import glob


def ensure_outputs(
    result,
    output_dir="data/result/live_run",
    archived_pattern="data/result/roof_results_with_power_generation.*",
):
    """Prefer live OpenGMS outputs; use archived case outputs only when Binder cannot download them."""
    try:
        return result.save(output_dir=output_dir)
    except Exception as error:
        response = getattr(error, "response", None)
        if getattr(response, "status_code", None) != 412:
            raise

        archived_files = sorted(glob(str(archived_pattern)))
        if not archived_files:
            raise RuntimeError("Archived case outputs were not found.") from error
        return archived_files
