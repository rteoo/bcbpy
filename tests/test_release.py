import importlib.util
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location("release_helper", Path(__file__).parents[1] / "release.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)

class ReleaseTests(TestCase):
    def test_strict_tag_and_fake_git_command(self):
        self.assertEqual(release.tag_version("v2.3.4"), "2.3.4")
        result = Mock(returncode=0, stdout="deadbeef\n")
        with patch.object(release.subprocess, "run", return_value=result) as run:
            self.assertEqual(release.command("git", "rev-parse", "HEAD"), "deadbeef")
        run.assert_called_once()

    def test_dirty_checkout_refuses_before_release(self):
        def fake(*args, capture=True):
            if args[:3] == ("git", "remote", "get-url"): return "https://github.com/rteoo/bcbpy.git"
            if args[:3] == ("git", "branch", "--show-current"): return "main"
            if args[:3] == ("git", "status", "--porcelain"): return " M tracked.py"
            return ""
        with patch.object(release, "command", side_effect=fake), patch.object(release.subprocess, "run") as run:
            with self.assertRaisesRegex(RuntimeError, "checkout changes"):
                release.main(["--tag", f"v{release.manifest_version()}", "--dry-run"])
        run.assert_not_called()

    def _fake_commands(self, calls, *, tag_output="", fail_gate=False):
        head = "a" * 40
        tag = "v" + release.manifest_version()
        pushed = False
        def fake(*args, capture=True):
            nonlocal pushed
            calls.append(args)
            if args[:2] == ("git", "push"):
                pushed = True
            if args[:3] == ("git", "remote", "get-url"): return f"https://github.com/{release.REPO}.git"
            if args[:3] == ("git", "branch", "--show-current"): return "main"
            if args[:3] == ("git", "status", "--porcelain"): return ""
            if args[:3] == ("git", "rev-parse", "HEAD"): return head
            if args[:3] == ("git", "rev-parse", "origin/main"): return head
            if args[:2] == ("git", "ls-remote"):
                return tag_output or (f"{head}\trefs/tags/{tag}\n" if pushed else "")
            if args[:2] == ("gh", "api"): return release.REPO
            if args[0] == release.sys.executable and fail_gate: raise RuntimeError("command failed: gate")
            return ""
        return fake, head

    def test_dry_run_and_failed_gate_never_mutate(self):
        for fail_gate in (False, True):
            calls=[]; fake, _ = self._fake_commands(calls, fail_gate=fail_gate)
            gh = Mock(returncode=1, stderr="HTTP 404 not found")
            with patch.object(release, "command", side_effect=fake), patch.object(release.subprocess, "run", return_value=gh), patch.object(release, "input", create=True):
                if fail_gate:
                    with self.assertRaisesRegex(RuntimeError, "gate"): release.main(["--tag", f"v{release.manifest_version()}", "--dry-run"])
                else:
                    self.assertEqual(release.main(["--tag", f"v{release.manifest_version()}", "--dry-run"]), 0)
            self.assertFalse(any(
                call[0:2] in (("git", "push"), ("git", "tag"))
                or call[0:3] == ("gh", "release", "create")
                for call in calls
            ))

    def test_tag_conflict_and_unconfirmed_refuse(self):
        tag=f"v{release.manifest_version()}"; calls=[]; fake, head=self._fake_commands(calls, tag_output="b"*40+"\trefs/tags/"+tag+"\n")
        with patch.object(release, "command", side_effect=fake), patch.object(release.subprocess, "run", return_value=Mock(returncode=1, stderr="404")):
            with self.assertRaisesRegex(RuntimeError, "does not point"): release.main(["--tag", tag, "--dry-run"])
        calls=[]; fake, _=self._fake_commands(calls)
        with patch.object(release, "command", side_effect=fake), patch.object(release.subprocess, "run", return_value=Mock(returncode=1, stderr="404")), patch("builtins.input", return_value="no"):
            with self.assertRaisesRegex(RuntimeError, "not confirmed"): release.main(["--tag", tag])
        self.assertFalse(any(call[0:2] == ("git", "push") for call in calls))

    def test_confirmed_flow_tags_pushes_and_targets_exact_commit(self):
        tag=f"v{release.manifest_version()}"; calls=[]; fake, head=self._fake_commands(calls)
        with patch.object(release, "command", side_effect=fake), patch.object(release.subprocess, "run", return_value=Mock(returncode=1, stderr="404")), patch("builtins.input", return_value=tag):
            self.assertEqual(release.main(["--tag", tag]), 0)
        self.assertIn(("git", "tag", "--annotate", tag, "--message", f"Release {tag}", head), calls)
        self.assertIn(("git", "push", "origin", f"refs/tags/{tag}:refs/tags/{tag}"), calls)
        self.assertIn(("gh", "release", "create", tag, "--repo", release.REPO, "--target", head, "--verify-tag", "--generate-notes", "--title", tag), calls)
