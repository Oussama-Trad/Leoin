package com.leoni.repositories;

import com.leoni.models.Department;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface DepartmentRepository extends MongoRepository<Department, String> {
    
    /**
     * Find departments by location
     * @param location the location
     * @return List of departments at the specified location
     */
    List<Department> findByLocation(String location);
    
    /**
     * Check if department exists by name and location
     * @param name department name
     * @param location department location
     * @return true if exists
     */
    boolean existsByNameAndLocation(String name, String location);
    
    /**
     * Find unique locations
     * @return List of unique locations
     */
    @Query(value = "{}", fields = "{ 'location' : 1 }")
    List<Department> findAllLocations();
}
