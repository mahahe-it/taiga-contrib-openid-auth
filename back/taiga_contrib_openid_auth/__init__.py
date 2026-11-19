from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("taiga-contrib-openid-auth")
except PackageNotFoundError:
    # Used from a source checkout (e.g. symlinked into taiga-back), not installed
    __version__ = "0.0.0"
