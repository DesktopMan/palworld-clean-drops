import dotenv
import os
import shutil
from pathlib import Path


def install_to(path):
    if os.path.exists(path):
        shutil.rmtree(path)

    shutil.copytree(Path('dist'), path)


def main():
    install_to(Path(os.environ['PALSCHEMA_DIR']))
    install_to(Path(os.environ['WORKSHOP_DIR']))


if __name__ == '__main__':
    dotenv.load_dotenv()
    main()
