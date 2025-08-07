package com.leoni.repositories;

import com.leoni.models.User;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.List;

@Repository
public interface UserRepository extends MongoRepository<User, String> {
    
    /**
     * Find user by primary email address (email)
     * @param email the primary email to search for
     * @return Optional containing the user if found
     */
    Optional<User> findByEmail(String email);
    
    /**
     * Find user by primary email address (adresse1) - for backward compatibility
     * @param adresse1 the primary email to search for
     * @return Optional containing the user if found
     */
    @Query("{'email': ?0}")
    Optional<User> findByAdresse1(String adresse1);
    
    /**
     * Find user by employee ID
     * @param employeeId the employee ID to search for
     * @return Optional containing the user if found
     */
    Optional<User> findByEmployeeId(String employeeId);
    
    /**
     * Find users by department name
     * @param department the department name
     * @return List of users in the department
     */
    List<User> findByDepartment(String department);
    
    /**
     * Find users by department ID (using departmentRef)
     * @param departmentRef the department reference ID
     * @return List of users in the department
     */
    List<User> findByDepartmentRef(String departmentRef);
    
    /**
     * Find users by multiple department references
     * @param departmentRefs the list of department reference IDs
     * @return List of users in any of the departments
     */
    List<User> findByDepartmentRefIn(List<String> departmentRefs);
    
    /**
     * Find users by multiple department IDs (for backward compatibility)
     * @param departmentIds the list of department IDs
     * @return List of users in any of the departments
     */
    @Query("{'departmentRef': {'$in': ?0}}")
    List<User> findByDepartmentIdIn(List<String> departmentIds);
    
    /**
     * Find users by position
     * @param position the position name
     * @return List of users with the position
     */
    List<User> findByPosition(String position);
    
    /**
     * Check if primary email already exists
     * @param email the primary email to check
     * @return true if email exists, false otherwise
     */
    boolean existsByEmail(String email);
    
    /**
     * Check if primary email (adresse1) already exists - for backward compatibility
     * @param adresse1 the primary email to check
     * @return true if email exists, false otherwise
     */
    @Query(value = "{'email': ?0}", exists = true)
    boolean existsByAdresse1(String adresse1);
    
    /**
     * Check if employee ID already exists
     * @param employeeId the employee ID to check
     * @return true if employee ID exists, false otherwise
     */
    boolean existsByEmployeeId(String employeeId);
    
    /**
     * Find users by first name and last name (case insensitive)
     * @param firstName the first name
     * @param lastName the last name
     * @return List of matching users
     */
    @Query("{'firstName': {$regex: ?0, $options: 'i'}, 'lastName': {$regex: ?1, $options: 'i'}}")
    List<User> findByFirstNameAndLastNameIgnoreCase(String firstName, String lastName);
    
    /**
     * Search users by name (first or last name contains the search term)
     * @param searchTerm the term to search for
     * @return List of matching users
     */
    @Query("{'$or': [{'firstName': {$regex: ?0, $options: 'i'}}, {'lastName': {$regex: ?0, $options: 'i'}}]}")
    List<User> searchByName(String searchTerm);
    
    /**
     * Find users by status
     * @param status the status to search for
     * @return List of users with the specified status
     */
    List<User> findByStatus(String status);
    
    /**
     * Find users by department ID
     * @param departmentId the department ID to search for
     * @return List of users in the specified department
     */
    List<User> findByDepartmentId(String departmentId);
}