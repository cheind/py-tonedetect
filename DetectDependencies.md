
### Detect Python dependencies

Follow these steps to detect any project dependencies that should be part of `setup.py`.

Create empty virtual environment
```
> conda create -n snowflake python=3
```

Activate environment
```
> activate snowflake
```

Switch to project directory
```
(snowflake) > cd project
```

Install package
```
(snowflake) > pip install .
```

Try to run tests
```
(snowflake) > python setup.py test
```

Install missing packages either via pip or conda (preferred)
```
(snowflake) > pip install package

(snowflake) > conda install package
```

Verify that tests pass
```
(snowflake) > python setup.py test
```

Export requirements and add the required packages to `setup.py`
```
(snowflake) > conda env export -n snowflake
```

Deactivate environment
```
(snowflake) > deactivate
```

Remove environment
```
(snowflake) > conda remove -n snowflake
```
