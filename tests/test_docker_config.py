import json
from pathlib import Path
import shutil
import subprocess
import unittest

import yaml


@unittest.skipUnless(Path("Dockerfile").is_file(), "Deployment sources are not included in the runtime image")
class TestDockerFiles(unittest.TestCase):
    def test_runtime_does_not_copy_secrets_or_local_storage(self):
        dockerfile = Path("Dockerfile").read_text()
        self.assertIn("USER hydromel", dockerfile)
        self.assertIn('ENTRYPOINT ["python3", "bot.py"]', dockerfile)
        self.assertIn('CMD ["webserver"]', dockerfile)
        self.assertIn("COPY --from=frontend", dockerfile)
        self.assertNotIn("COPY . ", dockerfile)
        ignored = Path(".dockerignore").read_text().splitlines()
        for pattern in ("**/.env", "**/.env.*", "storages", "env", "**/node_modules"):
            self.assertIn(pattern, ignored)

    def test_publish_workflow_does_not_push_pull_requests_or_replace_latest_on_tags(self):
        workflow = yaml.safe_load(
            Path(".github/workflows/docker-publish.yml").read_text())
        steps = workflow["jobs"]["docker"]["steps"]
        build = next(step for step in steps if step.get(
            "uses", "").startswith("docker/build-push-action"))
        self.assertEqual(build["with"]["push"],
                         "${{ github.event_name != 'pull_request' }}")
        metadata = next(step for step in steps if step.get(
            "uses", "").startswith("docker/metadata-action"))
        self.assertEqual(metadata["with"]["flavor"], "latest=false")
        self.assertIn(
            "value=latest,enable=${{ github.ref == 'refs/heads/main' }}", metadata["with"]["tags"])
        self.assertIn("type=ref,event=tag", metadata["with"]["tags"])


@unittest.skipUnless(shutil.which("docker"), "Docker CLI is not installed")
class TestComposeConfiguration(unittest.TestCase):
    def setUp(self):
        result = subprocess.run(
            ["docker", "compose", "version"], capture_output=True)
        if result.returncode:
            self.skipTest("Docker Compose is not installed")

    def test_sqlite_and_mariadb_stack_configuration(self):
        base = ["docker", "compose", "--env-file",
                "docs/docker/.env.example", "-f", "docs/docker/compose.yml"]
        for backend, extra in (("sqlite", []), ("mariadb", ["-f", "docs/docker/compose.mariadb.yml"])):
            with self.subTest(backend=backend):
                result = subprocess.run(
                    base + extra + ["config", "--no-env-resolution", "--format", "json"], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                services = json.loads(result.stdout)["services"]
                for name in ("migrate", "barman", "menestrel", "archiveuse", "webserver"):
                    service = services[name]
                    self.assertEqual(
                        service["environment"]["DB_TYPE"], backend)
                    self.assertEqual(
                        service["environment"]["WEB_HOST"], "0.0.0.0")
                    self.assertEqual(
                        service["environment"]["SQL_LOG_FILE"], "/app/storages/sql.log")
                    self.assertEqual(
                        service["volumes"][0]["source"], "hydromel-data")
                    if name != "migrate":
                        self.assertEqual(
                            service["depends_on"]["migrate"]["condition"], "service_completed_successfully")
                if backend == "mariadb":
                    self.assertEqual(
                        services["migrate"]["depends_on"]["database"]["condition"], "service_healthy")
