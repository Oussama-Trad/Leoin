package com.leoni.repositories;

import com.leoni.models.DocumentType;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface DocumentTypeRepository extends MongoRepository<DocumentType, String> {
    List<DocumentType> findByActiveTrue();
    boolean existsByNameIgnoreCase(String name);
    DocumentType findByNameIgnoreCase(String name);
}
