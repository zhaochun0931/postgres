import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.sql.SQLException;

public class PostgresClient {

    // JDBC URL, username, and password of PostgreSQL server
    private static final String URL = "jdbc:postgresql://localhost:5432/your_database";  // Replace with your database URL
    private static final String USER = "your_username";  // Replace with your username
    private static final String PASSWORD = "your_password";  // Replace with your password

    public static void main(String[] args) {
        
        // Connection object
        Connection connection = null;
        Statement statement = null;
        ResultSet resultSet = null;

        try {
            // Establish connection to the PostgreSQL server
            connection = DriverManager.getConnection(URL, USER, PASSWORD);
            System.out.println("Connected to PostgreSQL server successfully.");

            // Create a Statement object
            statement = connection.createStatement();

            // Query to retrieve PostgreSQL version
            String sql = "SELECT version();";

            // Execute the query and get the result
            resultSet = statement.executeQuery(sql);

            // Retrieve and print the version
            if (resultSet.next()) {
                String version = resultSet.getString(1);  // First column is the version info
                System.out.println("PostgreSQL version: " + version);
            }

        } catch (SQLException e) {
            e.printStackTrace();
        } finally {
            // Close resources to prevent memory leaks
            try {
                if (resultSet != null) {
                    resultSet.close();
                }
                if (statement != null) {
                    statement.close();
                }
                if (connection != null) {
                    connection.close();
                }
            } catch (SQLException ex) {
                ex.printStackTrace();
            }
        }
    }
}
