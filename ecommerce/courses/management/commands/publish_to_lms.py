""" This command publish the courses to LMS."""
from __future__ import unicode_literals
import logging
from optparse import make_option
import os

from django.core.management import BaseCommand, CommandError

from ecommerce.courses.models import Course


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Publish the courses to LMS."""

    help = 'Publish the courses to LMS'
    option_list = BaseCommand.option_list + (
        make_option(
            '--course_ids_file',
            action='store',
            dest='course_ids_file',
            default=None,
            help='Path to file to read courses from.'
        ),
    )

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    def handle(self, *args, **options):
        total_courses = 0
        failed = 0
        course_ids_file = options['course_ids_file']
        if not course_ids_file or not os.path.exists(course_ids_file):
            raise CommandError("Pass the correct absolute path to course ids file as --course_ids_file argument.")

        with open(course_ids_file, 'r') as course_ids:
            for course_id in course_ids:
                total_courses += 1
                try:
                    course_id = course_id.strip()
                    course = Course.objects.get(id=course_id)
                    publishing_error = course.publish_to_lms()
                    if publishing_error:
                        failed += 1
                        logger.error(u"%s\t%s\n", course_id, publishing_error)
                    else:
                        msg = "The course published successfully."
                        logger.info(u"%s\t%s\n", course_id, msg)
                except Course.DoesNotExist:
                    failed += 1
                    msg = u"The course {} does not exist.".format(course_id)
                    logger.error(u"%s\t%s\n", course_id, msg)
        if failed:
            logger.error("%s course(s) failed out of %s.", failed, total_courses)
        else:
            logger.info("All courses published successfully.")
