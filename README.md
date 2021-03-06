# Machine Learning for Software refactoring

This repository contains the machine learning part on the use
of machine learning methods to recommend software refactoring.

## Paper and appendix

* The paper can be found here: <https://arxiv.org/abs/2001.03338>
* The raw dataset can be found here: <https://zenodo.org/record/3547639>
* The appendix with our full results can be found here: <https://zenodo.org/record/3583980> 

## The machine learning pipeline

This project contains all the Python scripts that are responsible
for the ML pipeline.

### Installing and configuring the database

This project requires ```python 3.6``` or higher.

First, install all the dependencies:

```
pip3 install --user -r requirements.txt
```

Then, create a `dbconfig.ini` file, following the example structure in
`dbconfig-example.ini`. In this file, you configure your database connection.

Finally, configure the training in the `configs.py`. There, you can define which datasets to analyze, which models to build, which under sampling algorithms to use, and etc. Please, read the comments in this file.

### Training and testing models

The main Python script that generates all the models and results is the
`binary_classification.py`. You run it by simply calling `python3 binary_classification.py`.

The results will be stored in a `results/` folder.

The generated output is a text file with a weak structure. A quick way to get results is by grepping:

* `cat *.txt | grep "CSV"`: returns a CSV with all the models and their precision, recall, and accuracy.
* `cat *.txt | grep "TIME"`: returns a CSV with how much time it took to train and test the model.

**Before** running the **pipeline**, we suggest you to warm up the cache. The warming up basically executes all the required queries and cache them as CSV files. These queries can take a long time to run... and if you are like us, you will most likely re-execute your experiments many times! :) Thus, having them cached helps:

```
python3 warm_cache.py
```

If you need to clean up the cache, simply delete the `_cache` directory.

## Authors

This project was initially envisioned by Maurício Aniche, Erick Galante Maziero, Rafael Durelli, and Vinicius Durelli.

## License

This project is licensed under the MIT license.
