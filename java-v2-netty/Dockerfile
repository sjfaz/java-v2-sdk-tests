#
# Build stage
#
FROM maven:3.6.0-jdk-11-slim AS build
COPY src /app/src
COPY pom.xml /app/pom.xml
RUN mkdir /app/target
RUN mvn -f /app clean compile assembly:single

#
# Package stage
#
FROM openjdk:11-jre-slim
COPY --from=build /app/target/ddb-async-jar-with-dependencies.jar /usr/local/lib/demo.jar
ENTRYPOINT ["java","-jar","/usr/local/lib/demo.jar"]