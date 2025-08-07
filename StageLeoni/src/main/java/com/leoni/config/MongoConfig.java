package com.leoni.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.mongodb.config.AbstractMongoClientConfiguration;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.convert.DefaultMongoTypeMapper;
import org.springframework.data.mongodb.core.convert.MappingMongoConverter;
import org.springframework.data.mongodb.core.convert.MongoCustomConversions;
import org.springframework.data.mongodb.repository.config.EnableMongoRepositories;
import org.springframework.core.convert.converter.Converter;
import org.bson.types.Binary;

import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;

import java.util.Arrays;

@Configuration
@EnableMongoRepositories(basePackages = "com.leoni.repositories")
public class MongoConfig extends AbstractMongoClientConfiguration {
    
    @Value("${spring.data.mongodb.uri:mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp?retryWrites=true&w=majority}")
    private String mongoUri;
    
    @Value("${spring.data.mongodb.database:LeoniApp}")
    private String mongoDatabase;
    
    @Override
    protected String getDatabaseName() {
        return mongoDatabase;
    }
    
    @Override
    public MongoClient mongoClient() {
        return MongoClients.create(mongoUri);
    }
    
    /**
     * Custom converter for Binary to String conversion (read-only)
     * This allows existing binary data to be read as strings without converting new strings to binary
     */
    public static class BinaryToStringConverter implements Converter<Binary, String> {
        @Override
        public String convert(Binary binary) {
            if (binary == null) {
                return null;
            }
            return new String(binary.getData());
        }
    }
    
    @Bean
    public MongoCustomConversions customConversions() {
        return new MongoCustomConversions(Arrays.asList(
            new BinaryToStringConverter()
        ));
    }
    
    /**
     * Custom MongoTemplate configuration
     */
    @Bean
    public MongoTemplate mongoTemplate() throws Exception {
        MongoTemplate template = new MongoTemplate(mongoClient(), getDatabaseName());
        
        // Remove the _class field from documents
        MappingMongoConverter converter = (MappingMongoConverter) template.getConverter();
        converter.setTypeMapper(new DefaultMongoTypeMapper(null));
        
        // Set custom conversions for reading binary data
        converter.setCustomConversions(customConversions());
        converter.afterPropertiesSet();
        
        return template;
    }
    
    /**
     * Configure collection names and indexes if needed
     */
    @Bean
    public MongoTemplate customMongoTemplate() {
        try {
            MongoTemplate template = mongoTemplate();
            
            // Temporarily disable index creation to avoid startup issues
            // TODO: Re-enable after fixing index conflicts
            /*
            // Create indexes for better performance
            // Users collection indexes - adresse1 index (check if exists first)
            try {
                // Try to drop the existing unique index if it exists
                template.indexOps("users").dropIndex("adresse1_1");
            } catch (Exception e) {
                // Index doesn't exist, that's fine
            }
            
            // Create new non-unique adresse1 index
            template.indexOps("users").createIndex(
                new org.springframework.data.mongodb.core.index.Index()
                    .on("adresse1", org.springframework.data.domain.Sort.Direction.ASC)
                    .named("adresse1_non_unique")
                    // Removed .unique() to avoid duplicate null email issues
            );
            
            template.indexOps("users").createIndex(
                new org.springframework.data.mongodb.core.index.Index()
                    .on("employeeId", org.springframework.data.domain.Sort.Direction.ASC)
                    .unique()
            );
            
            // Document requests collection indexes
            template.indexOps("document_requests").createIndex(
                new org.springframework.data.mongodb.core.index.Index()
                    .on("userId", org.springframework.data.domain.Sort.Direction.ASC)
            );
            
            template.indexOps("document_requests").createIndex(
                new org.springframework.data.mongodb.core.index.Index()
                    .on("status.current", org.springframework.data.domain.Sort.Direction.ASC)
            );
            
            template.indexOps("document_requests").createIndex(
                new org.springframework.data.mongodb.core.index.Index()
                    .on("createdAt", org.springframework.data.domain.Sort.Direction.DESC)
            );
            */
            
            return template;
        } catch (Exception e) {
            throw new RuntimeException("Failed to configure MongoDB template", e);
        }
    }
}