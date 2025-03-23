# Django Q Integration for OWSwims

This document explains how to use Django Q for asynchronous task processing in the OWSwims project.

## Overview

Django Q is a native Django task queue that uses Django's ORM as its storage backend. It provides a simple way to execute tasks asynchronously, which is particularly useful for time-consuming operations like event crawling and location verification.

## Configuration

Django Q is configured in `settings.py` with the following settings:

```python
# Django Q configuration
Q_CLUSTER = {
    "name": "owswims",
    "workers": 4,
    "recycle": 500,
    "timeout": 300,
    "retry": 600,  # Set retry larger than timeout to avoid warning
    "compress": True,
    "save_limit": 250,
    "queue_limit": 500,
    "cpu_affinity": 1,
    "label": "Django Q",
    "orm": "default",  # Use Django's ORM as the broker
}
```

## Running the Cluster

To process tasks, you need to run the Django Q cluster. There are two ways to do this:

### 1. Using VS Code Launch Configuration

The project includes a VS Code launch configuration for running the Django Q cluster:

- **Django Q Cluster**: Runs only the Django Q cluster
- **Django + Q Cluster**: Runs both the Django server and the Django Q cluster simultaneously

To use these configurations:
1. Open the Run and Debug panel in VS Code (Ctrl+Shift+D or Cmd+Shift+D)
2. Select "Django Q Cluster" or "Django + Q Cluster" from the dropdown
3. Click the green play button or press F5

### 2. Using Command Line

Alternatively, you can run the Django Q cluster from the command line:

```bash
cd backend
python manage.py qcluster
```

## Asynchronous Tasks

The project includes three main asynchronous tasks:

### 1. Event Processing

The `process_event_urls_async` function in `app/tasks.py` processes event URLs asynchronously. This task is triggered from the Django admin interface using the "Process event URLs asynchronously" action.

### 2. Single Event Crawling

The `crawl_single_event_async` function in `app/tasks.py` crawls a single event asynchronously. This task is equivalent to running `python manage.py crawl_events --event 'URL'` and is triggered from the Django admin interface using the "Crawl single event asynchronously" action.

### 3. Location Verification

The `verify_locations_async` function in `app/tasks.py` verifies locations asynchronously. This task is triggered from the Django admin interface using the "Process selected unverified locations" action.

## Task Completion Hooks

Task completion hooks are functions that are called when a task completes. They are defined in `app/tasks_hooks.py` and are used to:

1. Log task completion status
2. Create admin log entries for successful tasks
3. Log errors for failed tasks

## Using Asynchronous Tasks in the Admin Interface

### Event Processing

1. Go to the Events admin page
2. Select "Process event URLs asynchronously" from the actions dropdown
3. Enter the URLs to process in the form
4. Click "Process URLs" to submit the task to Django Q

### Single Event Crawling

1. Go to the Events admin page
2. Select "Crawl single event asynchronously" from the actions dropdown
3. Enter the URL of the event to crawl in the form
4. Click "Crawl Event" to submit the task to Django Q

### Location Verification

1. Go to the Locations admin page
2. Select the unverified locations you want to process
3. Choose "Process selected unverified locations" from the actions dropdown
4. The task will be submitted to Django Q for asynchronous processing

## Monitoring Tasks

You can monitor tasks in the Django admin interface by looking at the admin log entries. Each completed task creates an entry in the admin log with details about the task result.

## Creating New Asynchronous Tasks

To create a new asynchronous task:

1. Define the task function in `app/tasks.py`
2. Create a hook function in `app/tasks_hooks.py` if needed
3. Use `async_task` to submit the task to Django Q:

```python
from django_q.tasks import async_task

task_id = async_task(
    your_task_function,
    arg1, arg2,
    hook="app.tasks_hooks.your_hook_function",
)
```

## Benefits of Using Django Q

- **Improved User Experience**: Time-consuming operations run in the background, keeping the admin interface responsive
- **Better Resource Utilization**: Tasks are distributed across multiple workers
- **Reliability**: Failed tasks can be retried automatically
- **Scalability**: The number of workers can be increased to handle more tasks
