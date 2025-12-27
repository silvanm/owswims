from django.apps import AppConfig


class AppConfig(AppConfig):
    name = 'app'

    def ready(self):
        import app.signals  # noqa

        # Initialize Langfuse instrumentation for LlamaIndex tracing
        from app.instrumentation import init_langfuse_instrumentation
        init_langfuse_instrumentation()
