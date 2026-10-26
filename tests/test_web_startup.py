import json
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from fastapi import HTTPException
from mysql.connector.errors import DatabaseError

from libs.databases.models.application_model import ApplicationModel
from libs.utils.http_utils import HTTPUtils
from libs.utils.utils import Utils


middleware = Utils.import_module_from_path("startup_log_middleware", "http/middlewares/log_requests_middleware.py")
sessions = Utils.import_module_from_path("startup_sessions_controller", "http/controllers/sessions_controller.py")


class TestRequestErrorHandling(unittest.IsolatedAsyncioTestCase):
    async def test_original_exception_is_handled_without_lazy_mysql_attribute_error(self):
        with patch.object(middleware.Log, "info"), patch.object(middleware.Log, "error") as log:
            response = await middleware.log_requests(Mock(), AsyncMock(side_effect=RuntimeError("Original failure")))
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.body)["message"], "Original failure")
        self.assertIn("Original failure", log.call_args.args[0])

    async def test_mysql_errors_are_handled_by_imported_exception_class(self):
        with patch.object(middleware.Log, "info"), patch.object(middleware.Log, "error"):
            response = await middleware.log_requests(Mock(), AsyncMock(side_effect=DatabaseError("Database unavailable")))
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.body)["error"], "Database Error")

    async def test_normal_responses_are_preserved(self):
        expected = SimpleNamespace(status_code=200)
        with patch.object(middleware.Log, "info"):
            self.assertIs(await middleware.log_requests(Mock(), AsyncMock(return_value=expected)), expected)


class TestDiscordStartup(unittest.IsolatedAsyncioTestCase):
    async def test_guild_list_waits_for_ready_bot_before_building_projections(self):
        for bot in (None, Mock(is_ready=Mock(return_value=False))):
            with self.subTest(bot=bot), patch.object(ApplicationModel, "bot", bot, create=True), patch.object(
                HTTPUtils, "get_user_from_session", return_value=Mock()
            ), patch.object(sessions.GuildProjection, "from_guild") as project, self.assertRaises(HTTPException) as error:
                await sessions.guilds(Mock())
            self.assertEqual(error.exception.status_code, 503)
            self.assertEqual(error.exception.headers["Retry-After"], "3")
            project.assert_not_called()

    async def test_current_user_projection_waits_for_ready_bot(self):
        with patch.object(ApplicationModel, "bot", None, create=True), patch.object(HTTPUtils, "get_user_from_session", return_value=Mock()), patch.object(
            sessions.UserProjection, "from_user"
        ) as project, self.assertRaises(HTTPException) as error:
            await sessions.one(SimpleNamespace(query_params={}))
        self.assertEqual(error.exception.status_code, 503)
        project.assert_not_called()

    async def test_login_is_checked_before_discord_readiness(self):
        with patch.object(HTTPUtils, "get_user_from_session", side_effect=HTTPException(401)), patch.object(HTTPUtils, "require_discord_ready") as ready, self.assertRaises(HTTPException) as error:
            await sessions.guilds(Mock())
        self.assertEqual(error.exception.status_code, 401)
        ready.assert_not_called()

    async def test_ready_bot_serves_guild_list_normally(self):
        guild = Mock()
        user = SimpleNamespace(guildusers=[SimpleNamespace(guild=guild)])
        projection = Mock()
        with patch.object(ApplicationModel, "bot", Mock(is_ready=Mock(return_value=True)), create=True), patch.object(
            HTTPUtils, "get_user_from_session", return_value=user
        ), patch.object(sessions.GuildProjection, "from_guild", return_value=projection):
            self.assertEqual(await sessions.guilds(Mock()), [projection])
