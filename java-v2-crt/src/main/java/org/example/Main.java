package org.example;

import software.amazon.awssdk.core.client.config.ClientOverrideConfiguration;
import software.amazon.awssdk.core.retry.RetryPolicy;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbAsyncTable;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbEnhancedAsyncClient;
import software.amazon.awssdk.enhanced.dynamodb.Key;
import software.amazon.awssdk.enhanced.dynamodb.TableSchema;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbAttribute;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbBean;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbPartitionKey;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbSortKey;
import software.amazon.awssdk.http.crt.AwsCrtAsyncHttpClient;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.dynamodb.DynamoDbAsyncClient;
import software.amazon.awssdk.metrics.MetricPublisher;
import software.amazon.awssdk.metrics.publishers.cloudwatch.CloudWatchMetricPublisher;
import software.amazon.awssdk.services.cloudwatch.CloudWatchAsyncClient;

import java.time.Duration;
import java.time.Instant;
import java.time.format.DateTimeFormatter;

import software.amazon.awssdk.core.retry.backoff.BackoffStrategy;
import software.amazon.awssdk.core.retry.backoff.FullJitterBackoffStrategy;

public class Main {

    private static final Integer DEFAULT_APICALLTIMEOUT_DURATION = 1000;
    private static final Integer DEFAULT_APICALLATTEMPTTIMEOUT_DURATION = 250;
    private static final Integer RETRY_NUMRETRIES = 3;
    private static final Integer BACKOFF_MAXBACKOFFTIME = 30;
    private static final Integer DEFAULT_BACKOFF = 10;
    private static final Integer DEFAULT_DURATION = 60000;

    private static final String TABLE_NAME = System.getenv().getOrDefault("DYNAMODB_TABLE",
            "ecs-javav2-crt-cmk");
    private static final long INTERVAL_MS = Long
            .parseLong(System.getenv().getOrDefault("DURATION", DEFAULT_DURATION.toString()));
    private static final long APICALLTIMEOUT_DURATION = Long.parseLong(System.getenv()
            .getOrDefault("CALL_TIMEOUT", DEFAULT_APICALLTIMEOUT_DURATION.toString()));
    private static final long APICALLATTEMPTTIMEOUT_DURATION = Long.parseLong(System.getenv()
            .getOrDefault("ATTEMPT_TIMEOUT", DEFAULT_APICALLATTEMPTTIMEOUT_DURATION.toString()));
    private static final String REGION_ENV_VAR = System.getenv().getOrDefault("AWS_REGION",
            "us-east-1");
    private static final Region REGION = Region.of(REGION_ENV_VAR);
    private static BackoffStrategy backoffStrategy = FullJitterBackoffStrategy.builder()
            .baseDelay(Duration.ofMillis(DEFAULT_BACKOFF))
            .maxBackoffTime(Duration.ofMillis(BACKOFF_MAXBACKOFFTIME)).build();

    private static MetricPublisher metricsPub = CloudWatchMetricPublisher.builder()
            .namespace("SDK-Test-" + TABLE_NAME).cloudWatchClient(CloudWatchAsyncClient.builder()
                    .httpClient(AwsCrtAsyncHttpClient.builder().build()).build())
            .build();

    private static DynamoDbEnhancedAsyncClient enhancedAsyncClient = DynamoDbEnhancedAsyncClient
            .builder()
            .dynamoDbClient(DynamoDbAsyncClient.builder()
                    .httpClient(AwsCrtAsyncHttpClient.builder()
                            .connectionMaxIdleTime(Duration.ofSeconds(900)).build())
                    .overrideConfiguration(ClientOverrideConfiguration.builder()
                            .apiCallTimeout(Duration.ofMillis(APICALLTIMEOUT_DURATION))
                            .addMetricPublisher(metricsPub)
                            .apiCallAttemptTimeout(
                                    Duration.ofMillis(APICALLATTEMPTTIMEOUT_DURATION))
                            .retryPolicy(RetryPolicy.builder().numRetries(RETRY_NUMRETRIES)
                                    .backoffStrategy(backoffStrategy).build())
                            .build())
                    .region(REGION).build())
            .build();

    private static DynamoDbAsyncTable<MyItem> myItemTable = enhancedAsyncClient.table(TABLE_NAME,
            TableSchema.fromBean(MyItem.class));

    public static void main(String[] args) {
        while (true) {
            try {
                getItem();
                Thread.sleep(INTERVAL_MS);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    public static void getItem() {
        int randomNumber = (int) Math.floor(Math.random() * 10000);
        Key key = Key.builder().partitionValue("p#000" + randomNumber)
                .sortValue("p#000" + randomNumber).build();
        Instant startTime = Instant.now();
        myItemTable.getItem(key).whenComplete((item, error) -> {
            Duration elapsedTime = Duration.between(startTime, Instant.now());
            long milliseconds = elapsedTime.toMillis();
            if (error != null) {
                String timestamp = DateTimeFormatter.ISO_INSTANT.format(Instant.now());
                System.err.println(timestamp + " - Error: " + error.getMessage());
            }
            System.out.println("Time taken (ms): " + milliseconds);
        });
    }

    @DynamoDbBean
    public static class MyItem {
        private String partitionKey;
        private String sortKey;
        private String testAttribute;

        @DynamoDbAttribute("pk")
        @DynamoDbPartitionKey
        public String getPartitionKey() {
            return partitionKey;
        }

        public void setPartitionKey(String partitionKey) {
            this.partitionKey = partitionKey;
        }

        @DynamoDbAttribute("sk")
        @DynamoDbSortKey
        public String getSortKey() {
            return sortKey;
        }

        public void setSortKey(String sortKey) {
            this.sortKey = sortKey;
        }

        @DynamoDbAttribute("attribute_0")
        public String getTestAttribute() {
            return this.testAttribute;
        }

        public void setTestAttribute(String testAttribute) {
            this.testAttribute = testAttribute;
        }

        @Override
        public String toString() {
            return "MyItem{" + "partitionKey='" + partitionKey + '\'' + ", attribute='"
                    + testAttribute + '\'' + '}';
        }
    }
}