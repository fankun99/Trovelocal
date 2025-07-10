#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import threading
from django.conf import settings



def main():
   

    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knowledge_base_project.settings')
    try:
        from django.core.management import execute_from_command_line
        download_dir = os.path.join(settings.BASE_DIR, 'github_repos')
        os.makedirs(download_dir, exist_ok=True)

        save_dir = os.path.join(settings.BASE_DIR, 'craw_url_to_html')
        os.makedirs(save_dir, exist_ok=True)


        save_dir_2 = os.path.join(settings.BASE_DIR, 'knowledge_base')
        os.makedirs(save_dir_2, exist_ok=True)
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc


    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    


    main()
