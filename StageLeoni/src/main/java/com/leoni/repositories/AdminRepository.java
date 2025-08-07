package com.leoni.repositories;

import com.leoni.models.Admin;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface AdminRepository extends MongoRepository<Admin, String> {
    
    Optional<Admin> findByUsername(String username);
    
    Optional<Admin> findByUsernameAndActiveTrue(String username);
    
    List<Admin> findByActiveTrue();
    
    List<Admin> findByDepartmentId(String departmentId);
    
    List<Admin> findByDepartmentIdAndActiveTrue(String departmentId);
    
    boolean existsByUsername(String username);
    
    @Query("{'username': ?0, 'active': true}")
    Optional<Admin> findActiveAdminByUsername(String username);
}
