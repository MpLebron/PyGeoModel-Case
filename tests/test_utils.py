import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

class ResponseStub:
    def __init__(self, status_code):
        self.status_code = status_code


class ResultStub:
    def __init__(self, outcome):
        self.outcome = outcome
        self.output_dir = None

    def save(self, output_dir):
        self.output_dir = output_dir
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


class DownloadError(Exception):
    pass


class EnsureOutputsTests(unittest.TestCase):
    def test_uses_live_outputs_when_download_succeeds(self):
        from utils import ensure_outputs

        result = ResultStub(["data/result/live_run/result.zip"])

        saved_files = ensure_outputs(result, output_dir="data/result/live_run")

        self.assertEqual(saved_files, ["data/result/live_run/result.zip"])
        self.assertEqual(result.output_dir, "data/result/live_run")

    def test_uses_archived_case_outputs_for_binder_412_without_printing(self):
        from utils import ensure_outputs

        error = DownloadError("412 Precondition Failed")
        error.response = ResponseStub(412)

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            archive_dir = root / "data" / "result"
            archive_dir.mkdir(parents=True)
            (archive_dir / "roof_results_with_power_generation.shp").write_text("")
            (archive_dir / "roof_results_with_power_generation.dbf").write_text("")

            stream = io.StringIO()
            with redirect_stdout(stream):
                saved_files = ensure_outputs(
                    ResultStub(error),
                    output_dir=root / "data" / "result" / "live_run",
                    archived_pattern=root / "data" / "result" / "roof_results_with_power_generation.*",
                )

        self.assertEqual(
            saved_files,
            [
                str(archive_dir / "roof_results_with_power_generation.dbf"),
                str(archive_dir / "roof_results_with_power_generation.shp"),
            ],
        )
        self.assertEqual(stream.getvalue(), "")

    def test_reraises_non_binder_download_errors(self):
        from utils import ensure_outputs

        error = DownloadError("500 Server Error")
        error.response = ResponseStub(500)

        with self.assertRaises(DownloadError):
            ensure_outputs(ResultStub(error), output_dir="data/result/live_run")


if __name__ == "__main__":
    unittest.main()
