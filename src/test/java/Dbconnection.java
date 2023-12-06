
import com.clickhouse.jdbc.ClickHouseConnection;
import com.clickhouse.jdbc.ClickHouseDataSource;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public class Dbconnection {
    public static void main(String[] args) throws SQLException {
        String connString = "jdbc:ch://CLICKHOUSE_HTTPS_HOST:CLICKHOUSE_HTTPS_PORT?ssl=true&sslmode=STRICT";
        ClickHouseDataSource database = new ClickHouseDataSource(connString);
        ClickHouseConnection connection = database.getConnection("CLICKHOUSE_USER", "CLICKHOUSE_PASSWORD");
        Statement statement = connection.createStatement();
        ResultSet result_set = statement.executeQuery("SELECT 1 AS one");
        while (result_set.next()) {
            System.out.println(result_set.getInt("one"));
        }
    }
}
