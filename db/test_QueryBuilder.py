import unittest
from db.QueryBuilder import project_filter, join_table, get_metrics_level, get_instance_fields, \
    get_refactoring_levels, get_level_refactorings_count, get_all_level_refactorings, get_all_level_stable, \
    get_level_refactorings, get_refactoring_types


class QueryBuilderUnitTest(unittest.TestCase):
    maxDiff = None

    def test_project_filter(self):
        sqlExpected: str = "RefactoringCommit.project_id in (select id from project where datasetName = \"github\")"
        sqlBuilt: str = project_filter("RefactoringCommit", "github")
        self.assertEqual(sqlExpected, sqlBuilt)

        sqlExpected: str = "StableCommit.project_id in (select id from project where datasetName = \"github\")"
        sqlBuilt: str = project_filter("StableCommit", "github")
        self.assertEqual(sqlExpected, sqlBuilt)

    def test_join_tables(self):
        self.assertEqual(" INNER JOIN CommitMetaData ON RefactoringCommit.commitMetaData_id = CommitMetaData.id",
                         join_table("RefactoringCommit", "CommitMetaData"))
        self.assertEqual(" INNER JOIN ProcessMetrics ON RefactoringCommit.processMetrics_id = ProcessMetrics.id",
                         join_table("RefactoringCommit", "ProcessMetrics"))
        self.assertEqual(" INNER JOIN project ON StableCommit.project_id = project.id", join_table(
            "StableCommit", "project"))

    def test_get_metrics_level(self):
        self.assertEqual(2, len(get_metrics_level(1)))
        self.assertEqual(3, len(get_metrics_level(2)))
        self.assertEqual(4, len(get_metrics_level(3)))
        self.assertEqual(3, len(get_metrics_level(4)))
        self.assertNotEqual(get_metrics_level(2), get_metrics_level(4))

    def test_get_instance_fields(self):
        sqlExpected: str = "SELECT RefactoringCommit.id, RefactoringCommit.className, CommitMetaData.commitId FROM RefactoringCommit INNER JOIN CommitMetaData ON RefactoringCommit.commitMetaData_id = CommitMetaData.id"
        sqlBuilt: str = get_instance_fields("RefactoringCommit",
                                            [("RefactoringCommit", ["id", "className"]), ("CommitMetaData", ["commitId"])])
        self.assertEqual(sqlExpected, sqlBuilt)

        sqlExpected += " WHERE CommitMetaData.parentCommitId != null"
        sqlBuilt: str = get_instance_fields("RefactoringCommit",
                                            [("RefactoringCommit", ["id", "className"]),
                                             ("CommitMetaData", ["commitId"])],
                                            "CommitMetaData.parentCommitId != null")
        self.assertEqual(sqlExpected, sqlBuilt)

        sqlExpected += " AND RefactoringCommit.project_id in (select id from project where datasetName = \"github\")"
        sqlBuilt: str = get_instance_fields("RefactoringCommit",
                                            [("RefactoringCommit", ["id", "className"]),
                                             ("CommitMetaData", ["commitId"])],
                                            "CommitMetaData.parentCommitId != null",
                                            "github")
        self.assertEqual(sqlExpected, sqlBuilt)

        sqlExpected += " order by CommitMetaData.commitDate"
        sqlBuilt: str = get_instance_fields("RefactoringCommit",
                                            [("RefactoringCommit", ["id", "className"]),
                                             ("CommitMetaData", ["commitId"])],
                                            "CommitMetaData.parentCommitId != null",
                                            "github",
                                            "order by CommitMetaData.commitDate")
        self.assertEqual(sqlExpected, sqlBuilt)

    def test_get_refactoring_levels(self):
        sqlExpected: str = "SELECT refactoring, count(*) total from RefactoringCommit where " \
                           "RefactoringCommit.project_id in (select id from project where datasetName = \"github\") AND RefactoringCommit.isValid = TRUE " \
                           "group by refactoring order by count(*) desc"
        sqlBuilt: str = get_refactoring_levels("github")
        self.assertEqual(sqlExpected, sqlBuilt)

    def test_get_level_refactorings(self):
        sqlExpected: str = "SELECT CONCAT_WS('.', 'RefactoringCommit', RefactoringCommit.id) AS db_id, ClassMetric.classAnonymousClassesQty, ClassMetric.classAssignmentsQty, ClassMetric.classCbo, ClassMetric.classComparisonsQty, ClassMetric.classLambdasQty, ClassMetric.classLcom, ClassMetric.classLoc, ClassMetric.classLoopQty, ClassMetric.classMathOperationsQty, ClassMetric.classMaxNestedBlocks, ClassMetric.classNosi, ClassMetric.classNumberOfAbstractMethods, ClassMetric.classNumberOfDefaultFields, ClassMetric.classNumberOfDefaultMethods, ClassMetric.classNumberOfFields, ClassMetric.classNumberOfFinalFields, ClassMetric.classNumberOfFinalMethods, ClassMetric.classNumberOfMethods, ClassMetric.classNumberOfPrivateFields, ClassMetric.classNumberOfPrivateMethods, ClassMetric.classNumberOfProtectedFields, ClassMetric.classNumberOfProtectedMethods, ClassMetric.classNumberOfPublicFields, ClassMetric.classNumberOfPublicMethods, ClassMetric.classNumberOfStaticFields, ClassMetric.classNumberOfStaticMethods, ClassMetric.classNumberOfSynchronizedFields, ClassMetric.classNumberOfSynchronizedMethods, ClassMetric.classNumbersQty, ClassMetric.classParenthesizedExpsQty, ClassMetric.classReturnQty, ClassMetric.classRfc, ClassMetric.classStringLiteralsQty, ClassMetric.classSubClassesQty, ClassMetric.classTryCatchQty, ClassMetric.classUniqueWordsQty, ClassMetric.classVariablesQty, ClassMetric.classWmc, ClassMetric.isInnerClass, ProcessMetrics.authorOwnership, ProcessMetrics.bugFixCount, ProcessMetrics.qtyMajorAuthors, ProcessMetrics.qtyMinorAuthors, ProcessMetrics.qtyOfAuthors, ProcessMetrics.qtyOfCommits, ProcessMetrics.refactoringsInvolved FROM RefactoringCommit INNER JOIN CommitMetaData ON RefactoringCommit.commitMetaData_id = CommitMetaData.id INNER JOIN ClassMetric ON RefactoringCommit.classMetrics_id = ClassMetric.id INNER JOIN ProcessMetrics ON RefactoringCommit.processMetrics_id = ProcessMetrics.id WHERE RefactoringCommit.level = 1 AND RefactoringCommit.isValid = TRUE AND RefactoringCommit.refactoring = \"Change Parameter Type\" AND RefactoringCommit.project_id in (select id from project where datasetName = \"github\") order by CommitMetaData.commitDate"
        sqlBuilt: str = get_level_refactorings(
            1, "Change Parameter Type", "github")
        self.assertEqual(sqlExpected, sqlBuilt)

    def test_get_all_level_refactorings(self):
        sqlExpected: str = "SELECT CONCAT_WS('.', 'RefactoringCommit', RefactoringCommit.id) AS db_id, ClassMetric.classAnonymousClassesQty, ClassMetric.classAssignmentsQty, ClassMetric.classCbo, ClassMetric.classComparisonsQty, ClassMetric.classLambdasQty, ClassMetric.classLcom, ClassMetric.classLoc, ClassMetric.classLoopQty, ClassMetric.classMathOperationsQty, ClassMetric.classMaxNestedBlocks, ClassMetric.classNosi, ClassMetric.classNumberOfAbstractMethods, ClassMetric.classNumberOfDefaultFields, ClassMetric.classNumberOfDefaultMethods, ClassMetric.classNumberOfFields, ClassMetric.classNumberOfFinalFields, ClassMetric.classNumberOfFinalMethods, ClassMetric.classNumberOfMethods, ClassMetric.classNumberOfPrivateFields, ClassMetric.classNumberOfPrivateMethods, ClassMetric.classNumberOfProtectedFields, ClassMetric.classNumberOfProtectedMethods, ClassMetric.classNumberOfPublicFields, ClassMetric.classNumberOfPublicMethods, ClassMetric.classNumberOfStaticFields, ClassMetric.classNumberOfStaticMethods, ClassMetric.classNumberOfSynchronizedFields, ClassMetric.classNumberOfSynchronizedMethods, ClassMetric.classNumbersQty, ClassMetric.classParenthesizedExpsQty, ClassMetric.classReturnQty, ClassMetric.classRfc, ClassMetric.classStringLiteralsQty, ClassMetric.classSubClassesQty, ClassMetric.classTryCatchQty, ClassMetric.classUniqueWordsQty, ClassMetric.classVariablesQty, ClassMetric.classWmc, ClassMetric.isInnerClass, ProcessMetrics.authorOwnership, ProcessMetrics.bugFixCount, ProcessMetrics.qtyMajorAuthors, ProcessMetrics.qtyMinorAuthors, ProcessMetrics.qtyOfAuthors, ProcessMetrics.qtyOfCommits, ProcessMetrics.refactoringsInvolved FROM RefactoringCommit INNER JOIN CommitMetaData ON RefactoringCommit.commitMetaData_id = CommitMetaData.id INNER JOIN ClassMetric ON RefactoringCommit.classMetrics_id = ClassMetric.id INNER JOIN ProcessMetrics ON RefactoringCommit.processMetrics_id = ProcessMetrics.id WHERE RefactoringCommit.level = 1 AND RefactoringCommit.isValid = TRUE AND RefactoringCommit.project_id in (select id from project where datasetName = \"github\") order by CommitMetaData.commitDate"
        sqlBuilt: str = get_all_level_refactorings(1, "github")
        self.assertEqual(sqlExpected, sqlBuilt)

    def test_get_all_level_stable(self):
        sqlExpected: str = "SELECT CONCAT_WS('.', 'StableCommit', StableCommit.id) AS db_id, ClassMetric.classAnonymousClassesQty, ClassMetric.classAssignmentsQty, ClassMetric.classCbo, ClassMetric.classComparisonsQty, ClassMetric.classLambdasQty, ClassMetric.classLcom, ClassMetric.classLoc, ClassMetric.classLoopQty, ClassMetric.classMathOperationsQty, ClassMetric.classMaxNestedBlocks, ClassMetric.classNosi, ClassMetric.classNumberOfAbstractMethods, ClassMetric.classNumberOfDefaultFields, ClassMetric.classNumberOfDefaultMethods, ClassMetric.classNumberOfFields, ClassMetric.classNumberOfFinalFields, ClassMetric.classNumberOfFinalMethods, ClassMetric.classNumberOfMethods, ClassMetric.classNumberOfPrivateFields, ClassMetric.classNumberOfPrivateMethods, ClassMetric.classNumberOfProtectedFields, ClassMetric.classNumberOfProtectedMethods, ClassMetric.classNumberOfPublicFields, ClassMetric.classNumberOfPublicMethods, ClassMetric.classNumberOfStaticFields, ClassMetric.classNumberOfStaticMethods, ClassMetric.classNumberOfSynchronizedFields, ClassMetric.classNumberOfSynchronizedMethods, ClassMetric.classNumbersQty, ClassMetric.classParenthesizedExpsQty, ClassMetric.classReturnQty, ClassMetric.classRfc, ClassMetric.classStringLiteralsQty, ClassMetric.classSubClassesQty, ClassMetric.classTryCatchQty, ClassMetric.classUniqueWordsQty, ClassMetric.classVariablesQty, ClassMetric.classWmc, ClassMetric.isInnerClass, ProcessMetrics.authorOwnership, ProcessMetrics.bugFixCount, ProcessMetrics.qtyMajorAuthors, ProcessMetrics.qtyMinorAuthors, ProcessMetrics.qtyOfAuthors, ProcessMetrics.qtyOfCommits, ProcessMetrics.refactoringsInvolved FROM StableCommit INNER JOIN CommitMetaData ON StableCommit.commitMetaData_id = CommitMetaData.id INNER JOIN ClassMetric ON StableCommit.classMetrics_id = ClassMetric.id INNER JOIN ProcessMetrics ON StableCommit.processMetrics_id = ProcessMetrics.id WHERE StableCommit.level = 1 AND StableCommit.project_id in (select id from project where datasetName = \"github\") order by CommitMetaData.commitDate"
        sqlBuilt: str = get_all_level_stable(1, "github")
        self.assertEqual(sqlExpected, sqlBuilt)

    def test_get_level_refactorings_count(self):
        sqlExpected: str = "SELECT refactoring, count(*) FROM (SELECT RefactoringCommit.refactoring FROM RefactoringCommit WHERE RefactoringCommit.level = 2 AND RefactoringCommit.project_id in (select id from project where datasetName = \"github\") AND RefactoringCommit.isValid = TRUE) t group by refactoring order by count(*) desc"
        sqlBuilt: str = get_level_refactorings_count(2, "github")
        self.assertEqual(sqlExpected, sqlBuilt)

    def test_get_refactoring_types(self):
        sqlExpected: str = "SELECT DISTINCT refactoring FROM (SELECT RefactoringCommit.refactoring FROM RefactoringCommit WHERE RefactoringCommit.project_id in (select id from project where datasetName = \"github\")) t"
        sqlBuilt: str = get_refactoring_types("github")
        self.assertEqual(sqlExpected, sqlBuilt)


if __name__ == '__main__':
    unittest.main()
