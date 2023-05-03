"""Budget Books: A Flask app for personal finance and budgeting."""
__version__ = "0.1.0"

from .backend import main, create_app

if __name__ == "__main__":
    main(True)
