package com.leoni.repositories;

import com.leoni.models.DocumentRequest;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.Date;
import java.util.List;

@Repository
public interface DocumentRequestRepository extends MongoRepository<DocumentRequest, String> {
    
    /**
     * Find all document requests for a specific user
     * @param userId the user ID
     * @return List of document requests for the user
     */
    List<DocumentRequest> findByUserId(String userId);
    
    /**
     * Find document requests by current status
     * @param status the status to search for
     * @return List of document requests with the specified status
     */
    @Query("{'status.current': ?0}")
    List<DocumentRequest> findByCurrentStatus(String status);
    
    /**
     * Find document requests containing a specific document type
     * @param documentType the document type to search for in the list
     * @return List of document requests containing the specified type
     */
    List<DocumentRequest> findByDocumentTypesContaining(String documentType);
    
    /**
     * Find document requests by user ID and status
     * @param userId the user ID
     * @param status the status
     * @return List of matching document requests
     */
    @Query("{'userId': ?0, 'status.current': ?1}")
    List<DocumentRequest> findByUserIdAndCurrentStatus(String userId, String status);
    
    /**
     * Find document requests created between two dates
     * @param startDate the start date
     * @param endDate the end date
     * @return List of document requests created in the date range
     */
    List<DocumentRequest> findByCreatedAtBetween(Date startDate, Date endDate);
    
    /**
     * Find document requests by user ID containing a specific document type
     * @param userId the user ID
     * @param documentType the document type to search for in the list
     * @return List of matching document requests
     */
    List<DocumentRequest> findByUserIdAndDocumentTypesContaining(String userId, String documentType);
    
    /**
     * Count document requests by status
     * @param status the status to count
     * @return Number of document requests with the specified status
     */
    @Query(value = "{'status.current': ?0}", count = true)
    long countByCurrentStatus(String status);
    
    /**
     * Count document requests for a specific user
     * @param userId the user ID
     * @return Number of document requests for the user
     */
    long countByUserId(String userId);
    
    /**
     * Find recent document requests (ordered by creation date descending)
     * @return List of document requests ordered by creation date
     */
    List<DocumentRequest> findAllByOrderByCreatedAtDesc();
    
    /**
     * Find document requests by user ID ordered by creation date descending
     * @param userId the user ID
     * @return List of document requests for the user ordered by creation date
     */
    List<DocumentRequest> findByUserIdOrderByCreatedAtDesc(String userId);
    
    /**
     * Search document requests by description (case insensitive)
     * @param searchTerm the term to search for in description
     * @return List of matching document requests
     */
    @Query("{'description': {$regex: ?0, $options: 'i'}}")
    List<DocumentRequest> searchByDescription(String searchTerm);
}