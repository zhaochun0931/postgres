import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public class PostgresClient {
    
    // JDBC URL, username, and password of MySQL server
    private static final String URL = "jdbc:postgresql://localhost:5432/your_database";  // Replace with your database URL
    private static final String USER = "your_username";  // Replace with your username
    private static final String PASSWORD = "your_password";  // Replace with your password
    
    // SQL query to insert data
    private static final String INSERT_SQL = "INSERT INTO employees (name, age) VALUES (?, ?)";

    public static void main(String[] args) {
        
        // Connection and statement objects
        Connection connection = null;
        PreparedStatement preparedStatement = null;
        
        try {
            // Establish the connection to the database
            connection = DriverManager.getConnection(URL, USER, PASSWORD);
            System.out.println("Connected to the PostgreSQL server successfully.");

            // Prepare SQL statement
            preparedStatement = connection.prepareStatement(INSERT_SQL);
            
            // Insert multiple rows
            for (int i = 1; i <= 5; i++) {
                String name = "Employee" + i;
                int age = 30 + i;
                
                // Set values for prepared statement
                preparedStatement.setString(1, name);
                preparedStatement.setInt(2, age);
                
                // Execute the insert statement
                preparedStatement.executeUpdate();
                System.out.println("Inserted: " + name + " with age " + age);
            }
            
        } catch (SQLException e) {
            e.printStackTrace();
        } finally {
            // Close resources to prevent memory leaks
            try {
                if (preparedStatement != null) {
                    preparedStatement.close();
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
