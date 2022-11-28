from importlib.metadata import version

__version__ = version("mx_bluesky")
del version

__all__ = ["__version__"]
