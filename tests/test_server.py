import sys
import os
import shutil
import tempfile
import unittest
import git
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from mcp_server_git import server

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class TestGitTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_path = os.environ.get("TEST_GIT_REPO")
        logger.info(f"setUpClass: TEST_GIT_REPO={cls.repo_path}")

    def setUp(self):
        if self.repo_path:
            logger.info(f"Using existing repo: {self.repo_path}")
            self.test_dir = self.repo_path
            self.repo = git.Repo(self.test_dir)
        else:
            logger.info("Creating temporary test repo...")
            self.test_dir = tempfile.mkdtemp()
            self.repo = git.Repo.init(self.test_dir)
            file_path = os.path.join(self.test_dir, "test.txt")
            with open(file_path, "w") as f:
                f.write("hello world\n")
            self.repo.index.add([file_path])
            self.repo.index.commit("init commit")
            logger.info(f"Temporary repo created at {self.test_dir}")

    def tearDown(self):
        if not self.repo_path:
            logger.info(f"Removing temporary repo: {self.test_dir}")
            shutil.rmtree(self.test_dir)
        else:
            logger.info(f"tearDown: Skipping removal for existing repo: {self.test_dir}")

    def test_git_log(self):
        logger.info("Running test_git_log...")
        logs = server.git_log(self.repo, max_count=1)
        logger.info(f"git_log output: {logs}")
        self.assertTrue(len(logs) > 0)
        logger.info("test_git_log passed.")

    def test_git_status(self):
        logger.info("Running test_git_status...")
        status = server.git_status(self.repo)
        logger.info(f"git_status output: {status}")
        self.assertIn("On branch", status)
        logger.info("test_git_status passed.")

    def test_git_diff_unstaged(self):
        logger.info("Running test_git_diff_unstaged...")
        file_path = os.path.join(self.test_dir, "test.txt")
        with open(file_path, "a") as f:
            f.write("new line\n")
        logger.info(f"Appended 'new line' to {file_path}")
        diff = server.git_diff_unstaged(self.repo)
        logger.info(f"git_diff_unstaged output: {diff}")
        self.assertIn("+new line", diff)
        logger.info("test_git_diff_unstaged passed.")

    def test_git_add_and_commit(self):
        logger.info("Running test_git_add_and_commit...")
        new_file = os.path.join(self.test_dir, "new.txt")
        with open(new_file, "w") as f:
            f.write("abc\n")
        logger.info(f"Created new file: {new_file}")
        server.git_add(self.repo, [new_file])
        logger.info(f"Added {new_file} to staging area.")
        msg = "add new.txt"
        result = server.git_commit(self.repo, msg)
        logger.info(f"git_commit output: {result}")
        self.assertIn("Changes committed successfully", result)
        logs = server.git_log(self.repo, max_count=2)
        logger.info(f"git_log after commit: {logs}")
        self.assertIn(msg, "".join(logs))
        logger.info("test_git_add_and_commit passed.")

if __name__ == "__main__":
    logger.info("Starting unittest main...")
    unittest.main()
