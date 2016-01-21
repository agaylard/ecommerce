# encoding: utf-8
"""Contains the tests for publish to lms command."""

from __future__ import unicode_literals
import logging
import os
import tempfile

import ddt
from django.core.management import call_command, CommandError
import mock
from mock import call
from testfixtures import LogCapture

from ecommerce.courses.models import Course
from ecommerce.courses.tests.factories import CourseFactory
from ecommerce.extensions.catalogue.tests.mixins import CourseCatalogTestMixin
from ecommerce.tests.testcases import TransactionTestCase


logger = logging.getLogger(__name__)
LOGGER_NAME = 'ecommerce.courses.management.commands.publish_to_lms'


@ddt.ddt
class PublishCoursesToLMSTests(CourseCatalogTestMixin, TransactionTestCase):
    """Tests the course publish command."""

    tmp_file_path = os.path.join(tempfile.gettempdir(), "tmp-testfile.txt")

    def setUp(self):
        super(PublishCoursesToLMSTests, self).setUp()
        self.course = CourseFactory()
        self.create_course_ids_file(self.tmp_file_path, [self.course.id])

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.tmp_file_path):
            os.remove(cls.tmp_file_path)

    def create_course_ids_file(self, file_path, course_ids):
        """Write the course_ids list to the temp file."""

        with open(file_path, 'w') as temp_file:
            temp_file.write("\n".join(course_ids))

    @ddt.data("", "fake/path")
    def test_invalid_file_path(self, course_ids_file):
        """ Verify command raises the CommandError for invalid file path. """

        with self.assertRaises(CommandError):
            call_command('publish_to_lms', course_ids_file=course_ids_file)

    def test_invalid_course_id(self):
        """ Verify invalid course_id fails. """

        fake_course_id = "fake_course_id"
        self.create_course_ids_file(self.tmp_file_path, [fake_course_id])
        expected = (
            (
                LOGGER_NAME,
                "INFO",
                "Publishing 1 course(s) through management command."
            ),
            (
                LOGGER_NAME,
                "ERROR",
                u"Error in publishing course {} through management command.\tError detail: The course {} does not "
                u"exist.\n".format(fake_course_id, fake_course_id)
            ),
            (
                LOGGER_NAME,
                "ERROR",
                "Management Command: 1 course(s) failed out of 1."
            )
        )
        with LogCapture(LOGGER_NAME) as lc:
            call_command('publish_to_lms', course_ids_file=self.tmp_file_path)
            lc.check(*expected)

    def test_course_publish_successfully(self):
        """ Verify all courses are successfully published."""

        second_course = CourseFactory.create()
        self.create_course_ids_file(self.tmp_file_path, [self.course.id, second_course.id])
        expected = (
            (
                LOGGER_NAME,
                "INFO",
                "Publishing 2 course(s) through management command."
            ),
            (
                LOGGER_NAME,
                "INFO",
                u"The course {} published successfully through management command.\n".format(self.course.id)
            ),
            (
                LOGGER_NAME,
                "INFO",
                u"The course {} published successfully through management command.\n".format(second_course.id)),
            (
                LOGGER_NAME,
                "INFO",
                "Management Command: All 2 course(s) published successfully."
            )
        )
        with mock.patch.object(Course, 'publish_to_lms', autospec=True) as mock_publish:
            mock_publish.return_value = None
            with LogCapture(LOGGER_NAME) as lc:
                call_command('publish_to_lms', course_ids_file=self.tmp_file_path)
                lc.check(*expected)
        # Check that the mocked function was called twice.
        self.assertListEqual(mock_publish.call_args_list, [call(self.course), call(second_course)])

    def test_course_publish_failed(self):
        """ Verify failed courses are logged."""

        error_msg = "The failure message."
        expected = (
            (
                LOGGER_NAME,
                "INFO",
                "Publishing 1 course(s) through management command."
            ),
            (
                LOGGER_NAME,
                "ERROR",
                u"Error in publishing course {} through management command.\tError detail: {}\n".format(
                    self.course.id, error_msg)
            ),
            (
                LOGGER_NAME,
                "ERROR",
                "Management Command: 1 course(s) failed out of 1."
            )
        )
        with mock.patch.object(Course, 'publish_to_lms') as mock_publish:
            mock_publish.return_value = error_msg
            with LogCapture(LOGGER_NAME) as lc:
                call_command('publish_to_lms', course_ids_file=self.tmp_file_path)
                lc.check(*expected)
            mock_publish.assert_called_once_with()

    def test_unicode_file_name(self):
        """ Verify the unicode files name are read correctly."""
        unicode_file = os.path.join(tempfile.gettempdir(), u"اول.txt")
        self.create_course_ids_file(unicode_file, [self.course.id])
        expected = (
            (
                LOGGER_NAME,
                "INFO",
                "Publishing 1 course(s) through management command."
            ),
            (
                LOGGER_NAME,
                "INFO",
                u"The course {} published successfully through management command.\n".format(self.course.id)
            ),
            (
                LOGGER_NAME,
                "INFO",
                "Management Command: All 1 course(s) published successfully."
            )
        )
        with mock.patch.object(Course, 'publish_to_lms') as mock_publish:
            mock_publish.return_value = None
            with LogCapture(LOGGER_NAME) as lc:
                call_command('publish_to_lms', course_ids_file=unicode_file)
                lc.check(*expected)

        mock_publish.assert_called_once_with()
        os.remove(unicode_file)
