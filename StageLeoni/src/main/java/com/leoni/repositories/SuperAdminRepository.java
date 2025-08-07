package com.leoni.repositories;

import com.leoni.models.SuperAdmin;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface SuperAdminRepository extends MongoRepository<SuperAdmin, String> {
    
    /**
     * Find SuperAdmin by username
     */
    Optional<SuperAdmin> findByUsername(String username);
    
    /**
     * Find active SuperAdmin by username
     */
    Optional<SuperAdmin> findByUsernameAndActiveTrue(String username);
    
    /**
     * Find SuperAdmin by username and password (for authentication)
     */
    Optional<SuperAdmin> findByUsernameAndPassword(String username, String password);
    
    /**
     * Find all active SuperAdmins
     */
    List<SuperAdmin> findByActiveTrue();
    
    /**
     * Check if username exists
     */
    boolean existsByUsername(String username);
    
    /**
     * Find SuperAdmin by email
     */
    Optional<SuperAdmin> findByEmail(String email);
    
    /**
     * Find active SuperAdmin by username (query version)
     */
    @Query("{'username': ?0, 'active': true}")
    Optional<SuperAdmin> findActiveSuperAdminByUsername(String username);
}
