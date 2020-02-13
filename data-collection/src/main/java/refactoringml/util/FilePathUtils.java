package refactoringml.util;

import java.io.File;

public class FilePathUtils {
	public static String classFromFileName (String fileName) {
		String[] splittedFile = enforceUnixPaths(fileName).split("/");
		return splittedFile[splittedFile.length-1].replace(".java", "");
	}

	public static String classFromFullName (String refactoredClass) {
		String[] split = refactoredClass.split("\\.");
		return split[split.length-1];
	}

	public static String dirsOnly (String fileName) {
		return new File(fileName).getParent();
	}

	public static String fileNameOnly (String fileName) {
		return new File(fileName).getName();
	}

	public static boolean createAllDirs (String base, String fileName) {
		return new File(lastSlashDir(base) + dirsOnly(fileName)).mkdirs();
	}

	public static String lastSlashDir (String path) {
		//TODO: causes problems on Windows machines: C:\Users\test is made to C:\Users\test/
		// Solution: enforce unix-style paths are only unix OSs
		return path + (path.endsWith("/")?"":"/");
	}

	/*
		Enforce uniform path formatting for cross-platform support.
		On Windows jgit.Diffentry.getPath() and ck.getFile use different file separator e.g.
		yes.filePath: ...\Temp\1581608730366-0/ and diffEntry.filePath: .../Temp/1581608730366-0/
	 */
	public static String enforceUnixPaths(String filePath){ return filePath.replace(File.separator, "/"); }
}