# --------------------------------
# Testing
# --------------------------------
# is it a test run?
# test runs reduce the dataset to 100 instances only
from enum import IntEnum

# is this a test run?
TEST = False

# --------------------------------
# FileTypes
# --------------------------------
# Do we only look at production or test files or both?
# 0 = only_production, 1 = only_test, 2 = production_and_test
FILE_TYPE = 2

# --------------------------------
# Database related
# --------------------------------
# do we use the cached results? True=yes, False=no, go always to the db
USE_CACHE = True

# is the db available? sometimes it's not, but you have all the cache
DB_AVAILABLE = True

# --------------------------------
# Dataset balancing
# --------------------------------
BALANCE_DATASET = True

# how to balance the dataset
# options = [random, cluster_centroids, nearmiss]
BALANCE_DATASET_STRATEGY = "random"

# --------------------------------
# Dataset scaling
# --------------------------------
# scale using MinMaxScaler?
SCALE_DATASET = True

# region Sample size
# fraction of the samples (both true and false) to use for training, [0 - 1]
TRAINING_SAMPLE_FRACTION = 0.8

# fraction of the validation or test samples (both true and false) to use for evaluation, [0 - 1]
# If you choose a random train/ test split, this parameter has no effect, TRAINING_SAMPLE_FRACTION will be used instead
EVALUATION_SAMPLE_FRACTION = 1.0
# endregion

# region Feature reduction
# Remove all instances where one of process and authorship metrics is -1 (faulty).
DROP_FAULTY_PROCESS_AND_AUTHORSHIP_METRICS = False
# Use (or drop) process and authorship metrics, this cancels DROP_FAULTY_PROCESS_AND_AUTHORSHIP_METRICS.
DROP_PROCESS_AND_AUTHORSHIP_METRICS = True
# a list of all process and authorship metrics
PROCESS_AND_AUTHORSHIP_METRICS = ["authorOwnership", "bugFixCount", "qtyMajorAuthors", "qtyMinorAuthors", "qtyOfAuthors", "qtyOfCommits", "refactoringsInvolved"]

# Drop these metrics as well
DROP_METRICS = []

# perform feature reduction?
FEATURE_REDUCTION = False

# number of folds for feature reduction
N_CV_FEATURE_REDUCTION = 2
# endregion

# region Hyperparameter search
# what type of search for the best hyper params?
# options = [randomized, grid]
SEARCH = "grid"

# number of iterations (if Randomized strategy is chosen)
N_ITER_RANDOM_SEARCH = 100

# number of folds in the search for best parameters
N_CV_SEARCH = 5
# endregion

# region Evaluation: Cross-validation configuration
# Specify either a train/ test split, e.g. 0.2 -> 80/ 20 split
VAL_SPLIT_SIZE = -1
# Or specify test data sets in the database
# NOTE: set TEST_SPLIT_SIZE value to < 0, in order to indicate to use the given datasets instead of a random train/ test split
VALIDATION_DATASETS = ["test set github", "validation set github"]

# number of folds for the final evaluation
N_CV = 10

# number of folds for the DNN
N_CV_DNN = 10
# endregion

# region Models and datasets
# models and datasets we have available
MODELS = ['svm', 'svm-non-linear', 'decision-tree', 'random-forest', 'logistic-regression', 'naive-bayes',
          'extra-trees']

# Empty dataset means 'all datasets'
DATASETS = ["github"]
# endregion

# region refactorings
# refactoring levels
class Level(IntEnum):
    NONE = 0
    Class = 1
    Method = 2
    Variable = 3
    Field = 4
    Other = 5

# Refactorings to study
CLASS_LEVEL_REFACTORINGS = ["Extract Class",
                            "Extract Interface",
                            "Extract Subclass",
                            "Extract Superclass",
                            "Move And Rename Class",
                            "Move Class",
                            "Rename Class",
                            "Introduce Polymorphism",
                            "Convert Anonymous Class To Type"]

METHOD_LEVEL_REFACTORINGS = ["Extract And Move Method",
                             "Extract Method",
                             "Inline Method",
                             "Move Method",
                             "Pull Up Method",
                             "Push Down Method",
                             "Rename Method",
                             "Extract And Move Method",
                             "Change Return Type",
                             "Move And Inline Method",
                             "Move And Rename Method",
                             "Change Parameter Type",
                             "Split Parameter",
                             "Merge Parameter"]

VARIABLE_LEVEL_REFACTORINGS = ["Extract Variable",
                               "Inline Variable",
                               "Parameterize Variable",
                               "Rename Parameter",
                               "Rename Variable",
                               "Replace Variable With Attribute",
                               "Change Variable Type",
                               "Split Variable",
                               "Merge Variable"]

FIELD_LEVEL_REFACTORINGS = ["Move Attribute",
                            "Pull Up Attribute",
                            "Move And Rename Attribute",
                            "Push Down Attribute",
                            "Replace Attribute",
                            "Rename Attribute",
                            "Extract Attribute",
                            "Change Attribute Type"]

OTHER_LEVEL_REFACTORINGS = ["Move Source Folder",
                            "Change Package"]

# Maps each level onto its refactorings
LEVEL_MAP = {Level.NONE: [],
             Level.Class: CLASS_LEVEL_REFACTORINGS,
             Level.Method: METHOD_LEVEL_REFACTORINGS,
             Level.Variable: VARIABLE_LEVEL_REFACTORINGS,
             Level.Field: FIELD_LEVEL_REFACTORINGS,
             Level.Other: OTHER_LEVEL_REFACTORINGS}
# endregion

# region metrics fields
# the ids are not included as they are the same for every table: id : long
CLASS_METRICS_Fields = ["classAnonymousClassesQty",
                      "classAssignmentsQty",
                      "classCbo",
                      "classComparisonsQty",
                      "classLambdasQty",
                      "classLcom",
                      "classLoc",
                      "classLoopQty",
                      "classMathOperationsQty",
                      "classMaxNestedBlocks",
                      "classNosi",
                      "classNumberOfAbstractMethods",
                      "classNumberOfDefaultFields",
                      "classNumberOfDefaultMethods",
                      "classNumberOfFields",
                      "classNumberOfFinalFields",
                      "classNumberOfFinalMethods",
                      "classNumberOfMethods",
                      "classNumberOfPrivateFields",
                      "classNumberOfPrivateMethods",
                      "classNumberOfProtectedFields",
                      "classNumberOfProtectedMethods",
                      "classNumberOfPublicFields",
                      "classNumberOfPublicMethods",
                      "classNumberOfStaticFields",
                      "classNumberOfStaticMethods",
                      "classNumberOfSynchronizedFields",
                      "classNumberOfSynchronizedMethods",
                      "classNumbersQty",
                      "classParenthesizedExpsQty",
                      "classReturnQty",
                      "classRfc",
                      "classStringLiteralsQty",
                      "classSubClassesQty",
                      "classTryCatchQty",
                      "classUniqueWordsQty",
                      "classVariablesQty",
                      "classWmc",
                      "isInnerClass"]
METHOD_METRICS_FIELDS = [#"fullMethodName", ToDo: decide if and how to include string objects
    "methodAnonymousClassesQty",
    "methodAssignmentsQty",
    "methodCbo",
    "methodComparisonsQty",
    "methodLambdasQty",
    "methodLoc",
    "methodLoopQty",
    "methodMathOperationsQty",
    "methodMaxNestedBlocks",
    "methodNumbersQty",
    "methodParametersQty",
    "methodParenthesizedExpsQty",
    "methodReturnQty",
    "methodRfc",
    "methodStringLiteralsQty",
    "methodSubClassesQty",
    "methodTryCatchQty",
    "methodUniqueWordsQty",
    "methodVariablesQty",
    "methodWmc",
    #"shortMethodName", ToDo: decide if and how to include string objects
    "startLine"]
VARIABLE_METRICS_FIELDS = ["variableAppearances",
                         #"variableName" ToDo: decide if and how to include string objects
                         ]
FIELD_METRICS_FIELDS = ["fieldAppearances",
                      #"fieldName" ToDo: decide if and how to include string objects
                      ]
PROCESS_METRICS_FIELDS = ["authorOwnership",
                        "bugFixCount",
                        "qtyMajorAuthors",
                        "qtyMinorAuthors",
                        "qtyOfAuthors",
                        "qtyOfCommits",
                        "refactoringsInvolved"]
COMMIT_METADATA_FIELDS = ["commitDate",
                        "commitId",
                        "commitMessage",
                        "commitUrl",
                        "parentCommitId"]
PROJECT_FIELDS = ["commitCountThresholds",
                 "commits",
                 "datasetName",
                 "dateOfProcessing",
                 "exceptionsCount",
                 "finishedDate",
                 "gitUrl",
                 "isLocal",
                 "javaLoc",
                 "lastCommitHash",
                 "numberOfProductionFiles",
                 "numberOfTestFiles",
                 "productionLoc",
                 "projectName",
                 "projectSizeInBytes",
                 "testLoc"]
REFACTORING_COMMIT_FIELDS = ["className",
                           "filePath",
                           "isTest",
                           "level",
                           # "refactoring", this two fields are not used for the training
                           # "refactoringSummary"
                           ]
STABLE_COMMIT_FIELDS = ["className",
                      "filePath",
                      "isTest",
                      "level"]
# endregion

# region non-refactored instances
# Maps each level onto it stable commit thresholds
LEVEL_Stable_Thresholds_MAP = {Level.NONE: [],
                               Level.Class: 15,
                               Level.Method: 30,
                               Level.Variable: 40,
                               Level.Field: 30,
                               Level.Other: -1}
# endregion

# --------------------------------
# DO NOT CHANGE FROM HERE ON
# --------------------------------
if DROP_PROCESS_AND_AUTHORSHIP_METRICS:
    DROP_METRICS += PROCESS_AND_AUTHORSHIP_METRICS

# Let's change some parameters (i.e., make them smaller) if this is a test run
if TEST:
    N_ITER = 1
    N_CV = 2

    N_ITER_SVM = 1
    N_CV_SVM = 2

    N_CV_DNN = 2

    CV_FEATURE_REDUCTION = 2

    TRAINING_SAMPLE_FRACTION = 0.1
    EVALUATION_SAMPLE_FRACTION = 0.1
