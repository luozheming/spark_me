package com.clickhouse;


import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan(basePackages = {"com.clickhouse.mapper"})
public class StartClickHouse {
    public static void main(String[] args) {
        SpringApplication.run(StartClickHouse.class);
    }
}
