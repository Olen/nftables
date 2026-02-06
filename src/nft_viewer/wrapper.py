"""Wrapper that adds system site-packages for nftables module access."""
import sys
import os


def get_system_site_packages():
    """Get system site-packages paths for current Python version."""
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    paths = [
        f"/usr/lib/python{version}/site-packages",
        f"/usr/lib64/python{version}/site-packages",
        f"/usr/local/lib/python{version}/site-packages",
        f"/usr/local/lib64/python{version}/site-packages",
    ]
    return [p for p in paths if os.path.isdir(p)]


def main():
    # Add system site-packages to path for nftables module
    for path in get_system_site_packages():
        if path not in sys.path:
            sys.path.insert(0, path)

    # Now import and run the actual CLI
    from nft_viewer.cli import main as cli_main
    cli_main()


if __name__ == "__main__":
    main()
