This files contains guidelines on how to contribute to the project.

## File Issues
If you find a bug, or have a feature request, please file an issue on the [GitHub Repository](https://github.com/MattePalte/Verbify-TTS/issues).

## Pull Requests
If you have a modification in mind, feel free to fork the project and file a pull request.
Please follow the pep8 guidelines and make sure to add tests for your code.

## For Author(s): Development Guidelines

1. Make sure you have the following packages:
```bash
pip install twine
pip install wheel
```

2. To upload it to PyPi, run the following command:
```bash
python setup.py sdist bdist_wheel
python -m twine upload dist/*
```

