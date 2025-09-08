from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING, Any

from flask import Response, send_from_directory
from inginious.common.tasks_problems import Problem
from inginious.frontend.pages.utils import INGIniousPage
from inginious.frontend.parsable_text import ParsableText
from inginious.frontend.task_problems import DisplayableProblem

if TYPE_CHECKING:
    from gettext import NullTranslations

    from inginious.client.client import Client
    from inginious.common.filesystems import FileSystemProvider
    from inginious.frontend.course_factory import CourseFactory
    from inginious.frontend.plugin_manager import PluginManager
    from inginious.frontend.task_factory import TaskFactory
    from inginious.frontend.template_helper import TemplateHelper


__version__ = "0.1.0"

PATH_TO_PLUGIN = os.path.abspath(os.path.dirname(__file__))
PATH_TO_TEMPLATES = os.path.join(PATH_TO_PLUGIN, "templates")


class RegexShortAnswerProblemStatic(INGIniousPage):
    """Serve static files for the regex short answer plugin."""

    def GET(self, path: str) -> Response:  # noqa: N802
        """Serve static files for the regex short answer plugin.

        Args:
            path: The path to the static file.

        Returns:
            The static file.
        """
        return send_from_directory(os.path.join(PATH_TO_PLUGIN, "static"), path)


class RegexShortAnswerProblem(Problem):
    """Display an input box and check that the content match one of the regexes."""

    def __init__(
        self,
        problemid: str,
        content: dict[str, Any],
        translations: dict[str, NullTranslations],
        taskfs: FileSystemProvider,
    ) -> None:
        """Initialises a RegexShortAnswerProblem.

        Args:
            problemid: The problem ID.
            content: The problem content.
            translations: The problem translations.
            taskfs: The task file system provider.
        """
        super().__init__(problemid, content, translations, taskfs)
        self._header = content.get("header", "")
        self._centralize = "centralize" in content
        self._no_match_feedback = (
            [no_match_feedback]
            if (no_match_feedback := content.get("no_match_feedback"))
            else None
        )
        self._matches: list[dict] = list(content.get("matches", ()))

    @classmethod
    def get_type(cls) -> str:  # type: ignore
        """Returns the type of the problem.

        Returns:
            The type of the problem.
        """
        return "regex_short_answer"

    def input_is_consistent(  # type: ignore
        self,
        task_input: dict[str, str],
        default_allowed_extension: str,
        default_max_size: int,
    ) -> bool:
        """Checks if the input is consistent.

        Args:
            task_input: The task input.
            default_allowed_extension: The default allowed file extension.
            default_max_size: The default maximum file size.

        Returns:
            True if the input is consistent, False otherwise.
        """
        return self.get_id() in task_input

    def input_type(self) -> type:
        """Returns the type of the input.

        Returns:
            The type of the input.
        """
        return str

    def check_answer(  # type: ignore  # noqa: D102
        self,
        task_input: dict[str, str],
        language: str,
    ) -> tuple[bool, str | None, list[str] | None, int, str]:
        for match in self._matches:
            regex: str = match["regex"]

            if re.match(regex, task_input[self.get_id()]) is not None:
                valid: bool = match["valid"]
                feedback: list[str] | None = (  # type: ignore
                    [feedback] if (feedback := match["feedback"]) else None
                )
                return (
                    valid,
                    None,
                    feedback if not self._centralize else None,
                    0,
                    "",
                )

        return (
            False,
            None,
            self._no_match_feedback if not self._centralize else None,
            0,
            "",
        )

    @classmethod
    def parse_problem(cls, problem_content: dict[str, Any]) -> dict[str, Any]:
        """Parses the problem content.

        Args:
            problem_content: The problem content.

        Returns:
            The parsed problem.
        """
        if "centralize" in problem_content:
            problem_content["centralize"] = True

        if (
            "no_match_feedback" in problem_content
            and problem_content["no_match_feedback"].strip() == ""
        ):
            del problem_content["no_match_feedback"]

        if "matches" in problem_content:
            problem_content["matches"] = [
                val
                for _, val in sorted(
                    iter(problem_content["matches"].items()), key=lambda x: int(x[0])
                )
            ]
            for match in problem_content["matches"]:
                if "valid" in match:
                    match["valid"] = True
                if "feedback" in match and match["feedback"].strip() == "":
                    del match["feedback"]

        return Problem.parse_problem(problem_content)

    @classmethod
    def get_text_fields(cls) -> dict[str, Any]:  # noqa: D102
        fields: dict[str, Any] = Problem.get_text_fields()
        fields.update(
            {
                "header": True,
                "no_match_feedback": True,
                "matches": [{"regex": True, "feedback": True}],
            },
        )
        return fields


class RegexShortAnswerDisplayableProblem(RegexShortAnswerProblem, DisplayableProblem):  # type: ignore
    """A displayable regex short answer problem."""

    def __init__(
        self,
        problemid: str,
        content: dict[str, Any],
        translations: dict[str, NullTranslations],
        taskfs: FileSystemProvider,
    ) -> None:
        """Initialises a RegexShortAnswerDisplayableProblem.

        Args:
            problemid: The problem ID.
            content: The problem content.
            translations: The problem translations.
            taskfs: The task file system provider.
        """
        super().__init__(problemid, content, translations, taskfs)

    @classmethod
    def get_type_name(cls, language: str) -> str:  # type: ignore
        """Returns the type name of the problem.

        Args:
            language: The language code.

        Returns:
            The type name of the problem.
        """
        return "regex_short_answer"

    def show_input(  # type: ignore  # noqa: D415
        self,
        template_helper: TemplateHelper,
        language: str,
        seed: int,
    ) -> str:
        """Show a RegexShortAnswerDisplayableProblem.

        Args:
            template_helper: The template helper instance.
            language: The language code.
            seed: The random seed.

        Returns:
            The rendered input HTML.
        """
        header = ParsableText(
            self.gettext(language, self._header),
            "rst",
            translation=self.get_translation_obj(language),
        )
        return template_helper.render(
            "tasks/regex_short_answer.html",
            template_folder=PATH_TO_TEMPLATES,
            pid=self.get_id(),
            header=header,
        )

    @classmethod
    def show_editbox(  # type: ignore
        cls,
        template_helper: TemplateHelper,
        key: str,
        language: str,
    ) -> str:
        """Show the edit box for a RegexShortAnswerDisplayableProblem.

        Args:
            template_helper: The template helper instance.
            key: The problem key.
            language: The language code.

        Returns:
            The rendered edit box HTML.
        """
        return template_helper.render(
            "course_admin/subproblems/regex_short_answer.html",
            template_folder=PATH_TO_TEMPLATES,
            key=key,
        )

    @classmethod
    def show_editbox_templates(  # type: ignore
        cls,
        template_helper: TemplateHelper,
        key: str,
        language: str,
    ) -> str:
        """Show the edit box templates for a RegexShortAnswerDisplayableProblem.

        Args:
            template_helper: The template helper instance.
            key: The problem key.
            language: The language code.

        Returns:
            The rendered edit box templates HTML.
        """
        return template_helper.render(
            "course_admin/subproblems/regex_short_answer_templates.html",
            template_folder=PATH_TO_TEMPLATES,
            key=key,
        )


def init(
    plugin_manager: PluginManager,
    course_factory: CourseFactory,
    client: Client,
    plugin_config: dict[str, Any],
) -> None:
    """Initialises the regex-short-answer-problem plugin.

    Args:
        plugin_manager: The plugin manager instance.
        course_factory: The course factory instance.
        client: The client instance.
        plugin_config: The plugin configuration dictionary.
    """
    plugin_manager.add_page(
        "/plugins/regex_short_answer/static/<path:path>",
        RegexShortAnswerProblemStatic.as_view("regex_short_answer_static"),
    )
    plugin_manager.add_hook(
        "javascript_header",
        lambda: "/plugins/regex_short_answer/static/js/studio.js",
    )
    plugin_manager.add_hook(
        "javascript_header",
        lambda: "/plugins/regex_short_answer/static/js/task.js",
    )
    task_factory: TaskFactory = course_factory.get_task_factory()
    task_factory.add_problem_type(RegexShortAnswerDisplayableProblem)
