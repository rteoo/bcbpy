"""Release promotion tests use a command recorder; no GitHub or Git mutation occurs."""
import importlib.util
import os
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "release.py"
spec = importlib.util.spec_from_file_location("release_flow", SCRIPT)
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseFlowTests(unittest.TestCase):
    def setUp(self):
        self.original_cwd = Path.cwd()
        self.addCleanup(os.chdir, self.original_cwd)
        os.chdir(release.RELEASE_ROOT)
        self.tag = "v" + release.manifest_version()
        self.head = "a" * 40
        self.calls = []
        self.mode = "ok"
        self.gates = 0
        self.confirmed = False
        self.pushed = False
        self.start_patch(patch.object(release.subprocess, "run", side_effect=self.record))
        self.prompt = self.start_patch(patch("builtins.input", side_effect=self.confirm))
        if hasattr(release, "clean_wheel_smoke"):
            self.start_patch(patch.object(release, "clean_wheel_smoke"))

    def start_patch(self, patcher):
        value = patcher.start()
        self.addCleanup(patcher.stop)
        return value

    def confirm(self, message):
        self.confirmed = True
        return self.tag if self.mode != "unconfirmed" else "no"

    def record(self, argv, **kwargs):
        argv = tuple(str(arg) for arg in argv)
        self.calls.append(argv)
        if argv[:2] == ("git", "push"):
            self.pushed = True
        status, out, err = 0, "", ""
        if argv[:3] == ("git", "remote", "get-url"):
            out = ("https://evil.example/github.com/" if self.mode == "wronghost" else
                   "https://github.com/") + release.REPO + ".git"
        elif argv[:3] == ("git", "branch", "--show-current"):
            out = "topic" if self.mode == "branch" else "main"
        elif argv[:3] == ("git", "status", "--porcelain"):
            out = ("?? release.tmp" if self.mode == "untracked" else
                   " M code.py" if self.mode == "dirty" or (self.mode == "gate_dirty" and self.gates) else "")
        elif argv[:2] == ("git", "fetch") and self.mode == "gitfail":
            status = 1
        elif argv[:2] == ("git", "rev-parse"):
            out = self.head
            if argv[2] == "origin/main" and self.mode == "upstream":
                out = "b" * 40
            if self.mode == "moved" and self.gates:
                out = "b" * 40
            if self.mode == "prompt_move" and self.confirmed:
                out = "b" * 40
            if argv[2].endswith("^{commit}") and self.mode == "localconflict":
                out = "b" * 40
        elif argv[:2] == ("git", "ls-remote"):
            if self.mode == "postpush":
                out = ("b" if self.pushed else "") * 40
                if self.pushed:
                    out += "\trefs/tags/" + self.tag
            elif self.pushed:
                out = self.head + "\trefs/tags/" + self.tag
            elif self.mode == "remoteconflict":
                out = "b" * 40 + "\trefs/tags/" + self.tag
            if self.mode == "annotated":
                out = ("c" * 40 + "\trefs/tags/" + self.tag + "\n" +
                       self.head + "\trefs/tags/" + self.tag + "^{}")
        elif argv[:2] == ("git", "for-each-ref") and self.mode == "localconflict":
            out = "c" * 40
        elif argv[:2] == ("gh", "api"):
            out = release.REPO
        elif argv[:3] == ("gh", "release", "view"):
            status, err = 1, "release not found"
            if self.mode == "auth":
                err = "authentication failed"
            elif self.mode == "released":
                status = 0
        elif argv in tuple(tuple(str(arg) for arg in gate) for gate in release.GATES):
            self.gates += 1
            if self.mode == "gatefail":
                status = 1
        return subprocess.CompletedProcess(argv, status, out, err)

    def assert_no_publication(self):
        self.assertFalse(any(
            call[:2] in (("git", "tag"), ("git", "push")) or
            call[:3] == ("gh", "release", "create") for call in self.calls))

    def test_dry_run_runs_every_gate_without_prompt_or_publication(self):
        self.assertEqual(release.main(["--tag", self.tag, "--dry-run"]), 0)
        self.assertEqual(self.gates, len(release.GATES))
        self.prompt.assert_not_called()
        self.assert_no_publication()

    def test_invalid_flag_is_rejected_before_any_command(self):
        with self.assertRaises(SystemExit):
            release.main(["--tag", self.tag, "--dry"])
        self.assertEqual(self.calls, [])

    def test_manifest_mismatch_is_rejected_before_any_command(self):
        with self.assertRaises(RuntimeError):
            release.main(["--tag", "v9999.9999.9999", "--dry-run"])
        self.assertEqual(self.calls, [])

    def test_bad_checkouts_fail_before_any_gate(self):
        for mode in ("wronghost", "branch", "dirty", "untracked", "upstream", "gitfail"):
            with self.subTest(mode=mode):
                self.mode, self.gates = mode, 0
                with self.assertRaises(RuntimeError):
                    release.main(["--tag", self.tag, "--dry-run"])
                self.assertEqual(self.gates, 0)
                self.assert_no_publication()

    def test_tag_conflicts_stop_publication(self):
        for mode in ("remoteconflict", "localconflict"):
            self.mode = mode
            with self.assertRaises(RuntimeError):
                release.main(["--tag", self.tag, "--dry-run"])
            self.assert_no_publication()

    def test_annotated_tag_resolves_to_its_commit(self):
        self.mode = "annotated"
        self.assertEqual(release.main(["--tag", self.tag, "--dry-run"]), 0)
        self.assert_no_publication()

    def test_failed_gate_and_changed_checkout_stop_publication(self):
        for mode in ("gatefail", "gate_dirty", "moved"):
            with self.subTest(mode=mode):
                self.mode, self.gates = mode, 0
                with self.assertRaises(RuntimeError):
                    release.main(["--tag", self.tag, "--dry-run"])
                self.assert_no_publication()

    def test_auth_failure_and_existing_release_are_not_absence(self):
        for mode in ("auth", "released"):
            self.mode = mode
            with self.assertRaises(RuntimeError):
                release.main(["--tag", self.tag, "--dry-run"])
            self.assert_no_publication()

    def test_confirmation_is_required_and_candidate_is_rechecked(self):
        for mode in ("unconfirmed", "prompt_move"):
            self.mode, self.gates, self.confirmed = mode, 0, False
            with self.assertRaises(RuntimeError):
                release.main(["--tag", self.tag])
            self.assert_no_publication()

    def test_remote_tag_is_rechecked_before_release_creation(self):
        self.mode = "postpush"
        with self.assertRaises(RuntimeError):
            release.main(["--tag", self.tag])
        self.assertTrue(any(call[:2] == ("git", "push") for call in self.calls))
        self.assertFalse(any(call[:3] == ("gh", "release", "create") for call in self.calls))

    def test_tag_rejects_leading_zero_components(self):
        with self.assertRaises(ValueError):
            release.tag_version("v01.2.3")

    def test_confirmed_flow_publishes_only_the_immutable_tag(self):
        self.assertEqual(release.main(["--tag", self.tag]), 0)
        pushes = [call for call in self.calls if call[:2] == ("git", "push")]
        self.assertEqual(pushes, [("git", "push", "origin",
                                  f"refs/tags/{self.tag}:refs/tags/{self.tag}")])
        created = [call for call in self.calls if call[:3] == ("gh", "release", "create")]
        self.assertEqual(len(created), 1)
        self.assertEqual(created[0][created[0].index("--target") + 1], self.head)


if __name__ == "__main__":
    unittest.main()
