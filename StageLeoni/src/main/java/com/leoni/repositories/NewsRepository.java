package com.leoni.repositories;

import com.leoni.models.News;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface NewsRepository extends MongoRepository<News, String> {
    
    /**
     * Find published news by target location and department
     */
    @Query("{'visibility.status': 'published', 'targetLocation': ?0, 'targetDepartment': ?1}")
    List<News> findPublishedNewsByLocationAndDepartment(String targetLocation, String targetDepartment);
    
    /**
     * Find all published news (for superadmin)
     */
    @Query("{'visibility.status': 'published'}")
    List<News> findAllPublishedNews();
    
    /**
     * Find news by author (admin)
     */
    List<News> findByAuthorRef(String authorRef);
    
    /**
     * Find news by category
     */
    List<News> findByCategory(String category);
    
    /**
     * Find news by priority
     */
    List<News> findByPriority(String priority);
    
    /**
     * Find news by visibility status
     */
    @Query("{'visibility.status': ?0}")
    List<News> findByVisibilityStatus(String status);
    
    /**
     * Find recent published news ordered by published date
     */
    @Query("{'visibility.status': 'published'}")
    List<News> findPublishedNewsOrderByPublishedAtDesc();
    
    /**
     * Find news created between dates
     */
    List<News> findByCreatedAtBetween(LocalDateTime startDate, LocalDateTime endDate);
    
    /**
     * Count published news by location and department
     */
    @Query(value = "{'visibility.status': 'published', 'targetLocation': ?0, 'targetDepartment': ?1}", count = true)
    long countPublishedNewsByLocationAndDepartment(String targetLocation, String targetDepartment);
    
    // ===== METHODS FOR LEGACY DATA STRUCTURE (using isActive) =====
    
    /**
     * Find active news by target location and department (legacy structure)
     */
    @Query("{'isActive': true, 'targetLocation': ?0, 'targetDepartment': ?1}")
    List<News> findActiveNewsByLocationAndDepartment(String targetLocation, String targetDepartment);
    
    /**
     * Find all active news (legacy structure)
     */
    @Query("{'isActive': true}")
    List<News> findAllActiveNews();
}
