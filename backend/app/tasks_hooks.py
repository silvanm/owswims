import logging
from django.contrib import messages
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)


def crawl_single_event_hook(task):
    """
    Hook function called when a single event crawling task completes.

    Args:
        task: The completed Django Q task object
    """
    from .models import Event

    # Log the task completion
    logger.info(f"Event crawling task {task.id} completed with result: {task.result}")

    # Check if the task was successful
    if task.success:
        # Create an admin log entry
        try:
            # Get the first admin user as the actor for the log entry
            from django.contrib.auth import get_user_model

            User = get_user_model()
            admin_user = User.objects.filter(is_staff=True).first()

            if admin_user:
                content_type = ContentType.objects.get_for_model(Event)
                LogEntry.objects.create(
                    user_id=admin_user.id,
                    content_type_id=content_type.id,
                    object_id=0,  # Batch operation, no specific object
                    object_repr="Single event crawling",
                    action_flag=CHANGE,
                    change_message=f"Asynchronous event crawling completed: {task.result}",
                )
        except Exception as e:
            logger.error(f"Error creating admin log entry: {str(e)}")
    else:
        # Log the error
        logger.error(f"Event crawling task {task.id} failed: {task.result}")


def location_verification_hook(task):
    """
    Hook function called when a location verification task completes.

    Args:
        task: The completed Django Q task object
    """
    from .models import Location

    # Log the task completion
    logger.info(
        f"Location verification task {task.id} completed with result: {task.result}"
    )

    # Check if the task was successful
    if task.success:
        # Create an admin log entry
        try:
            # Get the first admin user as the actor for the log entry
            from django.contrib.auth import get_user_model

            User = get_user_model()
            admin_user = User.objects.filter(is_staff=True).first()

            if admin_user:
                content_type = ContentType.objects.get_for_model(Location)
                LogEntry.objects.create(
                    user_id=admin_user.id,
                    content_type_id=content_type.id,
                    object_id=0,  # Batch operation, no specific object
                    object_repr="Batch location verification",
                    action_flag=CHANGE,
                    change_message=f"Asynchronous location verification completed: {task.result}",
                )
        except Exception as e:
            logger.error(f"Error creating admin log entry: {str(e)}")
    else:
        # Log the error
        logger.error(f"Location verification task {task.id} failed: {task.result}")
