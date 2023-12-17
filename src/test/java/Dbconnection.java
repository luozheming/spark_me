


import com.clickhouse.StartClickHouse;
import com.clickhouse.config.ClickHouseConfig;
import org.junit.jupiter.api.Test;
import org.junit.runner.RunWith;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit4.SpringRunner;

import java.util.List;
import java.util.Map;
@RunWith(SpringRunner.class)
@SpringBootTest(classes = StartClickHouse.class)
public class Dbconnection {
    @Test
    public void select_Test() {
        String sql="select cluster,shard_num from clusters where  cluster like '%test%'";
        List<Map<String,String>> result= ClickHouseConfig.exeSql(sql);

        System.out.println(result);
    }


}
