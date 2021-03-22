# # TODO fix these tests, they are dependant on the config and order of params and therefore flaky

# from typing import Iterable
# import unittest

# from configs import LEVEL_Stable_Thresholds_MAP, Level

# from db.QueryBuilder import (
#     file_type_filter,
#     get_all_level_refactorings,
#     get_instance_fields,
#     get_level_refactorings, get_level_stable,
#     get_metrics_level,
#     get_refactoring_levels_counts,
#     get_refactoring_types,
#     join_table,
#     refactoringCommits,
#     valid_refactorings_filter)


# class QueryBuilderUnitTest(unittest.TestCase):
#     maxDiff = None

#     def test_join_tables(self):
#         self.assertEqual(
#             " INNER JOIN CommitMetaData ON RefactoringCommit.commitMetaData_id = CommitMetaData.id",
#             join_table(
#                 "RefactoringCommit",
#                 "CommitMetaData"))
#         self.assertEqual(
#             " INNER JOIN ProcessMetrics ON RefactoringCommit.processMetrics_id = ProcessMetrics.id",
#             join_table(
#                 "RefactoringCommit",
#                 "ProcessMetrics"))
#         self.assertEqual(
#             " INNER JOIN project ON StableCommit.project_id = project.id",
#             join_table(
#                 "StableCommit",
#                 "project"))

#     def test_get_metrics_level(self):
#         self.assertEqual(2, len(get_metrics_level(int(Level.Class))))
#         self.assertEqual(3, len(get_metrics_level(int(Level.Method))))
#         self.assertEqual(4, len(get_metrics_level(int(Level.Variable))))
#         self.assertEqual(3, len(get_metrics_level(int(Level.Field))))
#         self.assertNotEqual(get_metrics_level(
#             2), get_metrics_level(int(Level.Field)))

#     def test_get_instance_fields(self):
#         sql_expected: str = "SELECT RefactoringCommit.id, RefactoringCommit.className, CommitMetaData.commitId FROM RefactoringCommit INNER JOIN CommitMetaData ON RefactoringCommit.commitMetaData_id = CommitMetaData.id INNER JOIN project ON RefactoringCommit.project_id = project.id"
#         sql_built: str = get_instance_fields(
#             "RefactoringCommit", [
#                 ("RefactoringCommit", [
#                     "id", "className"]), ("CommitMetaData", ["commitId"]), ("project", [])])
#         self.assertEqual(sql_expected, sql_built)

#         sql_expected += " WHERE CommitMetaData.parentCommitId != null"
#         sql_built: str = get_instance_fields("RefactoringCommit",
#                                              [("RefactoringCommit", ["id", "className"]), ("CommitMetaData", [
#                                                  "commitId"]), ("project", [])],
#                                              "CommitMetaData.parentCommitId != null")
#         self.assertEqual(sql_expected, sql_built)

#         sql_expected += " AND datasetName IN (\"github\")"
#         sql_built: str = get_instance_fields("RefactoringCommit",
#                                              [("RefactoringCommit", ["id", "className"]), ("CommitMetaData", [
#                                                  "commitId"]), ("project", [])],
#                                              "CommitMetaData.parentCommitId != null",
#                                              ["github"])
#         self.assertEqual(sql_expected, sql_built)

#         sql_expected += " order by CommitMetaData.commitDate"
#         sql_built: str = get_instance_fields("RefactoringCommit",
#                                              [("RefactoringCommit", ["id", "className"]), ("CommitMetaData", [
#                                                  "commitId"]), ("project", [])],
#                                              "CommitMetaData.parentCommitId != null",
#                                              ["github"],
#                                              conditions="order by CommitMetaData.commitDate")
#         self.assertEqual(sql_expected, sql_built)

#     def test_get_refactoring_levels(self):
#         sql_expected: str = "SELECT refactoring, count(*) total from RefactoringCommit INNER JOIN project ON RefactoringCommit.project_id = project.id where RefactoringCommit.isTest = 0 AND datasetName LIKE \"github\" AND RefactoringCommit.isValid = TRUE group by `level`, refactoring order by count(*) desc"
#         sql_built: str = get_refactoring_levels_counts("github")
#         self.assertEqual(sql_expected, sql_built)

#     def test_get_level_refactorings(self):
#         sql_expected: str = "SELECT CONCAT_WS('.', 'RefactoringCommit', RefactoringCommit.id) AS db_id, ClassMetric.classAnonymousClassesQty, ClassMetric.classAssignmentsQty, ClassMetric.classCbo, ClassMetric.classComparisonsQty, ClassMetric.classLambdasQty, ClassMetric.classLcom, ClassMetric.classLoc, ClassMetric.classLoopQty, ClassMetric.classMathOperationsQty, ClassMetric.classMaxNestedBlocks, ClassMetric.classNosi, ClassMetric.classNumberOfAbstractMethods, ClassMetric.classNumberOfDefaultFields, ClassMetric.classNumberOfDefaultMethods, ClassMetric.classNumberOfFields, ClassMetric.classNumberOfFinalFields, ClassMetric.classNumberOfFinalMethods, ClassMetric.classNumberOfMethods, ClassMetric.classNumberOfPrivateFields, ClassMetric.classNumberOfPrivateMethods, ClassMetric.classNumberOfProtectedFields, ClassMetric.classNumberOfProtectedMethods, ClassMetric.classNumberOfPublicFields, ClassMetric.classNumberOfPublicMethods, ClassMetric.classNumberOfStaticFields, ClassMetric.classNumberOfStaticMethods, ClassMetric.classNumberOfSynchronizedFields, ClassMetric.classNumberOfSynchronizedMethods, ClassMetric.classNumbersQty, ClassMetric.classParenthesizedExpsQty, ClassMetric.classReturnQty, ClassMetric.classRfc, ClassMetric.classStringLiteralsQty, ClassMetric.classSubClassesQty, ClassMetric.classTryCatchQty, ClassMetric.classUniqueWordsQty, ClassMetric.classVariablesQty, ClassMetric.classWmc, ClassMetric.isInnerClass, MethodMetric.methodAnonymousClassesQty, MethodMetric.methodAssignmentsQty, MethodMetric.methodCbo, MethodMetric.methodComparisonsQty, MethodMetric.methodLambdasQty, MethodMetric.methodLoc, MethodMetric.methodLoopQty, MethodMetric.methodMathOperationsQty, MethodMetric.methodMaxNestedBlocks, MethodMetric.methodNumbersQty, MethodMetric.methodParametersQty, MethodMetric.methodParenthesizedExpsQty, MethodMetric.methodReturnQty, MethodMetric.methodRfc, MethodMetric.methodStringLiteralsQty, MethodMetric.methodSubClassesQty, MethodMetric.methodTryCatchQty, MethodMetric.methodUniqueWordsQty, MethodMetric.methodVariablesQty, MethodMetric.methodWmc, MethodMetric.startLine, ProcessMetrics.authorOwnership, ProcessMetrics.bugFixCount, ProcessMetrics.qtyMajorAuthors, ProcessMetrics.qtyMinorAuthors, ProcessMetrics.qtyOfAuthors, ProcessMetrics.qtyOfCommits, ProcessMetrics.refactoringsInvolved FROM RefactoringCommit INNER JOIN CommitMetaData ON RefactoringCommit.commitMetaData_id = CommitMetaData.id INNER JOIN ClassMetric ON RefactoringCommit.classMetrics_id = ClassMetric.id INNER JOIN MethodMetric ON RefactoringCommit.methodMetrics_id = MethodMetric.id INNER JOIN ProcessMetrics ON RefactoringCommit.processMetrics_id = ProcessMetrics.id INNER JOIN project ON RefactoringCommit.project_id = project.id WHERE RefactoringCommit.level = 2 AND RefactoringCommit.isValid = TRUE AND RefactoringCommit.isTest = 0 AND RefactoringCommit.refactoring = \"Change Parameter Type\" AND datasetName IN (\"github\") order by CommitMetaData.commitDate"
#         sql_built: str = get_level_refactorings(
#             int(Level.Method), "Change Parameter Type", ["github"])
#         self.assertEqual(sql_expected, sql_built)

#     def test_get_all_level_refactorings(self):
#         sql_expected: str = "SELECT CONCAT_WS('.', 'RefactoringCommit', RefactoringCommit.id) AS db_id, ClassMetric.classAnonymousClassesQty, ClassMetric.classAssignmentsQty, ClassMetric.classCbo, ClassMetric.classComparisonsQty, ClassMetric.classLambdasQty, ClassMetric.classLcom, ClassMetric.classLoc, ClassMetric.classLoopQty, ClassMetric.classMathOperationsQty, ClassMetric.classMaxNestedBlocks, ClassMetric.classNosi, ClassMetric.classNumberOfAbstractMethods, ClassMetric.classNumberOfDefaultFields, ClassMetric.classNumberOfDefaultMethods, ClassMetric.classNumberOfFields, ClassMetric.classNumberOfFinalFields, ClassMetric.classNumberOfFinalMethods, ClassMetric.classNumberOfMethods, ClassMetric.classNumberOfPrivateFields, ClassMetric.classNumberOfPrivateMethods, ClassMetric.classNumberOfProtectedFields, ClassMetric.classNumberOfProtectedMethods, ClassMetric.classNumberOfPublicFields, ClassMetric.classNumberOfPublicMethods, ClassMetric.classNumberOfStaticFields, ClassMetric.classNumberOfStaticMethods, ClassMetric.classNumberOfSynchronizedFields, ClassMetric.classNumberOfSynchronizedMethods, ClassMetric.classNumbersQty, ClassMetric.classParenthesizedExpsQty, ClassMetric.classReturnQty, ClassMetric.classRfc, ClassMetric.classStringLiteralsQty, ClassMetric.classSubClassesQty, ClassMetric.classTryCatchQty, ClassMetric.classUniqueWordsQty, ClassMetric.classVariablesQty, ClassMetric.classWmc, ClassMetric.isInnerClass, ProcessMetrics.authorOwnership, ProcessMetrics.bugFixCount, ProcessMetrics.qtyMajorAuthors, ProcessMetrics.qtyMinorAuthors, ProcessMetrics.qtyOfAuthors, ProcessMetrics.qtyOfCommits, ProcessMetrics.refactoringsInvolved FROM RefactoringCommit INNER JOIN CommitMetaData ON RefactoringCommit.commitMetaData_id = CommitMetaData.id INNER JOIN ClassMetric ON RefactoringCommit.classMetrics_id = ClassMetric.id INNER JOIN ProcessMetrics ON RefactoringCommit.processMetrics_id = ProcessMetrics.id INNER JOIN project ON RefactoringCommit.project_id = project.id WHERE RefactoringCommit.level = 1 AND RefactoringCommit.isValid = TRUE AND RefactoringCommit.isTest = 0 AND datasetName = \"github\" order by CommitMetaData.commitDate"
#         sql_built: str = get_all_level_refactorings(int(Level.Class), "github")
#         self.assertEqual(sql_expected, sql_built)

#     def test_get_all_level_stable(self):
#         sql_expected: str = "SELECT CONCAT_WS('.', 'StableCommit', StableCommit.id) AS db_id, ClassMetric.classAnonymousClassesQty, ClassMetric.classAssignmentsQty, ClassMetric.classCbo, ClassMetric.classComparisonsQty, ClassMetric.classLambdasQty, ClassMetric.classLcom, ClassMetric.classLoc, ClassMetric.classLoopQty, ClassMetric.classMathOperationsQty, ClassMetric.classMaxNestedBlocks, ClassMetric.classNosi, ClassMetric.classNumberOfAbstractMethods, ClassMetric.classNumberOfDefaultFields, ClassMetric.classNumberOfDefaultMethods, ClassMetric.classNumberOfFields, ClassMetric.classNumberOfFinalFields, ClassMetric.classNumberOfFinalMethods, ClassMetric.classNumberOfMethods, ClassMetric.classNumberOfPrivateFields, ClassMetric.classNumberOfPrivateMethods, ClassMetric.classNumberOfProtectedFields, ClassMetric.classNumberOfProtectedMethods, ClassMetric.classNumberOfPublicFields, ClassMetric.classNumberOfPublicMethods, ClassMetric.classNumberOfStaticFields, ClassMetric.classNumberOfStaticMethods, ClassMetric.classNumberOfSynchronizedFields, ClassMetric.classNumberOfSynchronizedMethods, ClassMetric.classNumbersQty, ClassMetric.classParenthesizedExpsQty, ClassMetric.classReturnQty, ClassMetric.classRfc, ClassMetric.classStringLiteralsQty, ClassMetric.classSubClassesQty, ClassMetric.classTryCatchQty, ClassMetric.classUniqueWordsQty, ClassMetric.classVariablesQty, ClassMetric.classWmc, ClassMetric.isInnerClass, ProcessMetrics.authorOwnership, ProcessMetrics.bugFixCount, ProcessMetrics.qtyMajorAuthors, ProcessMetrics.qtyMinorAuthors, ProcessMetrics.qtyOfAuthors, ProcessMetrics.qtyOfCommits, ProcessMetrics.refactoringsInvolved FROM StableCommit INNER JOIN CommitMetaData ON StableCommit.commitMetaData_id = CommitMetaData.id INNER JOIN ClassMetric ON StableCommit.classMetrics_id = ClassMetric.id INNER JOIN ProcessMetrics ON StableCommit.processMetrics_id = ProcessMetrics.id INNER JOIN project ON StableCommit.project_id = project.id WHERE StableCommit.commitThreshold = 15 AND StableCommit.`level` = 1 AND StableCommit.isTest = 0 AND datasetName = \"github\" order by CommitMetaData.commitDate"
#         sql_built: str = get_level_stable(
#             int(Level.Class), LEVEL_Stable_Thresholds_MAP[Level.Class], "github")
#         self.assertEqual(sql_expected, sql_built)

#     def test_get_refactoring_types(self):
#         sql_expected: str = "SELECT DISTINCT refactoring FROM (SELECT RefactoringCommit.refactoring FROM RefactoringCommit INNER JOIN project ON RefactoringCommit.project_id = project.id WHERE RefactoringCommit.isTest = 0 AND datasetName IN (\"github\")) t"
#         sql_built: str = get_refactoring_types(["github"])
#         self.assertEqual(sql_expected, sql_built)

#     def get_level_refactorings_count(
#             self,
#             level: int,
#             datasets: Iterable[str] = [],
#             project: str = "") -> str:
#         """
#         Get the count of all refactorings for the given level

#         Parameter:
#             level (int):               get the refactoring instances for this level
#             dataset (str) (optional):  filter for these specific projects
#         """
#         return f"SELECT refactoring, count(*) FROM (" + \
#                get_instance_fields(refactoringCommits, [(refactoringCommits, ["refactoring"])],
#                                    f"{refactoringCommits}.level = {str(level)}", datasets) + \
#                f" AND {valid_refactorings_filter(refactoringCommits)} AND {file_type_filter(refactoringCommits)}) t group by refactoring order by count(*) desc"

#     def get_all_level_refactorings(self, level: int, dataset: str = "") -> str:
#         """
#         Get all refactoring instances with the given level and the corresponding metrics

#         Parameter:
#             level (int):               get the refactoring instances for this level
#             dataset (str) (optional):  filter for these specific projects
#         """
#         return get_level_refactorings(level, "", dataset)

#     def get_refactoring_types(self, dataset: str = "") -> str:
#         """
#         Get all unique refactoring types as a list

#         Parameter:
#             dataset (str) (optional):  filter for these specific projects
#         """
#         return f"SELECT DISTINCT refactoring FROM ({get_instance_fields(refactoringCommits, [(refactoringCommits, ['refactoring'])], file_type_filter(refactoringCommits), [dataset])}) t"

#     def get_refactoring_levels_counts(self, dataset="") -> str:
#         """
#         Get the counts of all refactorings for all levels.

#         Parameters:
#             dataset (str) (optional):       filter the project dataset for this
#         """
#         return f"SELECT refactoring, count(*) total from {refactoringCommits}{join_table(refactoringCommits)} where {file_type_filter(refactoringCommits)} AND datasetName LIKE \"{dataset}\" AND {valid_refactorings_filter(refactoringCommits)}" \
#                + " group by `level`, refactoring order by count(*) desc"

#     def test_get_level_refactorings_count(self):
#         sql_expected: str = "SELECT refactoring, count(*) FROM (SELECT RefactoringCommit.refactoring FROM RefactoringCommit INNER JOIN project ON RefactoringCommit.project_id = project.id WHERE RefactoringCommit.level = 2 AND datasetName IN (\"github\") AND RefactoringCommit.isValid = TRUE AND RefactoringCommit.isTest = 0) t group by refactoring order by count(*) desc"
#         sql_built: str = self.get_level_refactorings_count(
#             int(Level.Method), ["github"])
#         self.assertEqual(sql_expected, sql_built)


# if __name__ == '__main__':
#     unittest.main()
