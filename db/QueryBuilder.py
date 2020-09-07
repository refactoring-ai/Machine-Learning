from configs import FILE_TYPE, CLASS_METRICS_Fields, METHOD_METRICS_FIELDS, VARIABLE_METRICS_FIELDS, \
    FIELD_METRICS_FIELDS, PROCESS_METRICS_FIELDS, COMMIT_METADATA_FIELDS, PROJECT_FIELDS, REFACTORING_COMMIT_FIELDS, \
    STABLE_COMMIT_FIELDS, FileType

# region database structure
# table names for reference:
commitMetaData: str = "CommitMetaData"
methodMetrics: str = "MethodMetric"
fieldMetrics: str = "FieldMetric"
variableMetrics: str = "VariableMetric"
processMetrics: str = "ProcessMetrics"
classMetrics: str = "ClassMetric"
project: str = "project"
refactoringCommits: str = "RefactoringCommit"
stableCommits: str = "StableCommit"

# all tables referenced from the instance base class for refactoring commit and stable commit
instanceReferences = ["classMetrics_id",
                      "commitMetaData_id",
                      "fieldMetrics_id",
                      "methodMetrics_id",
                      "processMetrics_id",
                      "project_id",
                      "variableMetrics_id"]

# maps table names onto their instance keys and their fields
tableMap = {commitMetaData: (commitMetaData + "_id", COMMIT_METADATA_FIELDS),
            methodMetrics: (methodMetrics + "s_id", METHOD_METRICS_FIELDS),
            fieldMetrics: (fieldMetrics + "s_id", FIELD_METRICS_FIELDS),
            variableMetrics: (variableMetrics + "s_id", VARIABLE_METRICS_FIELDS),
            processMetrics: (processMetrics + "_id", PROCESS_METRICS_FIELDS),
            classMetrics: (classMetrics + "s_id", CLASS_METRICS_Fields),
            project: (project + "_id", PROJECT_FIELDS),
            refactoringCommits: ("id", REFACTORING_COMMIT_FIELDS),
            stableCommits: ("id", STABLE_COMMIT_FIELDS)}
# endregion


# region tables utils
# returns a sql condition to join instances with the given table
def join_table(instance_name: str, table_name: str) -> str:
    join_collumn = tableMap[table_name][0]

    return " INNER JOIN " + table_name + \
           " ON " + instance_name + "." + \
           join_collumn[0].lower() + join_collumn[1:] + " = " + table_name + ".id"


def get_metrics_level(level: int):
    """
    Get a list of all metrics for the given level, e.g. classMetricsFields, methodMetricsFields and processMetricsFields for level 2 method level

    Parameters:
        level (int):   get the metrics for this level
    """
    if level <= 3:
        return [(classMetrics, CLASS_METRICS_Fields), (methodMetrics, METHOD_METRICS_FIELDS),
                (variableMetrics, VARIABLE_METRICS_FIELDS)][:level] + \
               [(processMetrics, PROCESS_METRICS_FIELDS)]
    elif level == 4:
        return [(classMetrics, CLASS_METRICS_Fields), (fieldMetrics, FIELD_METRICS_FIELDS),
                (processMetrics, PROCESS_METRICS_FIELDS)]
    elif level == 5:
        return [(classMetrics, CLASS_METRICS_Fields), (processMetrics, PROCESS_METRICS_FIELDS)]


def __stable_level_filter(level: int):
    """
    Get a filter to select distinct stable instances for the given level, e.g. for level 2 get stable instances with level 2 and 3

    Parameters:
        level (int):   get the instances for this level
    """
    if level == 1 or level == 5:
        return f"{stableCommits}.`level` = 1"
    else:
        return f"{stableCommits}.`level` = {level}"

# Create a sql select statement for the given instance and requested fields
# instance name: name of the instance table you are querying, e.g. RefactoringCommit or stablecommit, this is also given in the fields
# fields: a list containing the table name as string and all required fields from the table as a list of strings e.g [CommitMetaData, commitMetaDataFields]
# an instance has to be part of fields together with at least one field, either refactoring commit or stablecommit
# Optional conditions: a string with additional conditions for the instances, e.g. cm.isInnerClass = 1
# Optional dataset: filter the instances based on their project name, e.g. toyproject-1
# Optional order: order by command, e.g. order by CommitMetaData.commitDate
def get_instance_fields(instance_name: str, fields, conditions: str = "", dataset: str = "", order: str = "", get_instance_id: bool = False) -> str:
    """
    Create a sql select statement for the given instance and requested fields.

    Parameter:
        instance name (str): name of the instance table you are querying, e.g. RefactoringCommit or stablecommit, this is also given in the fields
        fields (list): a list containing the table name as string and all required fields from the table as a list of strings e.g [CommitMetaData, commitMetaDataFields], an instance has to be part of fields together with at least one field, either refactoring commit or stablecommit
        conditions (str) (optional): a string with additional conditions for the instances, e.g. cm.isInnerClass = 1
        dataset (str) (optional): filter the instances based on their project name, e.g. toyproject-1
        order (str) (optional): order by command, e.g. order by CommitMetaData.commitDate
        get_instance_id (bool) (optional): do you want the original instance id, e.g. StableCommit.2541?
    """
    # combine the required fields with their table names
    required_fields: str = ""
    required_tables: str = ""
    if get_instance_id:
        required_fields += f"CONCAT_WS(\'.\', \'{instance_name}\', {instance_name}.id) AS db_id, "
    for table_name, field_names in fields:
        # don't join the instance with itself
        if (instance_name != table_name):
            required_tables += join_table(instance_name, table_name)

        for field_name in field_names:
            required_fields += table_name + "." + field_name + ", "
    if len(dataset) > 0 and f"{project}" not in required_tables:
        required_tables += join_table(instance_name, project)
    # remove the last chars because it is either a ", " or an " AND "
    required_fields = required_fields[:-2]

    sql: str = f"SELECT {required_fields} FROM {instance_name}{required_tables} WHERE "
    if len(conditions) > 2:
        if not sql.endswith(' WHERE '):
            sql += " AND "
        sql += conditions
    if len(dataset) > 0:
        if not sql.endswith(' WHERE '):
            sql += " AND "
        sql += f"datasetName = \"{dataset}\""
    if sql.endswith(' WHERE '):
        sql = sql[:-7]
    if len(order) > 8:
        sql += " " + order
    return sql
# endregion


# region Public interaction
#
def get_refactoring_levels_counts(dataset="") -> str:
    """
    Get the counts of all refactorings for all levels.

    Parameters:
        dataset (str) (optional):       filter the project dataset for this
    """
    return f"SELECT refactoring, count(*) total from {refactoringCommits}{join_table(refactoringCommits, project)} where {file_type_filter(refactoringCommits)} AND datasetName LIKE \"{dataset}\" AND {valid_refactorings_filter(refactoringCommits)}" \
           + " group by `level`, refactoring order by count(*) desc"


def get_level_refactorings(level: int, m_refactoring: str, dataset: str = "") -> str:
    """
    Get all refactoring instances with the given refactoring type and metrics in regard to the level

    Parameters:
        level (int):                    the refactoring instances are filtered for this level
        m_refactoring (str) (optional): filter for a specific refactoring type, e.g. "Push Down Attribute"
        dataset (str) (optional):       filter the project dataset for this
    """
    # only select valid refactorings from the database, if refactorings are selected
    refactoring_condition: str = f"{refactoringCommits}.level = {str(level)} AND {valid_refactorings_filter(refactoringCommits)} AND {file_type_filter(refactoringCommits)}"

    # only select the specified refactoring type from the database
    if m_refactoring != "":
        refactoring_condition += f" AND {refactoringCommits}.refactoring = \"{m_refactoring}\""
    return get_instance_fields(refactoringCommits, [(refactoringCommits, []), (commitMetaData, [])] + get_metrics_level(level),
                               refactoring_condition, dataset, "", get_instance_id=True)


def get_level_stable(level: int, commit_threshold: int, dataset: str = "", conditions: str = "") -> str:
    """
    Get all stable instances with the given level and the corresponding metrics

    Parameters:
        level (int):                    get the stable instances for this level
        commit_threshold (int):    filter for this specific commit threshold, specifying the 'stability' of the instance
        dataset (str) (optional):       filter the project dataset for this
        conditions (str) (optional):    additional sql conditions for this refactoring, e.g. (commitDate BETWEEN A and B).
                                        DON'T add filter for the level or test; this is already done.
    """
    # only select valid refactorings from the database, if refactorings are selected
    stable_condition: str = f"{stableCommits}.commitThreshold = {commit_threshold} AND {__stable_level_filter(level)} AND {file_type_filter(stableCommits)}"

    if len(conditions) > 0:
        stable_condition += f" AND {conditions}"
    return get_instance_fields(stableCommits, [(stableCommits, []), (commitMetaData, [])] + get_metrics_level(level),
                               stable_condition, dataset, "", get_instance_id=True)


def file_type_filter(instance_name: str) -> str:
    """
    Add restriction whether to use only production, test or both files

    Parameter:
        (instance_name): name of the instance table to filter, either RefactoringCommit or StableCommit
    """
    if FILE_TYPE != FileType.test_and_production.value:
        return f"{instance_name}.isTest = " + str(FILE_TYPE)
    else:
        return ""


def valid_refactorings_filter(instance_name: str) -> str:
    """
    Only select valid refactorings from the database

    Parameter:
        (instance_name): name of the instance table to filter, either RefactoringCommit or StableCommit
    """
    if instance_name == refactoringCommits:
        return f"{instance_name}.isValid = TRUE"
    else:
        return ""


def get_level_refactorings_count(level: int, dataset: str = "") -> str:
    """
    Get the count of all refactorings for the given level

    Parameter:
        level (int):               get the refactoring instances for this level
        dataset (str) (optional):  filter for these specific projects
    """
    return f"SELECT refactoring, count(*) FROM (" + \
           get_instance_fields(refactoringCommits, [(refactoringCommits, ["refactoring"])],
                               f"{refactoringCommits}.level = {str(level)}", dataset) + \
           f" AND {valid_refactorings_filter(refactoringCommits)} AND {file_type_filter(refactoringCommits)}) t group by refactoring order by count(*) desc"


def get_all_level_refactorings(level: int, dataset: str = "") -> str:
    """
    Get all refactoring instances with the given level and the corresponding metrics

    Parameter:
        level (int):               get the refactoring instances for this level
        dataset (str) (optional):  filter for these specific projects
    """
    return get_level_refactorings(level, "", dataset)


def get_refactoring_types(dataset: str = "") -> str:
    """
    Get all unique refactoring types as a list

    Parameter:
        dataset (str) (optional):  filter for these specific projects
    """
    return f"SELECT DISTINCT refactoring FROM ({get_instance_fields(refactoringCommits, [(refactoringCommits, ['refactoring'])], file_type_filter(refactoringCommits), dataset)}) t"
# endregion
