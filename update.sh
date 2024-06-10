# Build the package
python3 setup.py sdist bdist_wheel

# Install the package
pip3 install dist/*.whl
