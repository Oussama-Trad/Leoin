package com.leoni.controllers;

import com.leoni.dto.UserDTO;
import com.leoni.exceptions.DuplicateUserException;
import com.leoni.exceptions.UserNotFoundException;
import com.leoni.services.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/users")
@CrossOrigin(origins = "*")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    /**
     * Get all users
     * @return List of all users
     */
    @GetMapping
    public ResponseEntity<List<UserDTO>> getAllUsers() {
        try {
            List<UserDTO> users = userService.getAllUsers();
            return ResponseEntity.ok(users);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Get user by ID
     * @param id the user ID
     * @return UserDTO
     */
    @GetMapping("/{id}")
    public ResponseEntity<UserDTO> getUserById(@PathVariable String id) {
        try {
            UserDTO user = userService.getUserById(id);
            return ResponseEntity.ok(user);
        } catch (UserNotFoundException e) {
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Get user by primary email (adresse1)
     * @param adresse1 the primary email address
     * @return UserDTO
     */
    @GetMapping("/adresse1/{adresse1}")
    public ResponseEntity<UserDTO> getUserByAdresse1(@PathVariable String adresse1) {
        try {
            UserDTO user = userService.getUserByAdresse1(adresse1);
            return ResponseEntity.ok(user);
        } catch (UserNotFoundException e) {
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Get user by employee ID
     * @param employeeId the employee ID
     * @return UserDTO
     */
    @GetMapping("/employee/{employeeId}")
    public ResponseEntity<UserDTO> getUserByEmployeeId(@PathVariable String employeeId) {
        try {
            UserDTO user = userService.getUserByEmployeeId(employeeId);
            return ResponseEntity.ok(user);
        } catch (UserNotFoundException e) {
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Create a new user
     * @param userDTO the user data
     * @return created UserDTO
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> createUser(@RequestBody UserDTO userDTO) {
        Map<String, Object> response = new HashMap<>();
        
        try {
            UserDTO createdUser = userService.createUser(userDTO);
            response.put("success", true);
            response.put("message", "Utilisateur créé avec succès");
            response.put("user", createdUser);
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (DuplicateUserException e) {
            response.put("success", false);
            response.put("message", e.getMessage());
            response.put("errorCode", e.getErrorCode());
            return ResponseEntity.status(HttpStatus.CONFLICT).body(response);
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "Erreur lors de la création de l'utilisateur: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }
    
    /**
     * Update an existing user
     * @param id the user ID
     * @param userDTO the updated user data
     * @return updated UserDTO
     */
    @PutMapping("/{id}")
    public ResponseEntity<Map<String, Object>> updateUser(@PathVariable String id, @RequestBody UserDTO userDTO) {
        Map<String, Object> response = new HashMap<>();
        
        try {
            UserDTO updatedUser = userService.updateUser(id, userDTO);
            response.put("success", true);
            response.put("message", "Utilisateur mis à jour avec succès");
            response.put("user", updatedUser);
            return ResponseEntity.ok(response);
        } catch (UserNotFoundException e) {
            response.put("success", false);
            response.put("message", e.getMessage());
            response.put("errorCode", e.getErrorCode());
            return ResponseEntity.notFound().build();
        } catch (DuplicateUserException e) {
            response.put("success", false);
            response.put("message", e.getMessage());
            response.put("errorCode", e.getErrorCode());
            return ResponseEntity.status(HttpStatus.CONFLICT).body(response);
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "Erreur lors de la mise à jour de l'utilisateur: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }
    
    /**
     * Delete a user
     * @param id the user ID
     * @return deletion result
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> deleteUser(@PathVariable String id) {
        Map<String, Object> response = new HashMap<>();
        
        try {
            userService.deleteUser(id);
            response.put("success", true);
            response.put("message", "Utilisateur supprimé avec succès");
            return ResponseEntity.ok(response);
        } catch (UserNotFoundException e) {
            response.put("success", false);
            response.put("message", e.getMessage());
            response.put("errorCode", e.getErrorCode());
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "Erreur lors de la suppression de l'utilisateur: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }
    
    /**
     * Search users by name
     * @param searchTerm the search term
     * @return List of matching users
     */
    @GetMapping("/search")
    public ResponseEntity<List<UserDTO>> searchUsers(@RequestParam String searchTerm) {
        try {
            List<UserDTO> users = userService.searchUsersByName(searchTerm);
            return ResponseEntity.ok(users);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Get users by department ID
     * @param departmentId the department ID
     * @return List of users in the department
     */
    @GetMapping("/department/{departmentId}")
    public ResponseEntity<List<UserDTO>> getUsersByDepartmentId(@PathVariable String departmentId) {
        try {
            List<UserDTO> users = userService.getUsersByDepartmentId(departmentId);
            return ResponseEntity.ok(users);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Get users by position
     * @param position the position name
     * @return List of users with the position
     */
    @GetMapping("/position/{position}")
    public ResponseEntity<List<UserDTO>> getUsersByPosition(@PathVariable String position) {
        try {
            List<UserDTO> users = userService.getUsersByPosition(position);
            return ResponseEntity.ok(users);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Get users filtered by admin's department hierarchy level
     * If admin is assigned to company level, they see all users
     * If admin is assigned to location level, they see users from all departments in that location
     * If admin is assigned to department level, they see only users from that department
     * @param adminDepartmentId the admin's department ID
     * @return List of users accessible to the admin
     */
    @GetMapping("/filtered/{adminDepartmentId}")
    public ResponseEntity<List<UserDTO>> getFilteredUsers(@PathVariable String adminDepartmentId) {
        try {
            List<UserDTO> users = userService.getFilteredUsersByAdminDepartment(adminDepartmentId);
            return ResponseEntity.ok(users);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Health check endpoint
     * @return service status
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> healthCheck() {
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "Service utilisateurs opérationnel");
        response.put("timestamp", System.currentTimeMillis());
        return ResponseEntity.ok(response);
    }
    
    /**
     * Get all distinct locations
     * @return List of locations
     */
    @GetMapping("/locations")
    public ResponseEntity<List<String>> getAllLocations() {
        try {
            List<String> locations = userService.getAllLocations();
            return ResponseEntity.ok(locations);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Get all distinct departments
     * @return List of departments
     */
    @GetMapping("/departments")
    public ResponseEntity<List<String>> getAllDepartments() {
        try {
            List<String> departments = userService.getAllDepartments();
            return ResponseEntity.ok(departments);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}