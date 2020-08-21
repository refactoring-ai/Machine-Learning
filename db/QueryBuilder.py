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
# returns a sql condition as a string to filter instances based on the given project name
def project_filter(instance_name: str, project_name: str) -> str:
    return instance_name + ".project_id in (select id from project where datasetName = \"" + project_name + "\")"


# returns a sql condition to join instances with the given table
def join_table(instance_name: str, table_name: str) -> str:
    join_collumn = tableMap[table_name][0]

    return " INNER JOIN " + table_name + \
           " ON " + instance_name + "." + \
           join_collumn[0].lower() + join_collumn[1:] + " = " + table_name + ".id"


# returns a list of all metrics for the given level
# e.g. classMetricsFields, methodMetricsFields and processMetricsFields for level 2 method level
def get_metrics_level(level: int):
    if level <= 3:
        return [(classMetrics, CLASS_METRICS_Fields), (methodMetrics, METHOD_METRICS_FIELDS),
                (variableMetrics, VARIABLE_METRICS_FIELDS)][:level] + \
               [(processMetrics, PROCESS_METRICS_FIELDS)]
    elif level == 4:
        return [(classMetrics, CLASS_METRICS_Fields), (fieldMetrics, FIELD_METRICS_FIELDS),
                (processMetrics, PROCESS_METRICS_FIELDS)]
    elif level == 5:
        return [(classMetrics, CLASS_METRICS_Fields), (processMetrics, PROCESS_METRICS_FIELDS)]


# Create a sql select statement for the given instance and requested fields
# instance name: name of the instance table you are querying, e.g. RefactoringCommit or stablecommit, this is also given in the fields
# fields: a list containing the table name as string and all required fields from the table as a list of strings e.g [CommitMetaData, commitMetaDataFields]
# an instance has to be part of fields together with at least one field, either refactoring commit or stablecommit
# Optional conditions: a string with additional conditions for the instances, e.g. cm.isInnerClass = 1
# Optional dataset: filter the instances based on their project name, e.g. toyproject-1
# Optional order: order by command, e.g. order by CommitMetaData.commitDate
def get_instance_fields(instance_name: str, fields, conditions: str = "", dataset: str = "", order: str = "", get_instance_id: bool = False) -> str:
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
        sql += project_filter(instance_name, dataset)
    if sql.endswith(' WHERE '):
        sql = sql[:-7]
    if len(order) > 8:
        sql += " " + order
    return sql
# endregion


# region Public interaction
# get the count of all refactoring levels
def get_refactoring_levels(dataset="") -> str:
    return "SELECT refactoring, count(*) total from RefactoringCommit where " + project_filter("RefactoringCommit",
                                                                                               dataset) \
           + valid_refactorings_filter(refactoringCommits) \
           + " group by refactoring order by count(*) desc"


def __get_level(instance_name: str, level: int, m_refactoring: str, dataset: str = "", conditions: str = "") -> str:
    # only select valid refactorings from the database, if refactorings are selected
    refactoring_condition: str = f"{instance_name}.level = {str(level)}" + valid_refactorings_filter(instance_name) + file_type_filter(instance_name)

    # only select the specified refactoring type from the database
    if m_refactoring != "":
        refactoring_condition += f" AND {refactoringCommits}.refactoring = \"{m_refactoring}\""
    if len(conditions) > 0:
        refactoring_condition += f" AND {conditions}"
    return get_instance_fields(instance_name, [(instance_name, []), (commitMetaData, [])] + get_metrics_level(level),
                               refactoring_condition, dataset, f"order by {commitMetaData}.commitDate", get_instance_id=True)


# Add restriction whether to use only production, test or both files
def file_type_filter(instance_name: str) -> str:
    if FILE_TYPE != FileType.test_and_production.value:
        return f" AND {instance_name}.isTest = " + str(FILE_TYPE)
    else:
        return ""


# only select valid refactorings from the database
def valid_refactorings_filter(instance_name: str) -> str:
    if instance_name == refactoringCommits:
        return " AND " + instance_name + ".isValid = TRUE"
    else:
        return ""


# get the count of all refactorings for the given level
def get_level_refactorings_count(level: int, dataset: str = "") -> str:
    return "SELECT refactoring, count(*) FROM (" + \
           get_instance_fields(refactoringCommits, [(refactoringCommits, ["refactoring"])],
                               refactoringCommits + ".level = " + str(level), dataset) + \
           valid_refactorings_filter(
               refactoringCommits) + ") t group by refactoring order by count(*) desc"


# get all refactoring instances with the given refactoring type and metrics in regard to the level
def get_level_refactorings(level: int, m_refactoring: str, dataset: str = "") -> str:
    return __get_level(refactoringCommits, level, m_refactoring, dataset)


# get all refactoring instances with the given level and the corresponding metrics
def get_all_level_refactorings(level: int, dataset: str = "") -> str:
    return __get_level(refactoringCommits, level, "", dataset)


# get all stable instances with the given level and the corresponding metrics
def get_all_level_stable(level: int, commit_threshold: int, dataset: str = "") -> str:
    return __get_level(stableCommits, level, "", dataset, conditions=f"{stableCommits}.commitThreshold = {commit_threshold}")


# get all unique refactoring types as a list
# Optional dataset: filter to this specific project
def get_refactoring_types(dataset: str = "") -> str:
    return "SELECT DISTINCT refactoring FROM " \
           "(" + get_instance_fields(refactoringCommits,
                                     [(refactoringCommits, ["refactoring"])], "", dataset) + ") t"
# endregion
