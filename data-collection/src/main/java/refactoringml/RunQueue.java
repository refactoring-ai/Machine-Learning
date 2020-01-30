package refactoringml;

import com.google.common.io.Files;
import com.rabbitmq.client.*;
import org.apache.commons.io.FileUtils;
import org.apache.log4j.Logger;
import refactoringml.db.Database;
import refactoringml.db.HibernateConfig;

import java.io.File;
import java.io.IOException;
import java.util.List;
import java.util.concurrent.TimeoutException;

import static refactoringml.util.FilePathUtils.lastSlashDir;

public class RunQueue {

	private static final Logger log = Logger.getLogger(RunQueue.class);
	public final static String QUEUE_NAME = "refactoring";
	private final Database db;
	private String storagePath;
	private String host;
	private final int threshold;
	private final boolean testFilesOnly;
	private final boolean storeFullSourceCode;

	public RunQueue(String host, String url, String user, String pwd, String storagePath, int threshold, boolean testFilesOnly, boolean storeFullSourceCode) {
		this.host = host;
		this.storagePath = storagePath;
		this.threshold = threshold;
		this.testFilesOnly = testFilesOnly;
		this.storeFullSourceCode = storeFullSourceCode;
		db = new Database(new HibernateConfig().getSessionFactory(url, user, pwd));
	}

	public static void main(String[] args) throws Exception {

		// we gotta wait 3 minutes before the queue is up and the db is up...
		// Docker stuf...
		Thread.sleep(1000 * 60 * 3);


		String queueHost = "localhost";
		String url = "jdbc:mysql://localhost:3306/refactoringtest?useSSL=false&useLegacyDatetimeCode=false&serverTimezone=UTC";
		String user = "root";
		String pwd = "";
		int threshold = 50;
		boolean bTestFilesOnly = false;
		boolean storeFullSourceCode = true;
		String storagePath = "/Users/mauricioaniche/Desktop/results/";

		boolean test = true;
		if(!test) {
			queueHost = System.getenv("QUEUE_HOST");
			url = System.getenv("REF_URL");
			user = System.getenv("REF_USER");
			pwd = System.getenv("REF_DBPWD");
			threshold = Integer.parseInt(System.getenv("THRESHOLD"));
			bTestFilesOnly = Boolean.parseBoolean(System.getenv("TEST_ONLY"));
			storeFullSourceCode = Boolean.parseBoolean(System.getenv("STORE_FILES"));
			storagePath = System.getenv("STORAGE_PATH");
		}

		new RunQueue(queueHost, url, user, pwd, storagePath, threshold, bTestFilesOnly, storeFullSourceCode).run();

	}

	private void run() throws IOException, TimeoutException {
		ConnectionFactory factory = new ConnectionFactory();
		factory.setHost(host);

		while(true) {
			log.info("Waiting for the queue!");
			try (Connection connection = factory.newConnection();
			     Channel channel = connection.createChannel()) {

				GetResponse chResponse = channel.basicGet(QUEUE_NAME, true);
				if (chResponse != null) {
					byte[] body = chResponse.getBody();
					String message = new String(body);

					log.info("Got from queue: " + message);

					doWork(message);
				}
			}
		}
	}

	private void doWork(String message) {

		String[] msg = message.split(",");

		String dataset = msg[2];
		String gitUrl = msg[1];

		log.info("Dataset: " + dataset + ", Git URL: " + gitUrl);

		// do not run if the project is already in the database
		if (db.projectExists(gitUrl)) {
			System.out.println(String.format("Project %s already in the database", gitUrl));
		} else {
			try {
				new App(dataset, gitUrl, storagePath, threshold, db, testFilesOnly, storeFullSourceCode).run();
			} catch(Exception e) {
				log.error("Error while processing " + gitUrl, e);
			}
		}
	}


}
